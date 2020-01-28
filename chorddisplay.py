from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, \
    DictProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

import json

from music_constants import major_chord_shapes, minor_chord_shapes, \
    dom_chord_shapes, sus_chord_shapes, dim_chord_shapes, aug_chord_shapes, \
    chrom_scale, standard_tuning

Builder.load_file('chorddiagram.kv')

chord_groups = {
    'Major': major_chord_shapes, 'Minor': minor_chord_shapes,
    'Dominant': dom_chord_shapes, 'Suspended': sus_chord_shapes,
    'Diminished': dim_chord_shapes, 'Augmented': aug_chord_shapes
    }

ROW_HEIGHT = dp(95)


class BackGroundColorWidget(Widget):
    pass


class ChordTitleBar(BoxLayout):
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chrom_scale = chrom_scale

    def top_justify(self, *args):
        pass


class ChordRow(BoxLayout):
    bin_chord_shape = NumericProperty(0b000000000000)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    display = ObjectProperty(None)
    voicings = ListProperty()
    mode_filter = NumericProperty(0)
    root_note_idx = NumericProperty(0)

    def on_display(self, row, display):
        # Once display becomes available, look up voicings for this row.
        self.voicings = self.display.chords_to_voicings.get(bin(self.bin_chord_shape), [])


class ChordGroup(StencilView, BackGroundColorWidget):
    group_height = NumericProperty(0)
    chord_group = StringProperty('')
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    display = ObjectProperty(None)
    mode_filter = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.fold_button = Button(background_normal='',
                                  background_down='',
                                  background_color=(0, 0, 0, 0))
        self.fold_button.bind(on_press=self.fold)
        self.add_widget(self.fold_button)
        self.add_widget(self.box)
        self.bind(pos=self.top_justify, size=self.top_justify)
        Clock.schedule_once(self.top_justify, 0.1)  # no text in some groups initially without this

    def on_chord_group(self, *args):
        # Using this as a sort of __init__ method to avoid repetitive classes.
        # self.chord_group is just some text in kv.
        chord_group_list = chord_groups[self.chord_group]
        for chord_name, bin_chord_shape in chord_group_list.items():
            chord_row = ChordRow()
            chord_row.label.text = chord_name
            chord_row.bin_chord_shape = bin_chord_shape
            self.bind(note_idxs=chord_row.setter('note_idxs'))
            self.bind(display=chord_row.setter('display'))
            self.bind(mode_filter=chord_row.setter('mode_filter'))
            self.bind(root_note_idx=chord_row.setter('root_note_idx'))
            self.box.add_widget(chord_row)
        self.group_height = ROW_HEIGHT * len(chord_group_list)
        self.box.height = self.group_height
        self.fold_button.height = self.group_height
        self.fold_button.width = self.box.children[0].ids.label.width if self.box.children else 100
        self.fold_button.x = self.box.children[0].ids.label.x if self.box.children else 0
        self.top_justify()

    def fold(self, *args):
        self.height = ROW_HEIGHT if self.height > ROW_HEIGHT else dp(self.group_height)
        self.display.top_justify_all()

    def top_justify(self, *args):
        self.box.width = self.width
        self.box.top = self.top
        self.fold_button.width = self.box.children[0].ids.label.width if self.box.children else 100
        self.fold_button.top = self.top


class ChordDisplay(ScrollView, FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])

    def __init__(self, **kwargs):
        with open('chord_voicings_by_tuning.json') as read_file:
            chord_voicings_by_tuning = json.load(read_file)
        self.chords_to_voicings = chord_voicings_by_tuning[str(standard_tuning)]
        super().__init__(**kwargs)

    def top_justify_all(self):
        for chord_group in self.ids.display_box.children:
            chord_group.top_justify()

    def on_mode_filter(self, *args):
        write_idx = 0
        for i, bit in enumerate(bin(self.mode_filter)[2:]):
            if int(bit) == 1:
                note_idx = (self.root_note_idx + i) % 12
                if write_idx < len(self.note_idxs):
                    self.note_idxs[write_idx] = note_idx
                write_idx += 1

    def on_root_note_idx(self, *args):
        self.note_idxs[0] = self.root_note_idx
        self.on_mode_filter()
        # prev_root_note_idx = self.note_idxs[0]
        # diff = self.root_note_idx - prev_root_note_idx
        # self.note_idxs = [(note_idx + diff) % 12 for note_idx in self.note_idxs]

class ChordDisplayApp(App):
    def build(self):
        return ChordDisplay()


if __name__ == "__main__":
    ChordDisplayApp().run()