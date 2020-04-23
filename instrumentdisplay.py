from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder

Builder.load_file('fretboard.kv')
Builder.load_file('chorddisplay.kv')

from chorddisplay import ChordDisplay


class SlidingChordDisplay(ChordDisplay):
    top_prop = NumericProperty(0)
    display = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_shown = False

    def slide(self, *args):
        if self.display:
            rack = self.display.ids.rack
            if not self.is_shown:
                self.height = rack.y  # Change the size,
                self.top_prop = rack.y  # before changing the position.
                rack.bind(y=self.top_prop_setter)
                self.is_shown = True
            else:
                rack.unbind(y=self.top_prop_setter)
                self.top_prop = 0
                self.is_shown = False

    def top_prop_setter(self, rack, rack_y):
        self.height = rack.y
        self.top_prop = rack_y


class InstrumentRack(ScrollView):
    fretboard = ObjectProperty()
    piano = ObjectProperty()

    def fold(self, *args):
        if self.height == dp(250):
            self.height = dp(500)
        else:
            self.height = dp(250)


class InstrumentDisplay(FloatLayout):
    pass


class InstrumentDisplayApp(App):
    def build(self):
        return InstrumentDisplay()


if __name__ == "__main__":
    InstrumentDisplayApp().run()