from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
# from kivy.config import Config
# Config.set('graphics', 'maxfps', 0)

Builder.load_file("style.kv")
Builder.load_file("popupmenu.kv")
Builder.load_file("keysigchooser.kv")
Builder.load_file("keysigdisplay.kv")
Builder.load_file("tuner.kv")
Builder.load_file("numfretschanger.kv")
Builder.load_file("fretboard.kv")

class MainPage(FloatLayout):
    pass

class MainApp(App):
    def build(self):
        return MainPage()

if __name__ == "__main__":
    MainApp().run()