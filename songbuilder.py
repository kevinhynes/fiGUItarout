from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

import guitarpro

from song_data import song_data
from music_constants import chrom_scale

black = Color(0, 0, 0, 1)


class KivyBeat:
    def __init__(self, seconds: float, frets: list, notes: list = None, duration: object = None):
        self.seconds = seconds
        self.frets = frets
        self.notes = notes
        self.duration = duration


class TabViewer(ScrollView):
    file = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.song_data = song_data
        self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)


        # Testing the TabViewer build.
        # for measure in self.song_data:
        #     tab = TabWidget(measure)
        #     self.box.height += tab.height
        #     self.box.add_widget(tab)
        # print(tab.width)
        # self.add_widget(self.box)

        self.gp_song = guitarpro.parse('./tgr-nm-01.gp5')
        self.flat_song = self.flatten_song()
        float_height = self.calc_float_height()
        self.floatlayout = FloatLayout(size_hint_y=None, height=float_height)
        tab_widget = TabWidget()
        self.child_y = float_height - tab_widget.height

        # self.print_flattened_track(self.flat_song[0])
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

        Tracks list represents each guitar.
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

    def calc_float_height(self):
        height = 0
        spacing = 10
        tab_widget = TabWidget()
        for gp_measure in self.flat_song[0]:
            height += tab_widget.height + spacing
            if gp_measure.timeSignature.numerator / gp_measure.timeSignature.denominator.value > 1:
                height += tab_widget.height + spacing
        return height

    def build_track(self, flat_track):
        for gp_measure in flat_track:
            self.add_measure(gp_measure)
        self.add_widget(self.floatlayout)

    def add_measure(self, gp_measure):
        # In order to keep scrolling bar moving at same speed for all measures at the same tempo,
        # some measures (7/4, 9/8...) will need an extra line
        timesig_ratio = gp_measure.timeSignature.numerator / gp_measure.timeSignature.denominator.value
        spacing = 10

        tab_widget = TabWidget(pos=(0, self.child_y))
        tab_widget.build_measure(gp_measure, 0)
        next_beat_idx = tab_widget.get_next_beat_idx()
        self.floatlayout.add_widget(tab_widget)
        self.child_y -= tab_widget.height + spacing

        if timesig_ratio > 1:
            print(f'\t  {next_beat_idx} / {len(gp_measure.voices[0].beats)}')
            tab_widget = TabWidget(pos=(0, self.child_y))
            tab_widget.build_measure(gp_measure, next_beat_idx)
            self.floatlayout.add_widget(tab_widget)
            self.child_y -= tab_widget.height + spacing


class TabWidget(Widget):

    def __init__(self, **kwargs):
        self.step_y = 20
        # self.step_x = 8
        self.measure_start = 64
        self.tab_width = 1024
        super().__init__(**kwargs)
        self.glyphs = InstructionGroup()
        self.backgrounds = InstructionGroup()
        self.tuplet_count = 0
        self.canvas.add(Color(1, 0, 0, 0.5))
        self.canvas.add(self.backgrounds)
        self.canvas.add(black)
        self.canvas.add(self.glyphs)

    def get_next_beat_idx(self):
        return self.next_beat_idx

    def build_measure(self, gp_measure, start_idx):
        self.add_timesig(gp_measure)
        for gp_voice in gp_measure.voices[:-1]:
            print(f'Header Number {gp_measure.header.number}')
            xpos = self.measure_start
            for beat_idx, gp_beat in enumerate(gp_voice.beats[start_idx:]):
                beat_width = (1 / gp_beat.duration.value) * (
                            gp_beat.duration.tuplet.times / gp_beat.duration.tuplet.enters) * self.tab_width
                self.add_beat(gp_beat, xpos)
                xpos += beat_width
                if xpos >= self.tab_width + self.measure_start:
                    print(f'Breaking for second line of tab')
                    break
        self.next_beat_idx = beat_idx + 1
        self.xpos_end = xpos

    def add_timesig(self, gp_measure):
        num, den = gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value
        num_instr = Rectangle(pos=(self.x, self.y + self.step_y * 6), size=(self.step_y, self.step_y*2))
        den_instr = Rectangle(pos=(self.x, self.y + self.step_y * 4), size=(self.step_y, self.step_y*2))
        num_glyph = CoreLabel(text=str(num))
        den_glyph = CoreLabel(text=str(den))
        num_glyph.refresh()
        den_glyph.refresh()
        num_instr.texture = num_glyph.texture
        den_instr.texture = den_glyph.texture
        self.glyphs.add(num_instr)
        self.glyphs.add(den_instr)

    def add_beat(self, gp_beat, xpos):
        self.add_note_duration_glyph(gp_beat.duration, xpos)
        for gp_note in gp_beat.notes:
            fret_text = str(gp_note.value)
            if gp_note.effect.isHarmonic:
                fret_text = '<' + fret_text + '>'
            ypos = self.y + self.step_y * (8 - (gp_note.string-1)) - self.step_y / 2
            background = Rectangle(pos=(xpos, ypos), size=(self.get_fret_num_size(fret_text)))
            fret_num_instr = Rectangle(pos=(xpos, ypos), size=self.get_fret_num_size(fret_text))
            fret_num_glyph = CoreLabel(text=fret_text)
            fret_num_glyph.refresh()
            fret_num_instr.texture = fret_num_glyph.texture
            self.backgrounds.add(background)
            self.glyphs.add(fret_num_instr)

    def get_fret_num_size(self, fret_num):
        mult = len(str(fret_num))
        return 8 * mult, self.step_y

    def add_note_duration_glyph(self, duration, xpos):
        normal = {1: self.add_whole_note,
                  2: self.add_half_note,
                  4: self.add_quarter_note,
                  8: self.add_eight_note,
                  16: self.add_sixteenth_note}
        tuplet = {8: self.add_eighth_note_tuplet,
                  16: self.add_sixteenth_note_tuplet}
        if duration.tuplet.times == 1:
            func = normal[duration.value]
            func(xpos)
        elif self.tuplet_count == 0:
            func = tuplet[duration.value]
            func(xpos, duration)
            self.tuplet_count = 1
        else:
            self.tuplet_count += 1
            if self.tuplet_count == duration.tuplet.enters:
                self.tuplet_count = 0

    def add_sixteenth_note(self, xpos):
        pass

    def add_eight_note(self, xpos):
        pass

    def add_quarter_note(self, xpos):
        glyph = Line(points=(xpos + 4, self.y + self.step_y * 1.5,
                            xpos + 4, self.y + self.step_y * 2.5))
        self.glyphs.add(glyph)

    def add_half_note(self, xpos):
        pass

    def add_whole_note(self, xpos):
        pass

    def add_eighth_note_tuplet(self, xpos, duration):
        step = (1 / duration.value) * (duration.tuplet.times / duration.tuplet.enters) * self.tab_width
        xmin, xmax = float('inf'), float('-inf')
        # Vertical bars.
        for i in range(duration.tuplet.enters):
            xpos *= i * step
            xmin, xmax = min(xmin, xpos), max(xmax, xpos)
            glyph = Line(points=(xpos + 4, self.y + self.step_y * 1.5,
                            xpos + 4, self.y + self.step_y * 2.5))
            self.glyphs.add(glyph)
        # Horizontal bars.
        lowbar = Line(points=(xmin, self.y + self.step_y * 1.5,
                             xmax, self.y + self.step_y * 1.5),
                     width=1.05)
        self.glyphs.add(lowbar)
        # Tuplet text.
        xmid = (xmin + xmax) / 2
        text_width, text_height = self.get_fret_num_size(duration.tuplet.times)
        text_instr = Rectangle(pos=(xmid - text_width / 2, self.y + self.step_y * 1.25),
                               size=(text_width, text_height))
        text_glyph = CoreLabel(text=str(duration.tuplet.enters))
        text_glyph.refresh()
        text_instr.texture = text_glyph.texture
        self.glyphs.add(text_instr)

    def add_sixteenth_note_tuplet(self, xpos, duration):
        step = (1 / duration.value) * (duration.tuplet.times / duration.tuplet.enters) * self.tab_width
        xmin, xmax = float('inf'), float('-inf')
        # Vertical bars.
        for i in range(duration.tuplet.enters):
            glyph_x = xpos + i * step
            print(i, xpos)
            xmin, xmax = min(xmin, glyph_x), max(xmax, glyph_x)
            glyph = Line(points=(glyph_x + 4, self.y + self.step_y * 1.5,
                            glyph_x + 4, self.y + self.step_y * 2.5))
            self.glyphs.add(glyph)
        # Horizontal bars.
        lowbar = Line(points=(xmin, self.y + self.step_y * 1.5,
                              xmax, self.y + self.step_y * 1.5),
                      width=1.05)
        highbar = Line(points=(xmin, self.y + self.step_y * 1.75,
                               xmax, self.y + self.step_y * 1.75),
                      width=1.05)
        self.glyphs.add(lowbar)
        self.glyphs.add(highbar)
        # Tuplet text.
        xmid = (xmin + xmax) / 2
        text_width, text_height = self.get_fret_num_size(duration.tuplet.times)
        text_instr = Rectangle(pos=(xmid - text_width / 2, self.y + self.step_y * 0.5),
                               size=(text_width, text_height))
        text_glyph = CoreLabel(text=str(duration.tuplet.enters))
        text_glyph.refresh()
        text_instr.texture = text_glyph.texture
        self.glyphs.add(text_instr)


class SongBuilderApp(App):
    pass


if __name__ == "__main__":
    SongBuilderApp().run()
