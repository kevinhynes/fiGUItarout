from kivy.properties import ListProperty, NumericProperty
from kivy.animation import Animation
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout


class SlidingMenu(TabbedPanel):
    menu_font_size = NumericProperty(32)

    def on_size(self, instance, value):
        self.menu_font_size = self.width * 0.01

    def animate_slide(self):
        if self.top_hint == 0:
            anim = Animation(top_hint=0.5, duration=0.3)
        else:
            anim = Animation(top_hint=0, duration=0.3)
        anim.start(self)


class SlideUpMenu(FloatLayout):
    tuning = ListProperty()
    num_frets = NumericProperty(12)
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)

