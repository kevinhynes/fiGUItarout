from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty


class FretboardDisplay(BoxLayout):
    tuning = ListProperty([0, 0, 0, 0, 0, 0])
    num_frets = NumericProperty(24)
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    key_sig_text = StringProperty("")
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")


class FretboardDisplayApp(App):
    def build(self):
        return FretboardDisplay()


if __name__ == "__main__":
    FretboardDisplayApp().run()