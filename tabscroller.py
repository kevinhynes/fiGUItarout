from kivy.app import App
from kivy.uix.scrollview import ScrollView

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.animation import Animation

from song_data import song_data

black = Color(0, 0, 0, 1)


class TabWidget(Widget):
    # step = NumericProperty(20)
    # num_measures = NumericProperty(4)

    '''
    Draw ultra-long guitar tab to canvas, where x-axis steps will be defined by 'width' of
    a 1/128th note to give a fine enough resolution.  Typically note values will only go down
    to 1/16th notes.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_glyphs = InstructionGroup()
        self.backgrounds = InstructionGroup()
        self.step_x = 4
        self.step_y = 20
        self.song_data = song_data
        self.num_measures = len(self.song_data)

        x_pos = 0
        for i, measure in enumerate(self.song_data):
            for beat in measure:
                note_dur = beat[1].value
                times = beat[1].tuplet.times
                enters = beat[1].tuplet.enters
                steps = (128 / note_dur) * (enters / times) * self.step_x
                voicing = beat[0]
                for y, fret_num in enumerate(voicing):
                    y_pos = self.step_y * (8 - y)
                    label_x = x_pos - self.step_x/2
                    label_y = y_pos - self.step_y/2
                    if fret_num is not None:
                        print(label_y)
                        background = Rectangle(pos=(label_x, label_y),
                                               size=(self.get_fret_num_size(fret_num)))
                        fret_num_instr = Rectangle(pos=(label_x, label_y),
                                                   size=(self.get_fret_num_size(fret_num)))
                        fret_num_glyph = CoreLabel(text=str(fret_num))
                        fret_num_glyph .refresh()
                        fret_num_instr.texture = fret_num_glyph.texture

                        self.note_glyphs.add(fret_num_instr)
                        self.backgrounds.add(background)
                x_pos += steps
        # self.canvas.add(Color(1, 0, 0, 0.5))
        # self.canvas.add(self.backgrounds)
        self.canvas.add(black)
        self.canvas.add(self.note_glyphs)

    def get_fret_num_size(self, fret_num):
        mult = len(str(fret_num))
        return self.step_x * mult, self.step_y


class TabScroller(ScrollView):
    step_y = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        anim = Animation(scroll_x=1, duration=150)
        anim.start(self)


class TabScrollerApp(App):
    pass


if __name__ == "__main__":
    TabScrollerApp().run()
