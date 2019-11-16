from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import InstructionGroup, Rectangle, Ellipse, Line, Color, Quad
# from kivy.uix.label import CoreLabel
from kivy.core.text import Label as CoreLabel

chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale2 = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']
octave_alpha = 0.8
octave_colors = [[255/255, 180/255, 52/255, octave_alpha],  # orange
                 [255/255, 251/255, 52/255, octave_alpha],  # yellow
                 [83/255, 180/255, 52/255, octave_alpha],   # green
                 [52/255, 255/255, 249/255, octave_alpha],  # blue
                 [255/255, 52/255, 243/255, octave_alpha]]  # purple

black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)
gray = Color(0.5, 0.5, 0.5, 1)

rainbow = [Color(hsv=[i/12, 1, 0.95]) for i in range(12)]
reds = [Color(hsv=[0, i/12, 1]) for i in range(12)][::-1]
blues = [Color(hsv=[0.6, i/12, 1]) for i in range(12)][::-1]

class String(RelativeLayout):
    open_note_val = NumericProperty(0)
    num_frets = NumericProperty(12)
    fret_positions = ListProperty()
    note_vals = ListProperty()
    mode_filter = NumericProperty(0b111111111111)
    root_note_idx = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.string_graphic = InstructionGroup()
        self.note_markers = InstructionGroup()
        self.octave_markers = InstructionGroup()
        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def on_open_note_val(self, instance, value):
        self.note_vals = [val for val in range(self.open_note_val, self.open_note_val+self.num_frets+1)]
        self.update_canvas(instance, value)

    def on_num_frets(self, instance, value):
        self.note_vals = [val for val in range(self.open_note_val, self.open_note_val+self.num_frets+1)]
        self.update_canvas(instance, value)

    def on_root_note_idx(self, instance, value):
        self.update_canvas(instance, value)

    def on_mode_filter(self, instance, value):
        self.update_canvas(instance, value)

    def update_canvas(self, *args):
        if self.fret_positions:  # self.fret_positions is empty during instantiation.
            # self.redraw_octave_markers()
            self.redraw_string()
            self.redraw_note_markers()

    def redraw_string(self):
        self.canvas.remove(self.string_graphic)  # Shadow gets darker with calls to on_size. Why?
        self.string_graphic.clear()
        w, h = self.width, self.height * 0.1
        y = (self.height / 2) - h / 2
        # Shadow effect.
        shadow_height = 3 * h
        self.string_graphic.add(Color(rgba=[0/255, 0/255, 0/255, 0.25]))
        self.string_graphic.add(Rectangle(size=[w, shadow_height], pos=[0, y-shadow_height]))
        # String.
        self.string_graphic.add(Color(rgba=[169/255, 169/255, 169/255, 1]))
        self.string_graphic.add(Rectangle(size=[w, h], pos=[0, y]))
        self.canvas.add(self.string_graphic)

    def redraw_note_markers(self, *args):
        self.note_markers.clear()
        x, y = self.pos
        r1 = self.height / 2
        r2 = r1 * 0.95
        rdiff = r1 - r2
        for i, note_val in enumerate(self.note_vals):
            self.redraw_note_marker(i, note_val, r1, r2, rdiff)
        self.canvas.add(self.note_markers)

    def redraw_note_marker(self, i, note_val, r1, r2, rdiff):
        octave, note_idx = divmod(note_val, 12)
        mask = int(bin(self.mode_filter)[2:][note_idx-self.root_note_idx])
        if mask:
            this_color = blues[note_idx-self.root_note_idx]
        elif i == 0:
            this_color = gray
        else:
            return

        # Make right edge of circle touch left edge of fret bar (where your finger should go!)
        fret_left = self.fret_positions[i] * self.width - (self.fretboard.fret_bar_width / 2)

        # Draw 2 concentric circles, c1 and c2.
        # Circles are defined by a square's lower left corner.
        c1x, c1y = fret_left - 2 * r1, 0
        c2x, c2y = c1x + rdiff, c1y + rdiff

        self.note_markers.add(white)
        self.note_markers.add(Ellipse(pos=[c1x, c1y], size=[2 * r1, 2 * r1]))
        self.note_markers.add(this_color)
        self.note_markers.add(Ellipse(pos=[c2x, c2y], size=[2 * r2, 2 * r2]))

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
            note1_label = CoreLabel(text=notes[0], font_size=a1, font_name="l_10646")
            note2_label = CoreLabel(text=notes[1], font_size=a1, font_name="l_10646")
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
                                   font_name="l_10646",
                                   font_size=self.height * 10 / 13 * 0.85)
            note_label.refresh()
            tw, th = note_label.texture.size
            xc_center, yc_center = c1x + r1, c1y + r1
            tx1, ty1 = xc_center - tw / 2, yc_center - th / 2
            note_instr = Rectangle(pos=[tx1, ty1], texture=note_label.texture, size=[tw, th])
            self.note_markers.add(black)
            self.note_markers.add(note_instr)

    def redraw_octave_markers(self):
        # print("String.redraw_octave_markers", self.note_vals)
        self.octave_markers.clear()
        for i, note_val in enumerate(self.note_vals):
            self.redraw_octave_marker(i, note_val)
        self.canvas.add(self.octave_markers)

    def redraw_octave_marker(self, i, note_val):
        # print("String.redraw_octave_marker")
        if self.fret_ranges:
            octave = (note_val - self.fretboard.root_note_idx) // 12
            octave -= 2  # second musical octave is 0th on guitar... sloopy
            color = Color(*octave_colors[octave])
            left, right = self.fret_ranges[i]
            width = right - left
            self.octave_markers.add(color)
            self.octave_markers.add(Rectangle(pos=[left, 0], size=[width, self.height]))


class Fretboard(RelativeLayout):
    num_frets = NumericProperty(24)
    tuning = ListProperty([28, 33, 38, 43, 47, 52])
    fret_ranges = ListProperty()
    fret_positions = ListProperty()
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fret_bar_width = self.width * (0.1 / 24.75)
        self.fret_positions = self.calc_fret_positions()
        self.fret_pos_midpoints = self.calc_fret_pos_midpoints()
        self.actual_fret_positions = self.calc_actual_fret_positions(self)
        self.fret_ranges = self.calc_fret_ranges(self)
        self.fingerboard = InstructionGroup()
        self.fret_bars = InstructionGroup()
        self.inlays = InstructionGroup()
        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def calc_fret_positions(self):
        '''Calculate relative position of frets on the fretboard, where full length of fretboard
        is from [0,1].'''
        # Ratio of fret[i]/fret[i+1] for 12-tone equal temperament.
        temperament = 2 ** (1 / 12)

        # All fret_pos in fret_positions represent % of guitar string; 12th fret_pos == 0.5.
        # All fret_pos in range [0, 0.75] for 24 fret guitar.
        fret_positions = [1 - (1 / (temperament ** fret_num)) for fret_num in range(self.num_frets+1)]

        # Stretch fret_positions to represent % of fretboard instead.
        # All fret_pos now in range [0, 1].
        fret_positions = [fret_pos / fret_positions[-1] for fret_pos in fret_positions]

        # Tricky: 0th fret cannot occur at 0; need room to its left to display note info.
        # Move 0th fret up for nut and scale remaining appropriately.
        # All fret_pos now in range [nut_width_ratio, 1].
        nut_width_ratio = 0.03
        fret_positions = [((1-nut_width_ratio) * fret_pos) + nut_width_ratio for fret_pos in fret_positions]
        self.fret_positions = fret_positions
        return self.fret_positions

    def calc_fret_pos_midpoints(self):
        '''Calculate relative position of the midpoint between frets from [0,1] to use for
        positioning inlays.'''
        fret_pos_midpoints = []
        left_fret = 0
        for right_fret in self.fret_positions:
            mid = (left_fret + right_fret) / 2
            fret_pos_midpoints.append(mid)
            left_fret = right_fret
        self.fret_pos_midpoints = fret_pos_midpoints
        return self.fret_pos_midpoints

    def update_canvas(self, *args):
        '''Resize the BoxLayout that holds the fretboard so it maintains a guitar neck
        aspect ratio.'''
        box = self.ids.box
        target_ratio = 10
        width, height = self.size
        # Check which size is the limiting factor.
        if width / height > target_ratio:
            # Window is "wider" than target, so the limitation is the height.
            box.height = height
            box.width = height * target_ratio
            box.x = (width / 2) - (box.width / 2)
        else:
            box.width = width
            box.height = width / target_ratio
            box.y = (height / 2) - (box.height / 2)

        # With box now resized, recalculate & redraw everything. Having trouble drawing things
        # in order using mixture of python and kv lang. Order is explicit here.
        self.calc_actual_fret_positions(box)
        self.calc_fret_ranges(box)
        self.redraw_fingerboard(box)
        self.redraw_fret_bars(box)
        self.redraw_inlays(box)

    def calc_actual_fret_positions(self, box):
        '''Calculate locations of each fret based on fretboards current width.'''
        self.actual_fret_positions = [fret_pos * box.width + box.x for fret_pos in self.fret_positions]
        return self.actual_fret_positions

    def calc_fret_ranges(self, box):
        '''Calculate x positions of fretboard between frets for use in displaying octaves.'''
        # Gibson ratio of fret bar width to scale length.
        self.fret_bar_width = box.width * (0.1 / 24.75)
        cur_right = box.x
        fret_ranges = []
        for fret_pos in self.actual_fret_positions:
            next_left = fret_pos - (self.fret_bar_width / 2)
            fret_ranges.append((cur_right, next_left))
            cur_right = (next_left + self.fret_bar_width)
        # print("Fretboard.calc_fret_ranges ", fret_ranges)
        self.fret_ranges = fret_ranges
        return self.fret_ranges

    def redraw_fingerboard(self, box):
        self.fingerboard.clear()
        self.fingerboard.add(Color(rgba=[114/255, 69/255, 16/255, 1]))
        ## If making fingerboard trapezoidal shape:
        # w, h = box.width, box.height
        # nut_width, heel_width = h, h * (50/43)  # This ratio defines neck shape.
        # diff = (heel_width - nut_width) / 2
        # bl = x1, y1 = box.pos
        # tl = (x1, y1 + h)
        # br, tr = (w, y1 - diff), (w, y1 + h + diff)
        # q = Quad(points=[*bl, *tl, *tr, *br])
        # self.fingerboard.add(q)
        self.fingerboard.add(Rectangle(size=box.size, pos=box.pos))
        self.canvas.before.add(self.fingerboard)

    def redraw_fret_bars(self, box):
        self.fret_bars.clear()
        self.fret_bars.add(Color(0, 0, 0, 1))
        for fret_pos in self.actual_fret_positions:
            x_pos = fret_pos - (self.fret_bar_width / 2)
            self.fret_bars.add(
                Rectangle(size=[self.fret_bar_width, box.height], pos=[x_pos, box.y]))
        self.canvas.before.add(self.fret_bars)

    def redraw_inlays(self, box):
        self.inlays.clear()
        self.inlays.add(Color(1, 1, 1, 1))
        d = box.width * 0.01
        for i, fret_range in enumerate(self.fret_ranges):
            # Double circular inlay at fret 12.
            if i != 0 and i % 12 == 0:
                x_pos = (sum(fret_range) / 2)
                y_pos1 = (box.height / 3) + box.y
                y_pos2 = 2 * (box.height / 3) + box.y
                self.inlays.add(Ellipse(size=[d, d], pos=[x_pos - d / 2, y_pos1 - d / 2]))
                self.inlays.add(Ellipse(size=[d, d], pos=[x_pos - d / 2, y_pos2 - d / 2]))
            # Single circular inlay.
            elif i in [3, 5, 7, 9, 15, 17, 19, 21]:
                x_pos = (sum(fret_range) / 2)
                y_pos = (box.height / 2) + box.y
                self.inlays.add(Ellipse(size=[d, d], pos=[x_pos - d / 2, y_pos - d / 2]))
        self.canvas.before.add(self.inlays)

    def on_num_frets(self, instance, value):
        self.calc_fret_positions()
        self.calc_fret_pos_midpoints()
        self.update_canvas(instance, value)


class FretboardApp(App):
    def build(self):
        return Fretboard()

if __name__ == "__main__":
    FretboardApp().run()