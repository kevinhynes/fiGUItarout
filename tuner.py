from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ReferenceListProperty, \
    StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock

sub = [u'\u2080', u'\u2081', u'\u2082', u'\u2083', u'\u2084', u'\u2085', u'\u2086', u'\u2087',
       u'\u2088', u'\u2089']
chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale2 = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']


class StringTuner(BoxLayout):
    note_val = NumericProperty(0)
    note_text = StringProperty("")

    def increment_note_val(self):
        self.note_val += 1
        if self.note_val == 84:
            self.note_val = 0

    def decrement_note_val(self):
        self.note_val -= 1
        if self.note_val == -1:
            self.note_val = 83

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y) and touch.is_mouse_scrolling and not touch.is_touch:
            if touch.button == "scrolldown":
                self.increment_note_val()
            elif touch.button == "scrollup":
                self.decrement_note_val()

    def on_note_val(self, instance, value):
        octave, note_idx = divmod(self.note_val, 12)
        note_text = chrom_scale2[note_idx]  # + sub[octave]
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

    def on_tuning(self, instance, value):
        # print("SixStringTuner.on_tuning ", value)
        pass

    def tune_to(self, req="Standard"):
        tunings = {
            "Standard": [28, 33, 38, 43, 47, 52],
            "Drop D": [26, 33, 38, 43, 47, 52],
            "Drop C": [24, 31, 36, 41, 45, 50],
            "Drop B": [23, 30, 35, 40, 44, 49],
        }
        for string_tuner, tuning in zip(self.ids.values(), tunings[req]):
            string_tuner.note_val = tuning

    def tune_to_standard(self, *args):
        standard = [28, 33, 38, 43, 47, 52]
        for string_tuner, tuning in zip(self.ids.values(), standard):
            string_tuner.note_val = tuning

    def tune_up_or_down(self, step):
        for string_tuner in self.ids.values():
            string_tuner.note_val += step


class ControlBar(BoxLayout):
    tuner_ref = ObjectProperty(None)


class Tuner(FloatLayout):
    tuning = ListProperty()
    box_height = NumericProperty(0)
    box_width = NumericProperty(0)

    def on_size(self, instance, value):
        width, height = self.size
        if height > 0:  # Avoid ZeroDivisionError when TabbedPanel.do_default_tab == False.
            target_ratio = 60/20
            # check which size is the limiting factor
            if width / height > target_ratio:
                # window is "wider" than targeted, so the limitation is the height.
                self.ids.box.height = height
                self.ids.box.width = height * target_ratio
            else:
                self.ids.box.width = width
                self.ids.box.height = width / target_ratio
            self.box_height = self.ids.box.height
            self.box_width = self.ids.box.width


class TunerApp(App):
    def build(self):
        return Tuner()


if __name__ == "__main__":
    TunerApp().run()
