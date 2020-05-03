from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.label import CoreLabel
# from kivy.core.text import Label as CoreLabel

from music_constants import chrom_scale, chrom_scale_no_acc


mode_filters = {
    "Chromatic": 0b111111111111,

    "Major": 0b101011010101,  # Ionian
    "Dorian": 0b101101010110,
    "Phrygian": 0b110101011010,
    "Lydian": 0b101010110101,
    "Mixolydian": 0b101011010110,
    "Minor": 0b101101011010,  # Aeolian
    "Locrian": 0b110101101010,

    "Melodic Minor": 0b101111010111,
    "Melodic Minor Ascending": 0b101101010101,
    "Melodic Minor Descending": 0b101011010110,
    "Harmonic Minor": 0b101101011001,

    "Major Pentatonic": 0b101010010100,
    "Minor Pentatonic": 0b100101010010,
}

mode_groups = {
    "All": [filter for filter in mode_filters],
    "Modern": ["Major", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Minor", "Locrian"],
    "Pentatonic": ["Major Pentatonic", "Minor Pentatonic"],
    "Minor": ["Minor", "Melodic Minor", "Melodic Minor Ascending", "Melodic Minor Descending",
              "Harmonic Minor"]
}


class RootNoteChooser(BoxLayout):
    root_note_idx = NumericProperty(0)

    def increment_root_note_idx(self):
        self.root_note_idx = (self.root_note_idx + 1) % 12

    def decrement_root_note_idx(self):
        self.root_note_idx = (self.root_note_idx - 1) % 12

    def on_root_note_idx(self, instance, value):
        self.spinner.text = chrom_scale[self.root_note_idx]

    def on_new_root_note_chosen(self, root_note):
        self.root_note_idx = chrom_scale.index(root_note)


class ModeChooser(BoxLayout):
    mode_group = StringProperty("")  # key to mode_groups dict.
    group_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)

    def on_group_idx(self, instance, value):
        self.mode_text = mode_groups[self.mode_group][self.group_idx]
        self.spinner.text = self.mode_text
        self.mode_filter = mode_filters[self.mode_text]

    def increment_group_idx(self):
        self.group_idx = (self.group_idx + 1) % len(mode_groups[self.mode_group])

    def decrement_group_idx(self):
        self.group_idx = (self.group_idx - 1) % len(mode_groups[self.mode_group])

    def on_mode_group(self, instance, value):
        self.spinner.values = mode_groups[self.mode_group]
        if self.group_idx == 0:
            self.on_group_idx(instance, value)
        self.group_idx = 0

    def on_new_mode_chosen(self, mode):
        self.group_idx = mode_groups[self.mode_group].index(mode)


class KeySigChooser(FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    key_sig_text = StringProperty("")

    top_prop = NumericProperty(0)

    def on_size(self, instance, value):
        width, height = self.size
        if height > 0:  # Avoid ZeroDivisionError when TabbedPanel.do_default_tab == False.
            target_ratio = 100/15
            # check which size is the limiting factor
            if width / height > target_ratio:
                # window is "wider" than targeted, so the limitation is the height.
                self.ids.box.height = height
                self.ids.box.width = height * target_ratio
            else:
                self.ids.box.width = width
                self.ids.box.height = width / target_ratio
        self.size = self.ids.box.size

    def slide(self, state):
        if state == 'down' and self.top == 0:
            self.top_prop = 150
        else:
            self.top_prop = 0


class KeySigChooserApp(App):
    def build(self):
        return KeySigChooser()


if __name__ == "__main__":
    KeySigChooserApp().run()