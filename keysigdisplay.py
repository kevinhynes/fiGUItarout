from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import InstructionGroup, Rectangle, Ellipse, Line, Color
from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.animation import Animation


from markers import Marker

flat = u'\u266D'
sharp = u'\u266F'
chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale_no_acc = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']
scale_degrees = ["1", "♭2", "2", "♭3", "3", "4", "♯4/♭5", "5", "♯5/♭6", "6", "♭7", "7"]

scale_texts = {
    "": chrom_scale,
    "Notes": chrom_scale,
    "Notes - No Accidentals": chrom_scale_no_acc,
    "Scale Degrees": scale_degrees}

black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)
gray = Color(0.5, 0.5, 0.5, 1)

rainbow = [Color(hsv=[i/12, 1, 0.95]) for i in range(12)]
reds = [Color(hsv=[0, i/12, 1]) for i in range(12)][::-1]
blues = [Color(hsv=[0.6, i/12, 1]) for i in range(12)][::-1]


class KeySigDisplay(FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    box_x = NumericProperty(0)
    box_y = NumericProperty(0)
    box_pos = ReferenceListProperty(box_x, box_y)
    scale_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_markers = InstructionGroup()
        self._add_markers()
        self.canvas.add(self.note_markers)

    def _add_markers(self):
        for i in range(12):
            self.note_markers.add(Marker())

    def update_markers(self):
        x, y = self.ids.box.pos
        w, h = self.ids.box.size
        r1 = h / 2
        r2 = r1 * 0.9
        rdiff = r1 - r2
        mask = 2048
        for i, marker in enumerate(self.note_markers.children):
            c1x, c1y = x + w / 12 * i, y
            c2x, c2y = c1x + rdiff, c1y + rdiff
            included = mask & self.mode_filter
            mask >>= 1
            if self.scale_text == "Scale Degrees":
                note_idx = i
            else:
                note_idx = (self.root_note_idx + i) % 12

            note_text = scale_texts[self.scale_text][note_idx]

            color_idx = i
            marker.update(i, note_text, color_idx, c1x, c1y, r1, c2x, c2y, r2, included)

    def on_size(self, instance, value):
        width, height = self.size
        target_ratio = 12
        if width / height > target_ratio:
            self.ids.box.height = height
            self.ids.box.width = height * target_ratio
        else:
            self.ids.box.width = width
            self.ids.box.height = width / target_ratio

    def on_box_pos(self, instance, value):
        self.update_markers()

    def on_root_note_idx(self, instance, value):
        self.update_markers()

    def on_mode_filter(self, instance, value):
        self.update_markers()

    def on_scale_text(self, *args):
        self.update_markers()


class KeySigDisplayApp(App):
    def build(self):
        return KeySigDisplay()


if __name__ == "__main__":
    KeySigDisplayApp().run()