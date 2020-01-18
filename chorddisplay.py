from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.lang import Builder


class BackGroundColorWidget(Widget):
    pass


class BackGroundColorBoxLayout(BoxLayout):
    pass


class ChordGroup(StencilView, BackGroundColorWidget):

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.height = dp(90) if self.height == dp(270) else dp(270)
            return True


class ChordDisplay(FloatLayout):
    pass


class ChordDisplayApp(App):
    def build(self):
        return ChordDisplay()


if __name__ == "__main__":
    ChordDisplayApp().run()