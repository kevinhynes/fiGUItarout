from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.lang import Builder


# Builder.load_file("keysigdisplay.kv")

class KeySigTitleBar(BoxLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0)
    key_sig_text = StringProperty("")
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")
    key_sig_display = ObjectProperty()

    def prep_play(self, flat_song, track_num=0, tempo_mult=1):
        self.key_sig_display.prep_play(flat_song, track_num, tempo_mult)

    def play(self, lead_in):
        self.key_sig_display.play_thread(lead_in)

    def stop(self):
        self.key_sig_display.stop()

class KeySigTitleBarApp(App):
    def build(self):
        return KeySigTitleBar()


if __name__ == "__main__":
    KeySigTitleBarApp().run()