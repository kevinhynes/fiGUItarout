from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.clock import  Clock
from kivy.metrics import dp
from kivy.lang import Builder

from music_constants import major_chord_shapes, minor_chord_shapes, dom_chord_shapes


class BackGroundColorWidget(Widget):
    pass


class ChordRow(BoxLayout):
    pass


class ChordGroup(StencilView, BackGroundColorWidget):
    group_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical', pos_hint={'center': [0.5, 0.5]})
        self.add_widget(self.box)
        Clock.schedule_once(self.on_pos, 0.1)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.height = dp(90) if self.height > dp(90) else dp(self.group_height)
        self.box.top = self.top

    def on_size(self, *args):
        self.box.width = self.width

    def on_pos(self, *args):
        self.box.top = self.top


class MajorChordGroup(ChordGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for chord in major_chord_shapes:
            chord_row = ChordRow()
            chord_row.label.text = chord
            self.box.add_widget(chord_row)
        self.box.height = 90 * len(major_chord_shapes)
        self.group_height = dp(90 * len(major_chord_shapes))
        self.box.top = self.top


class MinorChordGroup(ChordGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for chord in minor_chord_shapes:
            chord_row = ChordRow()
            chord_row.label.text = chord
            self.box.add_widget(chord_row)
        self.box.height = 90 * len(minor_chord_shapes)
        self.group_height = dp(90 * len(minor_chord_shapes))
        self.box.top = self.top


class DominantChordGroup(ChordGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for chord in dom_chord_shapes:
            chord_row = ChordRow()
            chord_row.label.text = chord
            self.box.add_widget(chord_row)
        self.box.height = 90 * len(dom_chord_shapes)
        self.group_height = dp(90 * len(dom_chord_shapes))
        self.box.top = self.top

class ChordDisplay(FloatLayout):
    pass


class ChordDisplayApp(App):
    def build(self):
        return ChordDisplay()


if __name__ == "__main__":
    ChordDisplayApp().run()