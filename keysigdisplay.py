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

class KeySigDisplay(FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    box_x = NumericProperty(0)
    box_y = NumericProperty(0)
    box_pos = ReferenceListProperty(box_x, box_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_markers = InstructionGroup()

    def update_canvas(self, *args):
        self.redraw_note_markers()

    def redraw_note_markers(self, *args):
        self.note_markers.clear()
        x, y = self.ids.box.pos
        r1 = self.ids.box.height / 2
        r2 = r1 * 0.95
        rdiff = r1 - r2
        mask = 2048
        for i in range(12):
            self.redraw_note_marker(i, x, y, r1, r2, rdiff, mask)
            mask >>= 1
        self.canvas.add(self.note_markers)

    def redraw_note_marker(self, i, x, y, r1, r2, rdiff, mask):
        if self.mode_filter & mask:
            this_color = blues[i]
        else:
            this_color = gray

        # Draw 2 concentric circles, c1 and c2.
        # Circles are defined by a square's lower left corner.
        c1x, c1y = (2*r1)*i + x, y
        c2x, c2y = c1x + rdiff, c1y + rdiff

        self.note_markers.add(white)
        self.note_markers.add(Ellipse(pos=[c1x, c1y], size=[2 * r1, 2 * r1]))
        self.note_markers.add(this_color)
        self.note_markers.add(Ellipse(pos=[c2x, c2y], size=[2 * r2, 2 * r2]))

        note_idx = (self.root_note_idx + i) % 12
        note_text = chrom_scale[note_idx]
        # scale_degree = scale_degrees[i]
        # note_text = scale_degree
        if "/" in note_text:
            # Accidental notes. Add diagonal line.
            a1 = (1 / 2) ** 0.5 * r1  # a1 is side of a 45-45-90 right triangle.
            diff = r1 - a1
            lx1, ly1 = c1x + diff, c1y + diff
            lx2, ly2 = lx1 + 2 * a1, ly1 + 2 * a1
            self.note_markers.add(white)
            self.note_markers.add(Line(points=[lx1, ly1, lx2, ly2], width=1, cap="none"))
            # Add notes text.
            notes = note_text.split("/")
            note1_label = CoreLabel(text=notes[0], font_size=a1,
                                    font_name="./fonts/Lucida Sans Unicode Regular")
            note2_label = CoreLabel(text=notes[1], font_size=a1,
                                    font_name="./fonts/Lucida Sans Unicode Regular")
            note1_label.refresh()
            note2_label.refresh()
            # Locate coords of where to place Rectangle. Affected by font_size, text length...
            bx1, by1 = lx1, ly1 + a1  # Lower left of box 1, aiming to put text here.
            bx2, by2 = lx1 + a1, ly1
            bcx1, bcy1 = bx1 + a1 / 2, by1 + a1 / 2  # Center of box 1.
            bcx2, bcy2 = bx2 + a1 / 2, by2 + a1 / 2
            tw1, th1, = note1_label.texture.size
            tw2, th2 = note2_label.texture.size
            tx1, ty1 = bcx1 - tw1 / 2, bcy1 - th1 / 2  # Lower left of actual text box.  Avoids
            tx2, ty2 = bcx2 - tw2 / 2, bcy2 - th2 / 2  # stretching and centers to correct (x, y).
            note1_instr = Rectangle(pos=[tx1, ty1], texture=note1_label.texture, size=[tw1, th1])
            note2_instr = Rectangle(pos=[tx2, ty2], texture=note2_label.texture, size=[tw2, th2])
            self.note_markers.add(black)
            self.note_markers.add(note1_instr)
            self.note_markers.add(note2_instr)
        else:
            # Natural notes. Add note text.
            # Size of CoreLabel is .size, .texture.size, .content_size. (Why all 3..?)
            # CoreLabel.text_size is bounding box of text, and is (None, None).
            # Height is determined by font_size, width determined by font_size and text length.
            # Set size of Rectangle to match texture.size to avoid stretching text.
            note_label = CoreLabel(text=note_text,
                                   font_size=self.ids.box.height * 10 / 13 * 0.85,
                                   font_name="./fonts/Lucida Sans Unicode Regular")
            note_label.refresh()
            tw, th = note_label.texture.size
            xc_center, yc_center = c1x + r1, c1y + r1
            tx1, ty1 = xc_center - tw / 2, yc_center - th / 2
            note_instr = Rectangle(pos=[tx1, ty1], texture=note_label.texture, size=[tw, th])
            self.note_markers.add(black)
            self.note_markers.add(note_instr)

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
        self.update_canvas(instance, value)

    def on_root_note_idx(self, instance, value):
        self.update_canvas(instance, value)

    def on_mode_filter(self,instance, value):
        self.update_canvas(instance, value)

class KeySigDisplayApp(App):
    def build(self):
        return KeySigDisplay()


if __name__ == "__main__":
    KeySigDisplayApp().run()