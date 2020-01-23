from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import  Button
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

from music_constants import major_chord_shapes, minor_chord_shapes, \
    dom_chord_shapes, sus_chord_shapes, dim_chord_shapes, aug_chord_shapes

Builder.load_file('chorddiagram.kv')


chord_groups = {
    'Major': major_chord_shapes, 'Minor': minor_chord_shapes,
    'Dominant': dom_chord_shapes, 'Suspended': sus_chord_shapes,
    'Diminished': dim_chord_shapes, 'Augmented': aug_chord_shapes
    }


class BackGroundColorWidget(Widget):
    pass


class ChordRow(BoxLayout):
    pass


class ChordGroup(StencilView, BackGroundColorWidget):
    group_height = NumericProperty(0)
    chord_group = StringProperty('')

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
        chord_list = chord_groups[self.chord_group]
        for chord in chord_list:
            chord_row = ChordRow()
            chord_row.label.text = chord
            self.box.add_widget(chord_row)
        self.group_height = 90 * len(chord_list)
        self.box.height = self.group_height
        self.fold_button.height = self.group_height
        self.fold_button.width = self.box.children[0].ids.label.width if self.box.children else 1
        self.fold_button.x = self.box.children[0].ids.label.x if self.box.children else 0
        self.top_justify()

    def fold(self, *args):
        self.height = dp(90) if self.height > dp(90) else dp(self.group_height)
        self.display.top_justify_all()

    def top_justify(self, *args):
        self.box.width = self.width
        self.box.top = self.top
        self.fold_button.top = self.top


class ChordDisplay(ScrollView):
    def top_justify_all(self):
        for chord_group in self.ids.display_box.children:
            chord_group.top_justify()


class ChordDisplayApp(App):
    def build(self):
        return ChordDisplay()


if __name__ == "__main__":
    ChordDisplayApp().run()