from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

from kivy.graphics import Rectangle, Color

import json

from music_constants import major_chord_shapes, minor_chord_shapes, \
    dom_chord_shapes, sus_chord_shapes, dim_chord_shapes, aug_chord_shapes, \
    chrom_scale, standard_tuning
from chord_finder import get_chord_voicings_for_tuning
from chord_voicing_generator import get_chord_num_master_voicings


Builder.load_file('chorddiagram.kv')

chord_groups = {
    'Major': major_chord_shapes, 'Minor': minor_chord_shapes,
    'Dominant': dom_chord_shapes, 'Suspended': sus_chord_shapes,
    'Diminished': dim_chord_shapes, 'Augmented': aug_chord_shapes
    }

ROW_HEIGHT = dp(95)


class BackGroundColorWidget(Widget):
    pass


class ChordDisplay(ScrollView):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])

    top_prop = NumericProperty(0)
    instrument_rack = ObjectProperty(None)

    def __init__(self, **kwargs):
        # self.chords_to_voicings = get_chord_voicings_for_tuning(standard_tuning)
        super().__init__(**kwargs)
        self.is_shown = False
        # No text in some groups and fold_buttons are tiny initially without this.
        Clock.schedule_once(self.top_justify_all, 5)

    def top_justify_all(self, *args):
        if self.ids.scroll_child and self.ids.titlebar:
            self.ids.titlebar.top = self.ids.scroll_child.top
        for child in self.ids.scroll_child.children:
            child.top_justify()

    def slide(self, keysigtitlebar):
        if not self.is_shown:
            app = App.get_running_app()
            self.height = keysigtitlebar.top
            self.top = keysigtitlebar.top
            self.is_shown = True
        else:
            self.top = 0
            self.is_shown = False

    def slide_to_rack(self, *args):
        if self.instrument_rack:
            instrument_rack = self.instrument_rack
            if not self.is_shown:
                self.height = instrument_rack.y  # Change the size,
                self.top_prop = instrument_rack.y  # before changing the position.
                instrument_rack.bind(y=self.top_prop_setter)
                self.is_shown = True
            else:
                instrument_rack.unbind(y=self.top_prop_setter)
                self.top_prop = 0
                self.is_shown = False

    def top_prop_setter(self, instrument_rack, instrument_rack_y):
        # Unbinding from the self.setter('top_prop') callback is not working.
        self.height = instrument_rack.y
        self.top_prop = instrument_rack.y

    def on_mode_filter(self, *args):
        self.update_note_idxs()

    def on_root_note_idx(self, *args):
        self.note_idxs[0] = self.root_note_idx
        self.update_note_idxs()

    def update_note_idxs(self):
        write_idx = 0
        for i, bit in enumerate(bin(self.mode_filter)[2:]):
            if int(bit) == 1:
                note_idx = (self.root_note_idx + i) % 12
                # Modes with more than 7 notes (Melodic Minor) don't work.
                if write_idx < len(self.note_idxs):
                    self.note_idxs[write_idx] = note_idx
                write_idx += 1


class ChordGroup(StencilView, BackGroundColorWidget):
    group_height = NumericProperty(0)
    chord_group = StringProperty('')
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    display = ObjectProperty(None)
    mode_filter = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical', size_hint_x=None)
        with self.box.canvas:
            Color(1, 1, 0, 0.5)
            self.rect = Rectangle(size=self.box.size, pos=self.box.pos)
        self.box.bind(pos=self.update_box_rect, size=self.update_box_rect)
        self.fold_button = Button()
        self.fold_button.bind(on_press=self.fold)
        self.add_widget(self.fold_button)
        self.add_widget(self.box)
        self.bind(pos=self.top_justify, size=self.top_justify)

    def update_box_rect(self, *args):
        self.rect.pos = self.box.pos
        self.rect.size = self.box.size

    def on_kv_post(self, base_widget):
        self.box.children[0].label.bind(width=self.fold_button.setter('width'))

    def on_chord_group(self, *args):
        # Using this as a sort of __init__ method to avoid repetitive classes.
        # self.chord_group is just some text in kv.
        chord_group_list = chord_groups[self.chord_group]
        for chord_name, bin_chord_shape in chord_group_list.items():
            chord_row = ChordRow()
            chord_row.label.text = chord_name
            chord_row.chord_num = bin_chord_shape
            self.bind(note_idxs=chord_row.setter('note_idxs'))
            self.bind(display=chord_row.setter('display'))
            self.bind(mode_filter=chord_row.setter('mode_filter'))
            self.bind(root_note_idx=chord_row.setter('root_note_idx'))
            self.box.add_widget(chord_row)
        # ChordDiagram size being set explicitly. ChordRow width set to sum of its ChordDiagrams.
        # ChordGroup (and ChordGroup.box) should match ChordRow.width. Can't use bindings,
        # because ChordRow.width never actually changes.
        self.box.width = self.width = chord_row.width
        self.group_height = ROW_HEIGHT * len(chord_group_list)
        self.box.height = self.group_height
        self.fold_button.height = self.group_height
        self.fold_button.x = self.box.children[0].ids.label.x if self.box.children else 0
        self.top_justify()

    def fold(self, *args):
        self.height = ROW_HEIGHT if self.height > ROW_HEIGHT else dp(self.group_height)
        self.display.top_justify_all()

    def top_justify(self, *args):
        self.box.top = self.top
        self.fold_button.top = self.top


class ChordTitleBar(BoxLayout):
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chrom_scale = chrom_scale

    def top_justify(self, *args):
        pass


class ChordRow(BoxLayout):
    chord_num = NumericProperty(0b000000000000)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    display = ObjectProperty(None)
    voicings = ListProperty()
    mode_filter = NumericProperty(0)
    root_note_idx = NumericProperty(0)

    label = ObjectProperty(None)

    # def on_display(self, row, display):
    #     # Once display becomes available, look up voicings for this row.
    #     self.voicings = self.display.chords_to_voicings.get(bin(self.chord_num), [])

    def on_chord_num(self, *args):
        self.voicings = get_chord_num_master_voicings(standard_tuning, self.chord_num)


class ChordDisplayApp(App):
    def build(self):
        return ChordDisplay()


if __name__ == "__main__":
    ChordDisplayApp().run()