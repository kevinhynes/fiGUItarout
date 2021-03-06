from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ReferenceListProperty, \
    StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock

from music_constants import chrom_scale, chrom_scale_no_acc
subscripts = subs = [u'\u208B'+u'\u2081', u'\u2080', u'\u2081', u'\u2082', u'\u2083',
                     u'\u2084', u'\u2085', u'\u2086', u'\u2087', u'\u2088', u'\u2089']


class StringTuner(BoxLayout):
    note_val = NumericProperty(0)
    note_text = StringProperty("")

    def tune_up_or_down(self, step):
        # Keep all note_vals between [0 - 107] on 24 fret guitar.
        if 0 <= self.note_val + step < 107 - 25:
            self.note_val += step

    def on_note_val(self, instance, value):
        octave, note_idx = divmod(self.note_val, 12)
        note_text = chrom_scale_no_acc[note_idx] + subs[octave]
        self.note_text = note_text


class SixStringTuner(BoxLayout):
    s1 = NumericProperty(0)
    s2 = NumericProperty(0)
    s3 = NumericProperty(0)
    s4 = NumericProperty(0)
    s5 = NumericProperty(0)
    s6 = NumericProperty(0)
    tuning = ReferenceListProperty(s1, s2, s3, s4, s5, s6)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.tune_to_standard)

    def tune_to(self, req="Standard"):
        # tunings = {
        #     "Standard": [28, 33, 38, 43, 47, 52],  # E-A-D-G-B-E
        #     "Drop D": [26, 33, 38, 43, 47, 52],
        #     "Drop C": [24, 31, 36, 41, 45, 50],
        #     "Drop B": [23, 30, 35, 40, 44, 49],
        #     "Open G": [26, 31, 38, 43, 47, 50],  # D-G-D-G-B-D
        # }
        tunings = {
            "Standard": [40, 45, 50, 55, 59, 64],  # E-A-D-G-B-E
            "Drop D": [38, 45, 50, 55, 59, 64],
            "Drop C": [36, 43, 48, 53, 57, 62],
            "Drop B": [35, 42, 47, 52, 56, 61],
            "Open G": [38, 43, 50, 55, 59, 62],  # D-G-D-G-B-D
        }

        for string_tuner, tuning in zip(self.ids.values(), tunings[req]):
            string_tuner.note_val = tuning

    def tune_to_standard(self, *args):
        standard = [40, 45, 50, 55, 59, 64]
        for string_tuner, tuning in zip(self.ids.values(), standard):
            string_tuner.note_val = tuning

    def tune_up_or_down(self, step):
        for string_tuner in self.ids.values():
            string_tuner.tune_up_or_down(step)


class ControlBar(BoxLayout):
    tuner_ref = ObjectProperty(None)


class Tuner(FloatLayout):
    tuning = ListProperty()
    box_height = NumericProperty(0)
    box_width = NumericProperty(0)
    top_prop = NumericProperty(0)

    def on_size(self, instance, value):
        width, height = self.size
        target_ratio = 60/20
        if width / height > target_ratio:
            # window is "wider" than targeted, so the limitation is the height.
            self.ids.box.height = height
            self.ids.box.width = height * target_ratio
        else:
            self.ids.box.width = width
            self.ids.box.height = width / target_ratio
        self.size = self.ids.box.size

    def slide(self, state):
        if state == 'down' and self.top_prop == 0:
            self.top_prop = self.height + 50
        else:
            self.top_prop = 0


class TunerApp(App):
    def build(self):
        return Tuner()


if __name__ == "__main__":
    TunerApp().run()
