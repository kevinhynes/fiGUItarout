from kivy.app import App
from kivy.properties import ListProperty, NumericProperty
from kivy.animation import Animation
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout


class SlidingMenu(TabbedPanel):
    def animate_slide(self):
        if self.top_hint == 0:
            anim = Animation(top_hint=0.5)
        else:
            anim = Animation(top_hint=0)
        anim.start(self)


class SlideUpMenu(FloatLayout):
    tuning = ListProperty()
    num_frets = NumericProperty(12)
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

