from kivy.app import App
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.graphics import InstructionGroup, Color, Line, Rectangle

from music_constants import chrom_scale, chrom_scale_no_acc, scale_degrees, standard_tuning
from markers import Marker
from colors import black, white, rainbow, octave_colors

scale_texts = {
    None: chrom_scale,
    "": chrom_scale,
    "Notes": chrom_scale,
    "Notes - No Accidentals": chrom_scale_no_acc,
    "Scale Degrees": scale_degrees}

scale_highlights = {
    "": 0b111111111111,
    "All": 0b111111111111,
    "R": 0b100000000000,
    "R, 3": 0b100110000000,
    "R, 5": 0b100000110000,
    "R, 3, 5": 0b100110110000,
    }


class Piano(FloatLayout):
    keyboard_pos = ListProperty()
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")
    tuning = ListProperty(standard_tuning)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Rectangle()
        self.key_outlines = InstructionGroup()
        self.black_keys = InstructionGroup()
        self.note_markers = InstructionGroup()
        self.canvas.add(white)
        self.canvas.add(self.background)
        self.canvas.add(black)
        self.canvas.add(self.key_outlines)
        self.canvas.add(self.black_keys)
        self.canvas.add(self.note_markers)
        self.key_midpoints = []        # For placing note markers.
        self.black_key_midpoints = []  # For placing black keys.
        self.rel_marker_heights = [0.1, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.5, 0.1, 0.5, 0.1]
        self.note_vals = [note_val for note_val in range(24, 24 + 61)]
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_kv_post(self, *args):
        self._calc_key_midpoints()
        self._add_markers()
        self._add_key_outlines()
        self._add_black_keys()

    def _calc_key_midpoints(self):
        key_midpoints = []
        key_width = 1 / 35
        black_key_locs = {1, 2, 4, 5, 6}
        for i in range(1, 36):
            key_midpoints += [(i / 35) - key_width / 2]
            if i % 7 in black_key_locs:
                key_midpoints += [i / 35]
        self.key_midpoints = key_midpoints

    def _add_markers(self):
        for i in range(60):
            marker = Marker()
            self.note_markers.add(marker)

    def _add_key_outlines(self):
        x, y = self.ids.keyboard.pos
        w, h = self.ids.keyboard.size
        step = w / 35
        for i in range(35):
            outline = Line(rectangle=(x + step * i, y, step, h))
            self.key_outlines.add(outline)

    def _add_black_keys(self):
        # Total width = 5 octaves with 7 white keys each (black keys don't add to width).
        black_key_midpoints = []
        for i in range(35):
            if i % 7 in (1, 2, 4, 5, 6):
                black_key_midpoints += [i / 35]
                self.black_keys.add(Rectangle())
        self.black_key_midpoints = black_key_midpoints

    def on_size(self, *args):
        """Resize the BoxLayout that holds the fretboard to maintain a guitar neck aspect ratio."""
        target_ratio = 60 / 7
        width, height = self.size
        # Check which size is the limiting factor.
        if width / height > target_ratio:
            # Window is "wider" than target, so the limitation is the height.
            self.ids.keyboard.height = height
            self.ids.keyboard.width = height * target_ratio
        else:
            self.ids.keyboard.width = width
            self.ids.keyboard.height = width / target_ratio

    def on_keyboard_pos(self, *args):
        self.update_canvas()

    def update_canvas(self, *args):
        self.update_background()
        self.update_key_outlines()
        self.update_black_keys()
        self.update_note_markers()

    def update_background(self):
        self.background.pos = self.ids.keyboard.pos
        self.background.size = self.ids.keyboard.size

    def update_key_outlines(self):
        w, h = self.ids.keyboard.size
        x, y = self.ids.keyboard.pos
        step = w / 35
        key_outlines = [obj for obj in self.key_outlines.children if isinstance(obj, Line)]
        for i, outline in enumerate(key_outlines):
            outline.rectangle = (x + step * i, y, step, h)

    def update_black_keys(self):
        white_key_width = self.ids.keyboard.width / 35
        black_key_width = white_key_width * 0.55
        black_keys = [obj for obj in self.black_keys.children if isinstance(obj, Rectangle)]
        for center_x, black_key in zip(self.black_key_midpoints, black_keys):
            x = center_x * self.ids.keyboard.width - (black_key_width / 2)
            y = self.ids.keyboard.y + (self.ids.keyboard.height / 3)
            black_key.pos = (x, y)
            black_key.size = (black_key_width, self.ids.keyboard.height * (2/3))

    def update_note_markers(self):
        x, y = self.ids.keyboard.pos
        width, height = self.ids.keyboard.size
        key_width = width / 35
        r1 = (key_width / 2) * 0.65
        r2 = r1 * 0.9
        rdiff = r1 - r2
        for i, (note_val, marker) in enumerate(zip(self.note_vals, self.note_markers.children)):
            key_midpoint = self.key_midpoints[i]
            c1x = x + (key_midpoint * width) - r1
            c1y = y + self.rel_marker_heights[i % 12] * height
            c2x, c2y = c1x + rdiff, c1y + rdiff

            octave, note_idx = divmod(note_val, 12)
            included = int(bin(self.mode_filter)[2:][note_idx - self.root_note_idx])
            highlighted = int(bin(scale_highlights[self.notes_to_highlight])[2:][note_idx - self.root_note_idx])

            if self.notes_or_octaves == "Notes":
                color_idx = note_idx - self.root_note_idx
                color = rainbow[color_idx]
            else:
                color_idx = octave
                color = octave_colors[color_idx]

            if self.scale_text == "Scale Degrees":
                note_idx -= self.root_note_idx

            note_text = scale_texts[self.scale_text][note_idx]

            marker.update(i, note_text, c1x, c1y, r1, c2x, c2y, r2, included, highlighted, color)

    def on_root_note_idx(self, *args):
        self.update_canvas()

    def on_mode_filter(self, *args):
        self.update_canvas()

    def on_scale_text(self, *args):
        self.update_note_markers()

    def on_notes_to_highlight(self, *args):
        self.update_note_markers()

    def on_notes_or_octaves(self, *args):
        self.update_note_markers()

    def on_tuning(self, *args):
        # Piano will always use C as lowest note.
        lowest_guitar_octave, note_idx = divmod(self.tuning[0], 12)
        lowest_piano_octave, _ = divmod(self.note_vals[0], 12)
        if lowest_guitar_octave != lowest_piano_octave:
            # if lowest_guitar_octave < lowest_piano_octave:
            low_c_note_val = lowest_guitar_octave * 12
            self.note_vals = [note_val for note_val in range(low_c_note_val, low_c_note_val + 61)]
            self.update_note_markers()



class PianoApp(App):
    def build(self):
        return Piano()


if __name__ == "__main__":
    PianoApp().run()