from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.lang import Builder

from music_constants import chrom_scale

Builder.load_file('chorddiagram.kv')


class BackGroundColorWidget(Widget):
    pass


class ChordPalette(ScrollView):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    box = ObjectProperty(None)


class ChordPaletteRow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(kwargs)



class ChordPaletteApp(App):
    def build(self):
        return ChordPalette()


if __name__ == "__main__":
    ChordPaletteApp().run()