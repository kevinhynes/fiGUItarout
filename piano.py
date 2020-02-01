from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty
from kivy.graphics import InstructionGroup, Color, Line, Rectangle

from markers import Marker

black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)


class Piano(FloatLayout):
    keyboard_pos = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Rectangle()
        self.key_outlines = InstructionGroup()
        self.black_keys = InstructionGroup()
        self.black_key_midpoints = []
        self.note_markers = InstructionGroup()
        self.canvas.add(white)
        self.canvas.add(self.background)
        self.canvas.add(black)
        self.canvas.add(self.key_outlines)
        self.canvas.add(self.black_keys)
        # self.canvas.add(self.note_markers)
        self.rel_marker_heights = [0.2, 0.5, 0.2, 0.5, 0.2, 0.2, 0.5, 0.2, 0.5, 0.2, 0.5, 0.2]
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_kv_post(self, *args):
        self._add_markers()
        self._add_key_outlines()
        self._add_black_keys()

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
        white_key_step = 1 / (5 * 7)
        black_key_midpoints = []
        for i in range(35):
            if i % 7 in (1, 2, 4, 5, 6):
                black_key_midpoints += [i / 35]
                self.black_keys.add(Rectangle())
        self.black_key_midpoints = black_key_midpoints
        print(len(self.black_key_midpoints))

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
        black_key_width = white_key_width / 2
        black_keys = [obj for obj in self.black_keys.children if isinstance(obj, Rectangle)]
        for center_x, black_key in zip(self.black_key_midpoints, black_keys):
            x = center_x * self.ids.keyboard.width - (black_key_width / 2)
            y = self.ids.keyboard.y + (self.ids.keyboard.height / 3)
            black_key.pos = (x, y)
            black_key.size = (black_key_width, self.ids.keyboard.height * (2/3))


class PianoApp(App):
    def build(self):
        return Piano()


if __name__ == "__main__":
    PianoApp().run()