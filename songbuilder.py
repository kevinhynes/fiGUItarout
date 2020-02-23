from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle, Ellipse, InstructionGroup, Bezier
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

import guitarpro
from typing import List

black = Color(0, 0, 0, 1)


class TabViewer(ScrollView):
    file = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.child_parity = 0
        self.prev_timesig = None
        self.prev_tab_widget = None
        self.prev_tabwidget = None
        super().__init__(**kwargs)
        self.gp_song = guitarpro.parse('./tgr-nm-01.gp5')
        self.flat_song = self.flatten_song()
        floatlayout_height = self.calc_floatlayout_height()
        self.floatlayout = FloatLayout(size_hint_y=None, height=floatlayout_height)
        tab_widget = TabWidget()
        self.child_y = floatlayout_height - tab_widget.height
        self.build_track(self.flat_song[0])

    def on_file(self, *args):
        self.gp_song = guitarpro.parse(self.file)

    def flatten_song(self):
        '''
        GuitarPro.models.Song structure summary
        Song:
            Tracks: List[Track]
                Track:
                    Measures: List[Measure]
                        Measure:
                            MeasureHeader
                            Voices: List[Voice]
                                Voice:
                                    Beats: List[Beat]
                                        Beat:
                                            Notes: List[Note]
                                                Note

        Tracks list represents each guitar (guitar1, guitar2, ...).
        Voicings list is of length 2, and represents left and right hand on piano.
            So far, 2nd Voicing is empty and can be ignored.

        Measures are grouped into repeat groups. This will make it more difficult to read later.
        Flatten each track of the song to be a 'linear' list of measures so we can iterate
        straight through it later.
        '''
        flat_song = []
        for gp_track in self.gp_song.tracks:
            flat_song += [self.flatten_track(gp_track)]
        return flat_song

    def flatten_track(self, gp_track):
        '''
        - PyGuitarPro does not appear to be parsing measure.header.repeatAlternative correctly.
        - When Beat is a quarter note, beat.duration.time == 960.  No idea why.
        '''
        flat_track = []
        repeat_group = []
        for gp_measure in gp_track.measures:
            # Add to existing open repeat group.
            if repeat_group != []:
                repeat_group += [gp_measure]
                # Close the repeat group.
                if gp_measure.repeatClose > 0:
                    repeat_group *= gp_measure.repeatClose
                    flat_track += repeat_group
                    repeat_group = []
            # Start a new repeat group.
            elif gp_measure.isRepeatOpen:
                repeat_group = [gp_measure]
            # Add normal measure.
            else:
                flat_track += [gp_measure]
        return flat_track

    def print_flattened_track(self, flat_track):
        for i, gp_measure in enumerate(flat_track):
            print(f'{i} {gp_measure.header.number + 1}')
            for gp_voice in gp_measure.voices[:-1]:
                for gp_beat in gp_voice.beats:
                    print(f'\t {gp_beat.notes}')

    def calc_floatlayout_height(self):
        height = 0
        spacing = 10
        tab_widget = TabWidget()
        for gp_measure in self.flat_song[0]:
            height += tab_widget.height + spacing
            if gp_measure.timeSignature.numerator / gp_measure.timeSignature.denominator.value > 1:
                height += tab_widget.height + spacing
        return (height + tab_widget.height)/ 2

    def build_track(self, flat_track):
        total_measures = len(flat_track)
        for i, gp_measure in enumerate(flat_track, 1):
            self.add_measure(gp_measure, i, total_measures)
        self.add_widget(self.floatlayout)

    def add_measure(self, gp_measure, idx, total_measures):
        if idx == 72:
            return
        timesig = (gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value)
        prev_tabwidget = self.prev_tabwidget
        prev_timesig = self.prev_timesig
        spacing = 10
        tabwidget = TabWidget(idx, total_measures)
        # Place first measure all the way at the top left.
        if prev_tabwidget is None:
            tabwidget.pos = (0, self.child_y)
        # Place the next measure on a new line below.
        elif (prev_tabwidget.measure_end > tabwidget.measure_start + tabwidget.tab_width
              or prev_timesig != timesig):
            self.child_y -= tabwidget.height + spacing
            tabwidget.pos = (0, self.child_y)
        # Place the next measure to the right of the last measure of the same time signature.
        else:
            tabwidget.measure_start = 0
            tabwidget.pos = (prev_tabwidget.measure_end, self.child_y)

        tabwidget.build_measure(gp_measure)
        tabwidget.width = tabwidget.measure_end - tabwidget.x
        if tabwidget.starts_with_tie:
            start = self.prev_tabwidget.xmids[-1]
            end = tabwidget.xmids[0]
            tabwidget.draw_tie_across_measures(tabwidget.gp_beats[0], start, end)
        self.prev_tabwidget = tabwidget
        self.prev_timesig = timesig
        self.floatlayout.add_widget(tabwidget)


class TabWidget(Widget):
    measure_end = NumericProperty(0)

    def __init__(self, idx=0, total_measures=0, **kwargs):
        self.idx = idx
        self.total_measures = total_measures
        self.step_y = 20
        self.measure_start = 64
        self.tab_width = 512
        self.measure_end = self.measure_start + self.tab_width
        # self.next_beat_idx = 0
        self.starts_with_tie = False
        self.ends_with_slide = False
        super().__init__(**kwargs)
        self.glyphs = InstructionGroup()
        self.backgrounds = InstructionGroup()
        self.note_glyphs = InstructionGroup()
        self.num_glyphs = InstructionGroup()
        self.tuplet_count = 0
        self.canvas.add(Color(1, 0, 0, 0.5))
        self.canvas.add(self.backgrounds)
        self.canvas.add(black)
        self.canvas.add(self.glyphs)

    def build_measure(self, gp_measure: guitarpro.models.Measure):
        self.gp_beats, self.xmids = self.add_staff_glyphs(gp_measure)
        self.draw_measure_number(gp_measure)
        self.draw_measure_count()
        if self.x == 0:
            self.draw_timesig(gp_measure)
        self.draw_note_effects(self.gp_beats, self.xmids)
        gp_beat_groups = self.gp_beat_groupby(self.gp_beats)
        self.add_note_glyphs(gp_beat_groups, self.xmids)

    def draw_measure_number(self, gp_measure: guitarpro.models.Measure):
        num = gp_measure.header.number
        num_glyph = CoreLabel(text=str(num), font_size=14, font_name='./fonts/Arial')
        num_glyph.refresh()
        num_x = self.x + self.measure_start - num_glyph.width
        num_y = self.y + self.step_y * 8
        num_instr = Rectangle(pos=(num_x, num_y), size=num_glyph.texture.size)
        num_instr.texture = num_glyph.texture
        self.glyphs.add(num_instr)

    def draw_measure_count(self):
        # TODO: Once copy/delete buttons are added, update measure counts.
        measure_count = str(self.idx) + ' / ' + str(self.total_measures)
        count_glyph = CoreLabel(text=measure_count, font_size=14, font_name='./fonts/Arial')
        count_glyph.refresh()
        count_x = self.measure_end - (count_glyph.width + 5)
        count_y = self.y
        count_instr = Rectangle(pos=(count_x, count_y), size=count_glyph.size)
        count_instr.texture = count_glyph.texture
        self.glyphs.add(count_instr)

    def draw_timesig(self, gp_measure: guitarpro.models.Measure):
        num, den = gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value
        num_glyph = CoreLabel(text=str(num), font_size=50, font_name='./fonts/PatuaOne-Regular')
        den_glyph = CoreLabel(text=str(den), font_size=50, font_name='./fonts/PatuaOne-Regular')
        num_glyph.refresh()
        den_glyph.refresh()
        num_x = self.x + (self.measure_start / 2) - (num_glyph.texture.width / 2)
        den_x = self.x + (self.measure_start / 2) - (den_glyph.texture.width / 2)
        num_instr = Rectangle(pos=(num_x, self.y + self.step_y * 5), size=(num_glyph.texture.size))
        den_instr = Rectangle(pos=(den_x, self.y + self.step_y * 3), size=(den_glyph.texture.size))
        num_instr.texture = num_glyph.texture
        den_instr.texture = den_glyph.texture
        self.glyphs.add(num_instr)
        self.glyphs.add(den_instr)

    def add_staff_glyphs(self, gp_measure: guitarpro.models.Measure):
        gp_beats, xmids = [], []
        for gp_voice in gp_measure.voices[:-1]:
            xpos = self.x + self.measure_start
            for beat_idx, gp_beat in enumerate(gp_voice.beats):
                note_dur = 1 / gp_beat.duration.value
                tuplet_mult = gp_beat.duration.tuplet.times / gp_beat.duration.tuplet.enters
                beat_width = note_dur * tuplet_mult * self.tab_width
                if gp_beat.duration.isDotted:
                    beat_width *= 3 / 2
                elif gp_beat.duration.isDoubleDotted:
                    beat_width *= 7 / 4
                beat_mid = self.add_beat_glyph(gp_beat, xpos)
                xmids += [beat_mid]
                gp_beats += [gp_beat]
                xpos += beat_width
                # if any(gp_note.type.name == "tie" for gp_note in gp_beat.notes):
                #     print(f'{gp_beat.voice.measure.header.number}  {int(0 < self.x)}\n')
                #     tied_notes = [gp_note for gp_note in gp_beat.notes if gp_note.type.name == "tie"]
                #     for gp_note in tied_notes:
                #         print(f'\ti: {beat_idx},  string: {gp_note.string}, fret: {gp_note.value}')
        self.next_beat_idx = beat_idx + 1
        self.measure_end = xpos
        return gp_beats, xmids

    def add_beat_glyph(self, gp_beat: guitarpro.models.Beat, xpos: float):
        # If notes list is empty, rest for gp_beat.duration.value.
        if not gp_beat.notes:
            self.draw_rest(gp_beat, xpos)
            return xpos, -1
        for gp_note in gp_beat.notes:
            xmid = self.draw_fretnum(gp_note, xpos)
        return xmid

    def draw_fretnum(self, gp_note: guitarpro.models.Note, xpos: float):
        fret_text = str(gp_note.value)
        if gp_note.type.name == 'tie':
            fret_text = '  '
        if gp_note.type.name == 'dead':
            fret_text = 'X'
        if gp_note.effect.isHarmonic:
            fret_text = '<' + fret_text + '>'
        fret_num_glyph = CoreLabel(text=fret_text, font_size=14, font_name='./fonts/Arial')
        fret_num_glyph.refresh()
        ypos = self.y + self.step_y * (8 - (gp_note.string - 1)) - fret_num_glyph.height / 2
        background = Rectangle(pos=(xpos, ypos), size=fret_num_glyph.texture.size)
        fret_num_instr = Rectangle(pos=(xpos, ypos), size=fret_num_glyph.texture.size)
        fret_num_instr.texture = fret_num_glyph.texture
        self.backgrounds.add(background)
        self.glyphs.add(fret_num_instr)

        xmid = xpos + (fret_num_glyph.texture.width / 2)
        return xmid

    def gp_beat_groupby(self, gp_beats: List[guitarpro.models.Beat]):
        beat_groups, cur_group = [], []
        prev_dur = None
        i = 0
        while i < len(gp_beats):
            gp_beat = gp_beats[i]
            # Add rests by themselves.
            if not gp_beat.notes:
                if cur_group:
                    beat_groups.append(cur_group[:])
                    cur_group = []
                beat_groups.append([gp_beat])
                prev_dur = None
                i += 1
            # Add notes within a tuplet together.
            elif gp_beat.duration.tuplet.enters != 1:
                if cur_group:
                    beat_groups.append(cur_group[:])
                    cur_group = []
                tuplet_num = gp_beat.duration.tuplet.enters
                beat_groups.append(gp_beats[i:i + tuplet_num])
                prev_dur = None
                i += tuplet_num
            # Group this single note with a previously existing group.
            elif gp_beat.duration.value == prev_dur and not (
                    gp_beat.duration.isDotted or gp_beat.duration.isDoubleDotted
                    or any(gp_note.effect.slides for gp_note in gp_beat.notes)):
                cur_group += [gp_beat]
                i += 1
            # End the previous group and start a new one.
            else:
                if cur_group:
                    beat_groups += [cur_group[:]]
                cur_group = [gp_beat]
                prev_dur = gp_beat.duration.value
                i += 1
        if cur_group:
            beat_groups += [cur_group[:]]
        return beat_groups

    def add_note_glyphs(self, gp_beat_groups: List[guitarpro.models.Beat], xmids: List[float]):
        bg = x = 0
        while bg < len(gp_beat_groups):
            group = gp_beat_groups[bg]
            gp_beat = group[0]
            # Rest or single note.
            if len(group) == 1:
                if gp_beat.notes:
                    self.draw_stem(gp_beat, xmids[x])
                    self.draw_flags(gp_beat, xmids[x])
                x += 1
            # Tuplet.
            elif gp_beat.duration.tuplet.enters != 1:
                num_tuplet = gp_beat.duration.tuplet.enters
                tuplet_mids = xmids[x:x + num_tuplet]
                self.draw_tuplet(gp_beat, tuplet_mids)
                x += num_tuplet
            # Beamed note.
            elif len(group) % 2 == 0:
                num_notes = len(group)
                self.draw_beamed_notes(gp_beat, xmids[x:x + num_notes])
                x += num_notes
            # Mix of beamed note and single note.
            else:
                num_notes = len(group) - 1
                self.draw_beamed_notes(gp_beat, xmids[x:x + num_notes])
                x += num_notes
                self.draw_stem(gp_beat, xmids[x])
                self.draw_flags(gp_beat, xmids[x])
                x += 1
            bg += 1

    def draw_rest(self, gp_beat: guitarpro.models.Beat, xpos: float):
        # The only font I can find for rests doesn't follow the unicode standard.
        step_y = self.step_y
        unicode_rests = {1: u'\u1D13B', 2: u'\u1D13C', 4: u'\u1D13D', 8: u'\u1D13E', 16: u'\u1D13F'}
        rests = {1: u'\uE102', 2: u'\uE103', 4: u'\uE107', 8: u'\uE109', 16: u'\uE110'}
        rest_ys = {1: step_y * 4, 2: step_y * 3, 4: step_y * 2.5, 8: step_y * 3, 16: step_y * 3}
        rest, rest_y = rests[gp_beat.duration.value], rest_ys[gp_beat.duration.value]
        rest_glyph = CoreLabel(text=rest, font_size=32, font_name='./fonts/mscore-20')
        rest_glyph.refresh()
        rest_instr = Rectangle(pos=(xpos, self.y + rest_y), size=rest_glyph.texture.size)
        rest_instr.texture = rest_glyph.texture
        background = Rectangle(pos=(xpos, self.y + rest_y), size=rest_glyph.texture.size)
        self.backgrounds.add(background)
        self.glyphs.add(rest_instr)
        if gp_beat.duration.isDotted or gp_beat.duration.isDoubleDotted:
            ypos = rest_y + rest_glyph.texture.height * 0.75
            self.draw_dots(gp_beat, xpos, ypos)

    def draw_stem(self, gp_beat: guitarpro.models.Beat, xpos: float):
        lower = (xpos, self.y + self.step_y * 1.5)
        if gp_beat.duration.value == 1:
            return
        if gp_beat.duration.value == 2:
            upper = (xpos, self.y + self.step_y * 2)
        else:
            upper = (xpos, self.y + self.step_y * 2.5)
        stem = Line(points=(*lower, *upper), width=1, cap='square')
        if gp_beat.duration.isDotted or gp_beat.duration.isDoubleDotted:
            xpos, ypos = lower
            ypos += 2
            self.draw_dots(gp_beat, xpos, ypos)
        self.glyphs.add(stem)

    def draw_flags(self, gp_beat: guitarpro.models.Beat, xpos: float):
        # Texture created by mscore-20 font is unnecessarily tall, hard to place exactly.
        flags = {1: '', 2: '', 4: '', 8: u'\uE194', 16: u'\uE197', 32: u'\uE198'}
        flag = flags[gp_beat.duration.value]
        flag_glyph = CoreLabel(text=flag, font_size=32, font_name='./fonts/mscore-20')
        flag_glyph.refresh()
        flag_instr = Rectangle(pos=(xpos, self.y - self.step_y * 1.5), size=flag_glyph.texture.size)
        flag_instr.texture = flag_glyph.texture
        self.glyphs.add(flag_instr)

    def draw_tuplet(self, gp_beat: guitarpro.models.Beat, xmids: List[float]):
        xmin, xmax = xmids[0], xmids[-1]
        for xpos in xmids:
            self.draw_stem(gp_beat, xpos)
        if gp_beat.duration.value == 8:
            self.draw_eightnote_beam(xmin, xmax)
        if gp_beat.duration.value == 16:
            self.draw_eightnote_beam(xmin, xmax)
            self.draw_sixteenthnote_beam(xmin, xmax)

        xmid = (xmin + xmax) / 2
        text_glyph = CoreLabel(text=str(gp_beat.duration.tuplet.enters),
                               font_size=14,
                               font_name='./fonts/Arial')
        text_glyph.refresh()
        text_instr = Rectangle(
            pos=(xmid - text_glyph.texture.width / 2, self.y + self.step_y * 0.5),
            size=text_glyph.texture.size)
        text_instr.texture = text_glyph.texture
        self.glyphs.add(text_instr)

    def draw_beamed_notes(self, gp_beat: guitarpro.models.Beat, xmids: List[float]):
        xmin, xmax = xmids[0], xmids[-1]
        for xpos in xmids:
            self.draw_stem(gp_beat, xpos)
        if gp_beat.duration.value == 8:
            self.draw_eightnote_beam(xmin, xmax)
        if gp_beat.duration.value == 16:
            self.draw_eightnote_beam(xmin, xmax)
            self.draw_sixteenthnote_beam(xmin, xmax)

    def draw_eightnote_beam(self, xmin: float, xmax: float):
        lowbeam = Line(points=(xmin, self.y + self.step_y * 1.5,
                               xmax, self.y + self.step_y * 1.5),
                       width=1.4,
                       cap='square')
        self.glyphs.add(lowbeam)

    def draw_sixteenthnote_beam(self, xmin: float, xmax: float):
        highbeam = Line(points=(xmin, self.y + self.step_y * 1.75,
                                xmax, self.y + self.step_y * 1.75),
                        width=1.1,
                        cap='square')
        self.glyphs.add(highbeam)

    def draw_dots(self, gp_beat: guitarpro.models.Beat, xpos: float, ypos: float):
        xpos += 4
        dot_size = (3, 3)
        if gp_beat.duration.isDotted:
            dot = Ellipse(pos=(xpos, ypos), size=dot_size)
            self.glyphs.add(dot)
        elif gp_beat.duration.isDoubleDotted:
            dot1 = Ellipse(pos=(xpos, ypos), size=dot_size)
            dot2 = Ellipse(pos=(xpos + 4, ypos), size=dot_size)
            self.glyphs.add(dot1)
            self.glyphs.add(dot2)

    def draw_note_effects(self, gp_beats: List[guitarpro.models.Beat], xmids: List[float]):
        for i, (gp_beat, xmid) in enumerate(zip(gp_beats, xmids)):
            for gp_note in gp_beat.notes:
                if gp_note.type.name == "tie":
                    if i != 0:
                        self.draw_tie(gp_note, xmids[i-1], xmids[i])
                    else:
                        self.starts_with_tie = True
                elif gp_note.effect.slides:
                    if i != len(xmids) - 1:
                        self.draw_slide(gp_note, xmids[i], xmids[i+1])
                    else:
                        self.ends_with_slide = True

    def draw_tie(self, gp_note: guitarpro.models.Note, start: float, end: float):
        string_y = self.y + self.step_y * (8 - (gp_note.string - 1))
        line_mid = (start + end) / 2
        points = (start, string_y - self.step_y / 3,
                  line_mid, string_y - self.step_y,
                  end, string_y - self.step_y / 3)
        tie_line = Bezier(points=points)
        self.glyphs.add(tie_line)

    def draw_tie_across_measures(self, gp_beat: guitarpro.models.Beat, start: float, end: float):
        for gp_note in gp_beat.notes:
            if gp_note.type.name == "tie":
                self.draw_tie(gp_note, start, end)

    def draw_slide(self, gp_note: guitarpro.models.Note, start, end):
        # There are 7 guitarpro.models.SlideTypes. So far only shiftSlideto, value == 1.
        string_y = self.y + self.step_y * (8 - (gp_note.string - 1))
        padding = 10
        start += padding
        end -= padding
        points = (start, string_y + self.step_y / 4, end,  string_y - self.step_y / 4)
        slide_line = Line(points=points)
        self.glyphs.add(slide_line)


class SongBuilderApp(App):
    pass


if __name__ == "__main__":
    SongBuilderApp().run()
