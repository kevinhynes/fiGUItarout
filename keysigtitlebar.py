from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder


# Builder.load_file("keysigdisplay.kv")

class KeySigTitleBar(BoxLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    key_sig_text = StringProperty("")
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")


class KeySigTitleBarApp(App):
    def build(self):
        return KeySigTitleBar()


if __name__ == "__main__":
    KeySigTitleBarApp().run()