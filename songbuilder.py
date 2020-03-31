from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.properties import NumericProperty, ObjectProperty, AliasProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle, Ellipse, InstructionGroup, Bezier
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

import guitarpro
from typing import List
import song_library_funcs as slf
from songlibrary import SongLibraryPopup

black = Color(0, 0, 0, 1)


class SongBuilder(FloatLayout):
    spt_conn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.hide, 1)

    def hide(self, *args):
        self.top = 0

    def slide(self, keysigtitlebar):
        if self.top == 0:
            self.top = keysigtitlebar.top
        else:
            self.top = 0


class TabViewer(ScrollView):
    songbuilder = ObjectProperty()
    editbar = ObjectProperty()
    spt_conn = ObjectProperty()

    def __init__(self, **kwargs):
        self.prev_timesig = None
        self.prev_tabwidget = None
        self.clipboard = []
        self.keyboard = Window.request_keyboard(self.close_keyboard, self)
        self.keyboard.bind(on_key_down=self.on_key_down)
        self.keyboard.bind(on_key_up=self.on_key_up)
        self.shift_pressed = False
        self.selected_children = []
        super().__init__(**kwargs)
        self.floatlayout = TabFloatLayout(tabviewer=self, size_hint_y=None)
        self.add_widget(self.floatlayout)

    def close_keyboard(self, *args):
        self.keyboard.unbind(on_key_down=self.on_key_down)
        self.keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        keynum, keytext = keycode
        if keytext == 'shift':
            self.shift_pressed = True
        else:
            self.shift_pressed = False

    def on_key_up(self, keyboard, keycode):
        keynum, keytext = keycode
        if keytext == 'shift':
            self.shift_pressed = False

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
        PyGuitarPro does not appear to be parsing measure.header.repeatAlternative correctly.
        Also, no info on Da Capo or Dal Segno type of repeats. Requires user to copy/paste/delete
        in order to make corrections.
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
                # Single measures may be repeated by themselves.
                if gp_measure.repeatClose > 0:
                    repeat_group *= gp_measure.repeatClose
                    flat_track += repeat_group
                    repeat_group = []
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

    def set_floatlayout_height(self):
        height = 0
        spacing = 10
        tabwidget = TabWidget()
        prev_timesig = None
        prev_measure = None
        child_parity = 'left'
        for gp_measure in self.flat_song[0]:
            timesig = (gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value)
            prev_timesig_ratio = prev_timesig[0] / prev_timesig[1] if prev_timesig else 0
            # Place first measure all the way at the top left.
            if prev_measure is None:
                height += tabwidget.height + spacing
                child_parity = 'right'
            # Place the next measure on a new line below.
            elif (prev_timesig_ratio > 1
                  or prev_timesig != timesig
                  or prev_measure.repeatClose > 0
                  or gp_measure.isRepeatOpen
                  or child_parity == 'left'):
                height += tabwidget.height + spacing
                child_parity = 'right'
            # Place the next measure to the right of the last measure of the same time signature.
            else:
                child_parity = 'left'
            prev_measure = gp_measure
            prev_timesig = timesig
        # Add 1 extra tabwidget.height for songlabel
        self.floatlayout.height = height + tabwidget.height

    def set_child_y(self):
        tabwidget = TabWidget()
        self.child_y = self.floatlayout.height - tabwidget.height

    def add_song_label(self):
        tabwidget = TabWidget()
        song_name = (self.gp_song.artist + " - " + self.gp_song.title).upper()
        song_label = Label(text=song_name, font_size=32, font_name='./fonts/Impact',
                           halign='center', valign='center',
                           size_hint=(1, None), height=(tabwidget.height), pos=(0, self.child_y))
        self.floatlayout.add_widget(song_label)
        self.child_y -= tabwidget.height

    def build_track(self, flat_track):
        self.add_song_label()
        total_measures = len(flat_track)
        self.prev_timesig = self.prev_timesig_ratio = self.prev_tabwidget = None
        for i, gp_measure in enumerate(flat_track):
            self.add_measure(gp_measure, i, total_measures)

    def add_measure(self, gp_measure, idx, total_measures):
        timesig = (gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value)
        prev_tabwidget = self.prev_tabwidget
        prev_timesig = self.prev_timesig
        prev_timesig_ratio = prev_timesig[0] / prev_timesig[1] if prev_timesig else 0
        spacing = 10
        tabwidget = TabWidget(self, idx, total_measures)

        # Place first measure all the way at the top left.
        if prev_tabwidget is None:
            tabwidget.pos = (0, self.child_y)
        # Place the next measure on a new line below.
        elif (prev_timesig_ratio > 1 or prev_timesig != timesig
              or prev_tabwidget.close_repeat_width > 0 or prev_tabwidget.x != 0
              or gp_measure.isRepeatOpen):
            self.child_y -= tabwidget.height + spacing
            tabwidget.pos = (0, self.child_y)
        # Place the next measure to the right of the last measure of the same time signature.
        else:
            tabwidget.timesig_width = 0
            tabwidget.pos = (prev_tabwidget.right, self.child_y)

        tabwidget.build_measure(gp_measure)
        if tabwidget.starts_with_tie:
            start = self.prev_tabwidget.xmids[-1]
            end = tabwidget.xmids[0]
            tabwidget.draw_tie_across_measures(tabwidget.gp_beats[0], start, end)
        self.prev_tabwidget = tabwidget
        self.prev_timesig = timesig
        self.floatlayout.add_widget(tabwidget)

    def select(self, tabwidget):
        # If no other tabwigets are selected, shift and normal select do the same thing.
        if not self.selected_children:
            tabwidget.select()
            self.selected_children[:] = [tabwidget]
            return
        if self.shift_pressed:
            self.shift_select(tabwidget)
            return
        for selectedwidget in self.selected_children:
            selectedwidget.unselect()
        tabwidget.select()
        self.selected_children = [tabwidget]

    def shift_select(self, tabwidget):
        to_select = []
        # Selected TabWidget is above the existing group.
        if tabwidget.idx < self.selected_children[0].idx:
            i = self.tabwidget_to_child_idx(self.selected_children[0])
            j = self.tabwidget_to_child_idx(tabwidget)
            to_select = self.floatlayout.children[i+1:j+1]  # Don't include i, include j.
            self.selected_children[:] = to_select[::-1] + self.selected_children
        # Selected TabWidget is below the existing selected group.
        elif tabwidget.idx > self.selected_children[-1].idx:
            i = self.tabwidget_to_child_idx(tabwidget)
            j = self.tabwidget_to_child_idx(self.selected_children[-1])
            to_select = self.floatlayout.children[i:j]
            self.selected_children[:] = self.selected_children + to_select[::-1]
        for tabwidget in to_select:
            tabwidget.select()
        print("TabViewer.shift_select, ", [selectedwidget.idx for selectedwidget in self.selected_children])

    def unselect_all(self):
        for tabwidget in self.selected_children:
            tabwidget.unselect()
        self.selected_children = []

    def copy(self, *args):
        self.clipboard = [child.idx for child in self.floatlayout.children if \
                          isinstance(child, TabWidget) and child.is_selected]
        print("TabViewer.copy, clipboard: ", self.clipboard)
        self.show_copy_notification()
        for child in self.selected_children:
            child.is_selected = False
        self.editbar.ids.insert_before_btn.disabled = False
        self.editbar.ids.insert_after_btn.disabled = False

    def show_copy_notification(self):
        popup = CopyPopup()
        popup.open()
        Clock.schedule_once(popup.dismiss, 0.75)

    def insert_before(self, *args):
        before_idx = self.clipboard[0]
        for i, track in enumerate(self.flat_song):
            paste_measures = [track[j] for j in self.clipboard]
            self.flat_song[i] = track[:before_idx] + paste_measures + track[before_idx:]
        self.unselect_all()
        self.editbar.ids.insert_before_btn.disabled = True
        self.editbar.ids.insert_after_btn.disabled = True
        self.rebuild()

    def insert_after(self, *args):
        after_idx = self.clipboard[-1]
        for i, track in enumerate(self.flat_song):
            paste_measures = [track[j] for j in self.clipboard]
            self.flat_song[i] = track[:after_idx+1] + paste_measures + track[after_idx+1:]
        self.unselect_all()
        self.editbar.ids.insert_before_btn.disabled = True
        self.editbar.ids.insert_after_btn.disabled = True
        self.rebuild()

    def delete(self, *args):
        def tabwidget_sort(tabwidget):
            return -tabwidget.idx
        tabwidgets_to_delete = [child for child in self.floatlayout.children if \
                                isinstance(child, TabWidget) and child.is_selected]
        tabwidgets_to_delete.sort(key=tabwidget_sort)
        for child in tabwidgets_to_delete:
            self.floatlayout.remove_widget(child)
            print(child.idx)
            for i, track in enumerate(self.flat_song):
                del self.flat_song[i][child.idx]
        self.reindex_tabwidgets()

    def reindex_tabwidgets(self):
        '''TabWidget.idx should point to the relevant gp_measure in self.flat_song[0].'''
        # floatlayout also contains song title Lable
        tabwidgets = [child for child in self.floatlayout.children if isinstance(child, TabWidget)]
        for i, child in enumerate(tabwidgets[::-1]):
            child.idx = i

    def tabwidget_to_child_idx(self, tabwidget):
        '''First TabWidget (TabWidget.idx == 0) in floatlayout is last in floatlayout.children.'''
        last_index = len(self.floatlayout.children) - 2  # Additional -1 for header.
        return last_index - tabwidget.idx

    def rebuild(self, *args):
        self.set_floatlayout_height()
        self.set_child_y()
        self.prev_tabwidget = self.prev_timesig = None
        self.floatlayout.clear_widgets()
        self.build_track(self.flat_song[0])

    def show_fileloader(self, *args):
        content = FileLoaderPopupContent(load_new_file=self.load_new_file, cancel=self.close_fileloader)
        self.fileloader_popup = Popup(title="Load New Guitar Pro Song", content=content,
                                      size_hint=(0.9, 0.9))
        self.fileloader_popup.open()

    def load_new_file(self, filepath):
        self.fileloader_popup.dismiss()
        self.load_file(filepath[0], False)

    def close_fileloader(self, *args):
        self.fileloader_popup.dismiss()

    def save(self, *args):
        gp_song = self.gp_song
        artist, album, song_title = gp_song.artist.title(), gp_song.album.title(), gp_song.title.title()
        song_name = '-'.join([artist, album, song_title]).lower() + '.gp5'
        filepath = './song-library/' + song_name
        # Check if song already exists in database.
        if slf.get_saved_song_file(artist, album, song_title):
            self.fileoverwrite_popup = FileOverwritePopup(cancel=self.cancel_overwrite,
                                                          overwrite=self.overwrite,
                                                          artist=artist, album=album,
                                                          song_title=song_title)
            self.fileoverwrite_popup.open()
        else:
            editted_gp_song = gp_song
            for i in range(len(gp_song.tracks)):
                flat_track = self.flat_song[i]
                editted_gp_song.tracks[i].measures[:] = flat_track
            guitarpro.write(editted_gp_song, filepath, version=(5, 1, 0), encoding='cp1252')
            slf.save_song_to_library(artist, album, song_title, filepath)

    def overwrite(self, artist: str, album: str, song_title: str) -> None:
        song_name = '-'.join([artist, album, song_title]).lower() + '.gp5'
        filepath = './song-library/' + song_name
        gp_song = self.gp_song
        editted_gp_song = gp_song
        for i in range(len(gp_song.tracks)):
            flat_track = self.flat_song[i]
            editted_gp_song.tracks[i].measures[:] = flat_track
        guitarpro.write(editted_gp_song, filepath, version=(5, 1, 0), encoding='cp1252')
        self.fileoverwrite_popup.dismiss()

    def cancel_overwrite(self, *args):
        self.fileoverwrite_popup.dismiss()

    def show_song_library(self, *args):
        # content = SongLibrary(size_hint=(0.9, 0.9), load_saved_file=self.load_saved_file)
        # self.song_library_popup = Popup(title="Song Library", content=content, size_hint=(0.9, 0.9))
        self.song_library_popup = SongLibraryPopup(load_saved_file=self.load_saved_file)
        self.song_library_popup.open()

    def load_saved_file(self, filepath):
        self.song_library_popup.dismiss()
        self.load_file(filepath, True)

    def load_file(self, filepath, from_song_library):
        self.gp_song = guitarpro.parse(filepath)
        # Saved songs in ./song-library/ are already flattened.
        if not from_song_library:
            self.flat_song = self.flatten_song()
        else:
            self.flat_song = []
            for track in self.gp_song.tracks:
                self.flat_song.append(track.measures)
        self.floatlayout.clear_widgets()
        self.set_floatlayout_height()
        self.set_child_y()
        self.build_track(self.flat_song[0])

    def play(self, *args):
        query = self.gp_song.artist + ' ' + self.gp_song.title
        query.lower()
        if self.spt_conn:
            self.spt_conn.play_on_spotify(query)
        tempo = self.gp_song.tempo
        self.floatlayout.play(tempo)


class TabFloatLayout(FloatLayout):
    scrollbar1_x = NumericProperty(0)
    scrollbar1_y = NumericProperty(0)

    def __init__(self, tabviewer=None, **kwargs):
        super().__init__(**kwargs)
        self.tabviewer = tabviewer

    def on_touch_down(self, touch):
        tabwidget_touched = super().on_touch_down(touch)
        if not tabwidget_touched:
            self.tabviewer.unselect_all()

    def play(self, tempo):
        # The GuitarPro songs' tempo are of form BPM where the B(eat) is always a quarter note.
        self.beat_width = self.children[0].measure_width / 4
        self.seconds_per_beat = 60 / tempo

        self.scroll_coords = self.build_scroll_coords()
        self.scroll_coords_idx = 0
        self._play_next_line()

    def _play_next_line(self, *args):
        if self.scroll_coords_idx == len(self.scroll_coords):
            return
        x_start, x_stop, y, scroll_y = self.scroll_coords[self.scroll_coords_idx]
        num_beats = (x_stop - x_start) / self.beat_width
        seconds = self.seconds_per_beat * num_beats
        self.scroll_coords_idx += 1
        self.scrollbar1_x = x_start - 5
        self.scrollbar1_y = y
        self.tabviewer.scroll_y = scroll_y
        anim = Animation(scrollbar1_x=x_stop-5, d=seconds)
        anim.bind(on_complete=self._play_next_line)
        anim.start(self)

    def build_scroll_coords(self):
        # Scrolling bar will traverse 1 or more measures at a time. Build list of coordinates
        # for the scrolling bar to scroll to.
        tabwidgets = [child for child in self.children if isinstance(child, TabWidget)]
        scroll_coords = []
        i = len(tabwidgets) - 1
        scroll_y = 1
        while i >= 0:
            x_start = tabwidgets[i].measure_start
            while tabwidgets[i-1].x != 0:
                i -= 1
            x_stop = tabwidgets[i].measure_end
            y = tabwidgets[i].y
            # if scroll_y > self.tabview.height:
            scroll_y -= (210 / (self.height - self.tabviewer.height))
            scroll_coords.append((x_start, x_stop, y, scroll_y))
            i -= 1
        return scroll_coords


class TabWidget(Widget):
    open_repeat_opac = NumericProperty(0)
    close_repeat_opac = NumericProperty(0)
    selected_opac = NumericProperty(0)

    timesig_width = NumericProperty(64)
    open_repeat_width = NumericProperty(0)
    close_repeat_width = NumericProperty(0)
    measure_end = NumericProperty(0)

    def get_barline_x(self):
        return self.x + self.timesig_width
    barline_x = AliasProperty(get_barline_x, None,
                                  bind=['x', 'timesig_width'], cache=True)

    def get_measure_start(self):
        return self.x + self.timesig_width + self.open_repeat_width
    measure_start = AliasProperty(get_measure_start, None,
                                  bind=['x', 'timesig_width', 'open_repeat_width'], cache=True)

    def __init__(self, tabviewer=None, idx=0, total_measures=0, **kwargs):
        self.tabviewer = tabviewer
        self.idx = idx
        self.total_measures = total_measures
        self.step_y = 20
        self.measure_width = 512  # width of a 4/4 measure only, sort of a step_x.
        self.starts_with_tie = False
        self.ends_with_slide = False
        self.is_selected = False
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
        if self.x == 0:
            self.draw_timesig(gp_measure)
        self.draw_measure_number(gp_measure)
        self.draw_open_repeat(gp_measure)
        self.gp_beats, self.xmids = self.add_staff_glyphs(gp_measure)
        self.draw_note_effects(self.gp_beats, self.xmids)
        gp_beat_groups = self.gp_beat_groupby(self.gp_beats)
        self.add_note_glyphs(gp_beat_groups, self.xmids)
        self.draw_close_repeat(gp_measure)
        self.draw_measure_count()

    def draw_timesig(self, gp_measure: guitarpro.models.Measure):
        num, den = gp_measure.timeSignature.numerator, gp_measure.timeSignature.denominator.value
        num_glyph = CoreLabel(text=str(num), font_size=50, font_name='./fonts/PatuaOne-Regular')
        den_glyph = CoreLabel(text=str(den), font_size=50, font_name='./fonts/PatuaOne-Regular')
        num_glyph.refresh()
        den_glyph.refresh()
        num_x = (self.barline_x / 2) - (num_glyph.texture.width / 2)
        den_x = (self.barline_x / 2) - (den_glyph.texture.width / 2)
        num_instr = Rectangle(pos=(num_x, self.y + self.step_y * 5), size=(num_glyph.texture.size))
        den_instr = Rectangle(pos=(den_x, self.y + self.step_y * 3), size=(den_glyph.texture.size))
        num_instr.texture = num_glyph.texture
        den_instr.texture = den_glyph.texture
        self.glyphs.add(num_instr)
        self.glyphs.add(den_instr)

    def draw_measure_number(self, gp_measure: guitarpro.models.Measure):
        num = gp_measure.header.number
        num_glyph = CoreLabel(text=str(num), font_size=14, font_name='./fonts/Arial')
        num_glyph.refresh()
        num_x = self.barline_x - num_glyph.width
        num_y = self.y + self.step_y * 8
        num_instr = Rectangle(pos=(num_x, num_y), size=num_glyph.texture.size)
        num_instr.texture = num_glyph.texture
        self.glyphs.add(num_instr)

    def draw_measure_count(self):
        # TODO: Once copy/delete buttons are added, update measure counts.
        measure_count = str(self.idx + 1) + ' / ' + str(self.total_measures)
        count_glyph = CoreLabel(text=measure_count, font_size=14, font_name='./fonts/Arial')
        count_glyph.refresh()
        count_x = self.right - (count_glyph.width + 5)
        count_y = self.y
        count_instr = Rectangle(pos=(count_x, count_y), size=count_glyph.size)
        count_instr.texture = count_glyph.texture
        self.glyphs.add(count_instr)

    def draw_open_repeat(self, gp_measure: guitarpro.models.Measure):
        if gp_measure.isRepeatOpen:
            self.open_repeat_opac = 1
            self.open_repeat_width = 25

    def draw_close_repeat(self, gp_measure: guitarpro.models.Measure):
        if gp_measure.repeatClose > 0:
            self.close_repeat_opac = 1
            self.close_repeat_width = 25

    def add_staff_glyphs(self, gp_measure: guitarpro.models.Measure):
        gp_beats, xmids = [], []
        for gp_voice in gp_measure.voices[:-1]:
            xpos = self.measure_start
            for beat_idx, gp_beat in enumerate(gp_voice.beats):
                note_dur = 1 / gp_beat.duration.value
                tuplet_mult = gp_beat.duration.tuplet.times / gp_beat.duration.tuplet.enters
                beat_width = note_dur * tuplet_mult * self.measure_width
                if gp_beat.duration.isDotted:
                    beat_width *= 3 / 2
                elif gp_beat.duration.isDoubleDotted:
                    beat_width *= 7 / 4
                beat_mid = self.add_beat_glyph(gp_beat, xpos)
                xmids += [beat_mid]
                gp_beats += [gp_beat]
                xpos += beat_width
        self.measure_end = xpos
        return gp_beats, xmids

    def add_beat_glyph(self, gp_beat: guitarpro.models.Beat, xpos: float):
        # If notes list is empty, rest for gp_beat.duration.value.
        if not gp_beat.notes:
            self.draw_rest(gp_beat, xpos)
            return xpos
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
        fret_num_glyph = CoreLabel(text=fret_text, font_size=14, font_name='./fonts/Arial', bold=True)
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
        rests = {1: u'\uE102', 2: u'\uE103', 4: u'\uE107', 8: u'\uE109', 16: u'\uE10A'}
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

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.tabviewer.no_tabwidgets_touched = False
            self.tabviewer.select(self)
            return True
        return super().on_touch_down(touch)

    def select(self):
        self.is_selected = True
        self.selected_opac = 0.5

    def unselect(self):
        self.is_selected = False
        self.selected_opac = 0


class EditToolbar(FloatLayout):
    tabviewer = ObjectProperty()


# class SongLibrary(Carousel):
#     load_saved_file = ObjectProperty()
#     artist = StringProperty('')
#     album = StringProperty('')
#     song = StringProperty('')
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.artists_page = SongLibraryPage(name='Artists', carousel=self)
#         self.albums_page = SongLibraryPage(name='Albums', carousel=self)
#         self.songs_page = SongLibraryPage(name='Songs', carousel=self)
#         for page in (self.artists_page, self.albums_page, self.songs_page):
#             self.add_widget(page)
#
#     def on_press(self, button):
#         if self.current_slide.name == 'Artists':
#             self.artist = button.text
#             self.load_next(mode='next')
#         elif self.current_slide.name == 'Albums':
#             self.album = button.text
#             self.load_next(mode='next')
#         elif self.current_slide.name == 'Songs':
#             self.song = button.text
#
#     def on_artist(self, *args):
#         albums = slf.get_albums_by_artist(self.artist)
#         self.albums_page.update_list(albums)
#
#     def on_album(self, *args):
#         songs = slf.get_songs_on_album(self.artist, self.album)
#         self.songs_page.update_list(songs)
#
#     def on_song(self, *args):
#         filepath = slf.get_saved_song_file(self.artist, self.album, self.song)
#         self.load_saved_file(filepath)
#
#
# class SongLibraryPage(FloatLayout):
#
#     def __init__(self, name=None, carousel=None, **kwargs):
#         super().__init__(**kwargs)
#         self.name = name
#         self.carousel = carousel
#         self.header = SongLibraryHeader(text=name.title())
#         self.add_widget(self.header)
#         if name == 'Artists':
#             artists = slf.get_artists()
#             self.update_list(artists)
#
#     def update_list(self, str_list):
#         buttons = [child for child in self.children if isinstance(child, Button)]
#         while len(str_list) < len(buttons):
#             self.remove_widget(self.children[-1])
#             buttons.pop()
#
#         prev_widget = self.header
#         while len(str_list) > len(buttons):
#             button = Button(size_hint=[None, None], size=[350, 50])
#             button.top = prev_widget.y
#             prev_widget.bind(y=button.setter('top'))
#             buttons.append(button)
#             self.add_widget(button)
#             button.bind(on_press=self.carousel.on_press)
#             prev_widget = button
#
#         for child, text in zip(buttons, str_list):
#             child.text = text
#
#
# class SongLibraryHeader(Label):
#     pass


class FileLoaderPopupContent(BoxLayout):
    load_new_file = ObjectProperty()
    cancel = ObjectProperty()


class CopyPopup(Popup):
    pass


class FileOverwritePopup(Popup):
    cancel = ObjectProperty()
    overwrite = ObjectProperty()
    artist = StringProperty()
    album = StringProperty()
    song_title = StringProperty()


class SongBuilderApp(App):
    def build(self):
        return SongBuilder()


if __name__ == "__main__":
    SongBuilderApp().run()
