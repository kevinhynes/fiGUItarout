from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
Window.maximize()
# Window.size = (500, 300)

Builder.load_file("style.kv")
Builder.load_file("slideupmenu.kv")
Builder.load_file("fretboarddisplay.kv")
Builder.load_file("scaleoptionschooser.kv")
Builder.load_file("keysigchooser.kv")
Builder.load_file("keysigdisplay.kv")
Builder.load_file("keysigtitlebar.kv")
Builder.load_file("chorddisplay.kv")
Builder.load_file("metronome.kv")
Builder.load_file("tuner.kv")
Builder.load_file("numfretschanger.kv")
Builder.load_file("fretboard.kv")
Builder.load_file("piano.kv")
Builder.load_file("instrumentrack.kv")
Builder.load_file("songbuilder.kv")


class MainPage(FloatLayout):
    pass


class MainApp(App):
    def build(self):
        return MainPage()


if __name__ == "__main__":
    MainApp().run()