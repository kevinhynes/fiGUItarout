from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import InstructionGroup, Rectangle, Ellipse, Line, Color
from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty, ReferenceListProperty


flat = u'\u266D'
sharp = u'\u266F'
chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale2 = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']
scale_degrees = ["1", "♭2", "2", "♭3", "3", "4", "♯4/♭5", "5", "♯5/♭6", "6", "♭7", "7"]

black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)
gray = Color(0.5, 0.5, 0.5, 1)

rainbow = [Color(hsv=[i/12, 1, 0.95]) for i in range(12)]
reds = [Color(hsv=[0, i/12, 1]) for i in range(12)][::-1]
blues = [Color(hsv=[0.6, i/12, 1]) for i in range(12)][::-1]


class Marker(InstructionGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Color()
        self.background = Ellipse()
        self.marker_color = Color()
        self.marker = Ellipse()
        self.split_line_color = Color()
        self.split_line = Line(width=1, cap="none")
        self.text1_color = Color()
        self.text1_label = CoreLabel()
        self.text1_instr = Rectangle()
        self.text2_color = Color()
        self.text2_label = CoreLabel(font_name="./fonts/Lucida Sans Unicode Regular")
        self.text2_instr = Rectangle()
        self.background_color.hsv = white.hsv
        self.split_line_color.hsv = white.hsv
        self.text1_color.hsv = black.hsv
        self.text2_color.hsv = black.hsv

        self.add(self.background_color)
        self.add(self.background)
        self.add(self.marker_color)
        self.add(self.marker)
        self.add(self.split_line_color)
        self.add(self.split_line)
        self.add(self.text1_color)
        self.add(self.text1_instr)
        self.add(self.text2_color)
        self.add(self.text2_instr)

    def update(self, i, root_note_idx, c1x, c1y, r1, c2x, c2y, r2, included):
        self.background.size = [2*r1, 2*r1]
        self.background.pos = [c1x, c1y]
        self.marker.size = [2*r2, 2*r2]
        self.marker.pos = [c2x, c2y]

        if included:
            self.background_color.a = 1
            self.marker_color.hsv = rainbow[i].hsv
            self.marker_color.a = 1
            self.update_text(i, root_note_idx, c1x, c1y, r1)
        else:
            self.background_color.a = 0
            self.marker_color.a = 0
            self.split_line_color.a = 0
            self.text1_color.a = 0
            self.text2_color.a = 0

    def update_text(self, i, root_note_idx, c1x, c1y, r1):
        note_idx = (root_note_idx + i) % 12
        note_text = chrom_scale[note_idx]
        scale_degree = scale_degrees[i]
        note_text = scale_degree
        if "/" in note_text:
            # Accidental notes. Add diagonal line.
            a1 = (1 / 2) ** 0.5 * r1  # a1 is side of a 45-45-90 right triangle.
            diff = r1 - a1
            lx1, ly1 = c1x + diff, c1y + diff
            lx2, ly2 = lx1 + 2 * a1, ly1 + 2 * a1
            self.split_line_color.a = 1
            self.split_line.points = [lx1, ly1, lx2, ly2]

            # Add notes text. Need to remake CoreLabels every time.. inefficient.
            # Size of CoreLabel is .size, .texture.size, .content_size. (Why all 3..?)
            # CoreLabel.text_size is bounding box of text, and is (None, None).
            # Height is determined by font_size, width determined by font_size and text length.
            # Set size of Rectangle to match texture.size to avoid stretching text.
            notes = note_text.split("/")
            self.text1_label = CoreLabel(font_size=a1,
                                         text=notes[0],
                                         font_name="./fonts/Lucida Sans Unicode Regular")
            self.text2_label = CoreLabel(font_size=a1,
                                         text=notes[1],
                                         font_name="./fonts/Lucida Sans Unicode Regular")
            self.text1_label.refresh()
            self.text2_label.refresh()

            # Locate coords of where to place Rectangle. Affected by font_size, text length...
            b1x, b1y = lx1, ly1 + a1  # Lower left of box 1, aiming to put text here.
            b2x, b2y = lx1 + a1, ly1
            b1cx, b1cy = b1x + a1 / 2, b1y + a1 / 2  # Center of box 1.
            b2cx, b2cy = b2x + a1 / 2, b2y + a1 / 2
            t1w, t1h = self.text1_label.texture.size
            t2w, t2h = self.text2_label.texture.size
            t1x, t1y = b1cx - t1w / 2, b1cy - t1h / 2  # Lower left of actual text box.  Avoids
            t2x, t2y = b2cx - t2w / 2, b2cy - t2h / 2  # stretching and centers to correct (x, y).

            # Update graphics instructions.
            self.text1_color.a = 1
            self.text1_instr.pos = [t1x, t1y]
            self.text1_instr.size = [t1w, t1h]
            self.text1_instr.texture = self.text1_label.texture
            self.text2_color.a = 1
            self.text2_instr.pos = [t2x, t2y]
            self.text2_instr.size = [t2w, t2h]
            self.text2_instr.texture = self.text2_label.texture
        else:
            # Natural notes. Add note text.
            self.text1_label = CoreLabel(font_size=r1,
                                         text=note_text,
                                         font_name="./fonts/Lucida Sans Unicode Regular")
            self.text1_label.refresh()

            # Locate coords of the Rectangle.
            tw, th = self.text1_label.texture.size
            b1xc, b1yc = c1x + r1, c1y + r1
            t1x, t1y = b1xc - tw / 2, b1yc - th / 2

            self.text1_color.a = 1
            self.text1_instr.pos = [t1x, t1y]
            self.text1_instr.size = [tw, th]
            self.text1_instr.texture = self.text1_label.texture
            # Move text box 2's graphics instructions, but make it clear.
            self.text2_color.a = 0
            self.text2_instr.pos = [t1x, t1y]
            self.text2_instr.size = [tw, th]


class KeySigDisplay(FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    box_x = NumericProperty(0)
    box_y = NumericProperty(0)
    box_pos = ReferenceListProperty(box_x, box_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_markers = InstructionGroup()
        self.add_markers()
        self.canvas.add(self.note_markers)

    def add_markers(self):
        for i in range(12):
            marker = Marker()
            self.note_markers.add(marker)

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
            marker.update(i, self.root_note_idx, c1x, c1y, r1, c2x, c2y, r2, included)

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


class KeySigDisplayApp(App):
    def build(self):
        return KeySigDisplay()


if __name__ == "__main__":
    KeySigDisplayApp().run()