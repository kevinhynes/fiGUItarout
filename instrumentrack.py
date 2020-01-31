from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.metrics import dp


class InstrumentRack(ScrollView):
    key_sig_title_bar = ObjectProperty(None)

    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")

    def fold(self, *args):
        if self.height == dp(250):
            self.height = dp(500)
            self.top = self.key_sig_title_bar.y
        else:
            self.height = dp(250)
            self.top = self.key_sig_title_bar.y


class InstrumentDisplayApp(App):
    def build(self):
        return InstrumentRack()


if __name__ == "__main__":
    InstrumentDisplayApp().run()