from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock

from music_constants import chrom_scale, standard_tuning

# Builder.load_file('chorddiagram.kv')
from chorddiagram import ChordDiagram


class BackGroundColorWidget(Widget):
    pass


class ChordPalette(ScrollView, BackGroundColorWidget):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    tuning = ListProperty(standard_tuning)
    box = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.titlebar = ChordPaletteTitleBar()
        self.box.add_widget(self.titlebar)
        self.bind(root_note_idx=self.update_note_idxs, mode_filter=self.update_note_idxs)
        Clock.schedule_once(self.update_note_idxs, 0)

    def update_note_idxs(self, *args):
        self.note_idxs = []
        mode_str = bin(self.mode_filter)[2:]
        for i, bit in enumerate(mode_str):
            if bit == '1':
                note_idx = (self.root_note_idx + i) % 12
                self.note_idxs.append(note_idx)
        print(len(self.note_idxs), self.note_idxs)
        self.titlebar.update(self.note_idxs)

    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.x, touch.y):
    #         if self.mode_filter == 0b101011010101:
    #             self.mode_filter = 0b101010010100
    #         else:
    #             self.mode_filter = 0b101011010101
    #         # self.root_note_idx += 1
    #         return True
    #     return super().on_touch_down(touch)

    def add_row(self, *args):
        chord_row = ChordPaletteRow(width=self.titlebar.width)
        for child in self.titlebar.children:
            chord_row.add_widget(ChordDiagram(root_note_idx=self.root_note_idx,
                                              mode_filter=self.mode_filter))
        self.box.height += chord_row.height
        self.box.add_widget(chord_row)


class ChordPaletteTitleBar(BoxLayout, BackGroundColorWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, note_idxs):
        # Number of columns in title bar may change.
        # Children of BoxLayout are displayed right to left.
        child_count = len(note_idxs) + 1
        while len(self.children) > child_count:
            self.remove_widget(self.children[0])
        while len(self.children) < child_count:
            self.add_widget(Label())
        for label, note_idx in zip(reversed(self.children[:-1]), note_idxs):
            label.text = chrom_scale[note_idx]
        self.children[-1].text = "Chord Palette"


class ChordPaletteRow(BoxLayout, BackGroundColorWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChordPaletteApp(App):
    def build(self):
        float = FloatLayout()
        chord_palette = ChordPalette()
        btn = Button(size_hint=[None, None], size=[100, 50], text="Add Row")
        btn.bind(on_press=chord_palette.add_row)
        float.add_widget(chord_palette)
        float.add_widget(btn)
        return float


if __name__ == "__main__":
    ChordPaletteApp().run()
