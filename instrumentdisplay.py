from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder

Builder.load_file('fretboard.kv')
Builder.load_file('chorddisplay.kv')

from chorddisplay import ChordDisplay


class SlidingChordDisplay(ChordDisplay):
    top_hint = NumericProperty(0)
    display = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_shown = False

    def slide(self, *args):
        if self.display:
            rack = self.display.ids.rack
            if not self.is_shown:
                self.top_hint = rack.y
                # rack.bind(y=self.setter('top_hint'))
                self.is_shown = True
            else:
                # rack.unbind(y=self.setter('top_hint'))
                self.top_hint = 0
                self.is_shown = False


class InstrumentDisplay(FloatLayout):

    def fold(self, *args):
        if self.rack.height == dp(250):
            self.rack.height = dp(500)
        else:
            self.rack.height = dp(250)

    def remove_chord_display(self, *args):
        self.remove_widget(self.ids.chorddisplay)


class InstrumentRack(ScrollView):
    pass


class InstrumentDisplayApp(App):
    def build(self):
        return InstrumentDisplay()


if __name__ == "__main__":
    InstrumentDisplayApp().run()