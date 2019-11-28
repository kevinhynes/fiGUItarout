from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

class NumFretsChanger(FloatLayout):
    num_frets = NumericProperty(24)
    box_height = NumericProperty(0)
    box_width = NumericProperty(0)

    def increment_num_frets(self):
        if self.num_frets < 24:
            self.num_frets += 1

    def decrement_num_frets(self):
        if self.num_frets > 5:
            self.num_frets -= 1

    def on_size(self, instance, value):
        width, height = self.size
        # Avoid ZeroDivisionError when TabbedPanel.do_default_tab == False.
        # Set size according to target ratio if its not part of the main app.
        if height > 0 and not self.box_height:
            target_ratio = 10/20
            if width / height > target_ratio:
                self.ids.box.height = height
                self.ids.box.width = height * target_ratio
            else:
                self.ids.box.width = width
                self.ids.box.height = width / target_ratio
        else:
            self.ids.box.height = self.box_height
            self.ids.box.width = (self.box_width-40)/6 + 40

class NumFretsChangerApp(App):
    def build(self):
        return NumFretsChanger()

if __name__ == "__main__":
    NumFretsChangerApp().run()