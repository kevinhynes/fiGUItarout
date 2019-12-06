from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView
from kivy.properties import NumericProperty, ListProperty, ReferenceListProperty, ObjectProperty
from kivy.graphics import InstructionGroup, Rectangle, Ellipse, Line, Color, Quad
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.animation import Animation


from markers import Marker

flat = u'\u266D'
sharp = u'\u266F'
chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale2 = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']
scale_degrees = ["1", "♭2", "2", "♭3", "3", "4", "♯4/♭5", "5", "♯5/♭6", "6", "♭7", "7"]

octave_alpha = 0.8
octave_colors = [[255 / 255, 180 / 255, 52 / 255, octave_alpha],  # orange
                 [255 / 255, 251 / 255, 52 / 255, octave_alpha],  # yellow
                 [83 / 255, 180 / 255, 52 / 255, octave_alpha],  # green
                 [52 / 255, 255 / 255, 249 / 255, octave_alpha],  # blue
                 [255 / 255, 52 / 255, 243 / 255, octave_alpha]]  # purple

black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)
gray = Color(0.5, 0.5, 0.5, 1)
brown = Color(rgba=[114 / 255, 69 / 255, 16 / 255, 1])

rainbow = [Color(hsv=[i / 12, 1, 0.95]) for i in range(12)]
reds = [Color(hsv=[0, i / 12, 1]) for i in range(12)][::-1]
blues = [Color(hsv=[0.6, i / 12, 1]) for i in range(12)][::-1]


class String(FloatLayout):
    open_note_val = NumericProperty(0)
    num_frets = NumericProperty(12)
    fret_positions = ListProperty()
    note_vals = ListProperty()
    mode_filter = NumericProperty(0b111111111111)
    root_note_idx = NumericProperty(0)
    string_blinks = ReferenceListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.string_shadow = Rectangle()
        self.string_graphic = Rectangle()
        self.note_markers = InstructionGroup()
        self.octave_markers = InstructionGroup()

        self.canvas.add(Color(rgba=[0 / 255, 0 / 255, 0 / 255, 0.25]))
        self.canvas.add(self.string_shadow)
        self.canvas.add(Color(rgba=[169 / 255, 169 / 255, 169 / 255, 1]))
        self.canvas.add(self.string_graphic)
        self.add_markers()
        self.canvas.add(self.note_markers)
        self.canvas.add(self.octave_markers)
        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def add_markers(self):
        for i in range(25):
            marker = Marker()
            self.note_markers.add(marker)

    def update_canvas(self, *args):
        if self.fret_positions:  # self.fret_positions is empty during instantiation.
            # self.redraw_octave_markers()
            self.redraw_string()
            self.redraw_note_markers()

    def animate_marker(self, index, *args):
        print(*args)
        markers = self.note_markers.children
        print(markers)
        anim = Animation(duration=1)
        anim.bind(on_start=markers[index].initiate_animation)
        anim.bind(on_progress=markers[index].update_animation)
        anim.bind(on_complete=markers[index].after_animation)
        anim.start(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.animate_marker(0)

    def redraw_string(self):
        w, h = self.width, self.height * 0.1
        x, y = self.pos
        cy = y + (self.height / 2)
        string_y = cy - (h/2)
        shadow_height = 3 * h
        shadow_y = string_y - shadow_height
        # Shadow effect.
        self.string_shadow.size = [w, shadow_height]
        self.string_shadow.pos = [x, cy - shadow_height]
        # String.
        self.string_graphic.size = [w, h]
        self.string_graphic.pos = [x, string_y]

    def redraw_note_markers(self, *args):
        x, y = self.pos
        r1 = self.height / 2
        r2 = r1 * 0.9
        rdiff = r1 - r2
        for i, (note_val, marker) in enumerate(zip(self.note_vals, self.note_markers.children)):
            # Make right edge of circle touch left edge of fret bar (where your finger should go!)
            fret_left = self.fret_positions[i] - (self.fretboard.fret_bar_width / 2)
            # Draw 2 concentric circles, c1 and c2.
            # Circles are defined by a square's lower left corner.
            c1x, c1y = (fret_left - 2 * r1) + x, y
            c2x, c2y = c1x + rdiff, c1y + rdiff

            octave, note_idx = divmod(note_val, 12)
            note_text = chrom_scale[note_idx]
            color_idx = note_idx - self.root_note_idx
            included = int(bin(self.mode_filter)[2:][note_idx - self.root_note_idx])

            marker.update(i, note_text, color_idx, c1x, c1y, r1, c2x, c2y, r2, included)

    def redraw_octave_markers(self):
        self.octave_markers.clear()
        for i, note_val in enumerate(self.note_vals):
            self.redraw_octave_marker(i, note_val)

    def redraw_octave_marker(self, i, note_val):
        if self.fret_ranges:
            octave = (note_val - self.fretboard.root_note_idx) // 12
            octave -= 2  # second musical octave is 0th on guitar... sloopy
            color = Color(*octave_colors[octave])
            left, right = self.fret_ranges[i]
            width = right - left
            self.octave_markers.add(color)
            self.octave_markers.add(Rectangle(pos=[left, 0], size=[width, self.height]))

    def on_open_note_val(self, instance, value):
        self.note_vals = [val for val in range(self.open_note_val, self.open_note_val + 25)]
        self.update_canvas(instance, value)

    def on_num_frets(self, instance, value):
        self.note_vals = [val for val in range(self.open_note_val, self.open_note_val + 25)]
        self.update_canvas(instance, value)

    def on_root_note_idx(self, instance, value):
        self.update_canvas(instance, value)

    def on_mode_filter(self, instance, value):
        self.update_canvas(instance, value)


class Fretboard(StencilView, FloatLayout):
    num_frets = NumericProperty(24)
    tuning = ListProperty([28, 33, 38, 43, 47, 52])
    fret_ranges = ListProperty()
    fret_positions = ListProperty()
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    box_x = NumericProperty(0)
    box_y = NumericProperty(0)
    box_pos = ReferenceListProperty(box_x, box_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fret_bar_width = self.width * (0.1 / 24.75)
        self.relative_fret_positions = self.calc_relative_fret_positions()
        self.fret_positions = self.calc_fret_positions(self)
        self.fret_ranges = self.calc_fret_ranges(self)

        self.fingerboard = Rectangle()
        self.fret_bars = InstructionGroup()
        self.inlays = InstructionGroup()
        self.add_fret_bars()
        self.add_inlays()

        # When launching Fretboard as App, need to use canvas.before..
        self.canvas.before.add(brown)
        self.canvas.before.add(self.fingerboard)
        self.canvas.before.add(black)
        self.canvas.before.add(self.fret_bars)
        self.canvas.before.add(white)
        self.canvas.before.add(self.inlays)

    def add_fret_bars(self):
        """Add Rectangles to display fret bars.
        Setting maximum to 24 frets (25 with nut) - the most on any common guitar.
        When less frets are chosen, some will be drawn off screen."""
        for fret in range(25):
            self.fret_bars.add(Rectangle())

    def add_inlays(self):
        """Add Ellipses to display inlays.
        There will be a maximum of 12 for a 24-fret guitar (for a typical Fender style).
        When less frets are chosen, some will be drawn off screen."""
        for inlay in range(12):
            self.inlays.add(Ellipse())

    def calc_relative_fret_positions(self):
        """Calculate relative position of frets on a 24-fret fretboard.
        Each fret position is in the range [0, 1], where 1 is the full length of the fretboard."""
        # Ratio of fret[i]/fret[i+1] for 12-tone equal temperament.
        temperament = 2 ** (1 / 12)

        # All fret_pos in fret_positions represent % of guitar string; 12th fret_pos == 0.5.
        # All fret_pos in range [0, 0.75] for 24 fret guitar.
        fret_positions = [1 - (1 / (temperament ** fret_num)) for fret_num in range(25)]

        # Stretch fret_positions to represent % of fretboard instead.
        # All fret_pos now in range [0, 1].
        fret_positions = [fret_pos / fret_positions[-1] for fret_pos in fret_positions]

        # Tricky: 0th fret cannot occur at 0; need room to its left to display open note info.
        # Move 0th fret up for nut and scale remaining appropriately.
        # All fret_pos now in range [nut_width_ratio, 1].
        nut_width_ratio = 0.03
        fret_positions = [((1 - nut_width_ratio) * fret_pos) + nut_width_ratio for fret_pos in
                          fret_positions]
        return fret_positions

    def calc_fret_positions(self, box):
        """Calculate position of each fret based on fretboard's current width."""

        # Normalize relative_fret_positions so that we only draw self.num_frets on the screen.
        # Any frets with a normalized_fret_position > 1 will be drawn off screen.
        rightmost = self.relative_fret_positions[self.num_frets]
        normalized_fret_positions = [fret_pos / rightmost for fret_pos in self.relative_fret_positions]

        # Calculate the actual x position of each fret.
        self.fret_positions = [fret_pos * box.width + box.x for fret_pos in normalized_fret_positions]
        return self.fret_positions

    def calc_fret_ranges(self, box):
        """Calculate x positions of fretboard between frets for use in displaying octaves."""
        # Gibson ratio of fret bar width to scale length.
        self.fret_bar_width = box.width * (0.1 / 24.75)
        cur_right = box.x
        fret_ranges = []
        for fret_pos in self.fret_positions:
            next_left = fret_pos - (self.fret_bar_width / 2)
            fret_ranges.append((cur_right, next_left))
            cur_right = (next_left + self.fret_bar_width)
        self.fret_ranges = fret_ranges
        return self.fret_ranges

    def update_canvas(self, *args):
        # With box now resized, recalculate & redraw everything. Having trouble drawing things
        # in order using mixture of python and kv lang. Order is explicit here.
        box = self.ids.box
        self.calc_fret_positions(box)
        self.calc_fret_ranges(box)
        self.redraw_fingerboard(box)
        self.redraw_fret_bars(box)
        self.redraw_inlays(box)

    def redraw_fingerboard(self, box):
        self.fingerboard.size = box.size
        self.fingerboard.pos = box.pos

    def redraw_fret_bars(self, box):
        # When adding Rectangle to InstructionGroup, BindTextures are added first.
        self.fret_bar_width = self.width * (0.1/24.75)
        rects = [obj for obj in self.fret_bars.children if isinstance(obj, Rectangle)]
        for fret_pos, rect in zip(self.fret_positions, rects):
            x_pos = fret_pos - (self.fret_bar_width / 2)
            rect.size = [self.fret_bar_width, box.height]
            rect.pos = [x_pos, box.y]

    def redraw_inlays(self, box):
        inlays = [obj for obj in self.inlays.children if isinstance(obj, Ellipse)]
        inlay_num = 0
        d = box.width * 0.01
        for i, fret_range in enumerate(self.fret_ranges):
            # Double circular inlay at fret 12.
            if i != 0 and i % 12 == 0:
                x_pos = (sum(fret_range) / 2)
                y_pos1 = (box.height / 3) + box.y
                y_pos2 = 2 * (box.height / 3) + box.y
                inlay1 = inlays[inlay_num]
                inlay2 = inlays[inlay_num + 1]
                inlay1.size = [d, d]
                inlay2.size = [d, d]
                inlay1.pos = [x_pos - d / 2, y_pos1 - d / 2]
                inlay2.pos = [x_pos - d / 2, y_pos2 - d / 2]
                inlay_num += 2
            # Single circular inlay.
            elif i in [3, 5, 7, 9, 15, 17, 19, 21]:
                x_pos = (sum(fret_range) / 2)
                y_pos = (box.height / 2) + box.y
                inlay = inlays[inlay_num]
                inlay.size = [d, d]
                inlay.pos = [x_pos - d / 2, y_pos - d / 2]
                inlay_num += 1

    def on_size(self, *args):
        """Resize the BoxLayout that holds the fretboard to maintain a guitar neck aspect ratio."""
        target_ratio = 10
        width, height = self.size
        # Check which size is the limiting factor.
        if width / height > target_ratio:
            # Window is "wider" than target, so the limitation is the height.
            self.ids.box.height = height
            self.ids.box.width = height * target_ratio
        else:
            self.ids.box.width = width
            self.ids.box.height = width / target_ratio

    def on_box_pos(self, *args):
        self.update_canvas()

    def on_num_frets(self, *args):
        self.calc_fret_positions(self)
        self.update_canvas()


class FretboardApp(App):
    def build(self):
        return Fretboard()


if __name__ == "__main__":
    FretboardApp().run()
