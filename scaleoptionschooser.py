from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty


class ScaleTextChooser(BoxLayout):
    scale_text = StringProperty("")


class NoteHighlighter(BoxLayout):
    notes_to_highlight = StringProperty("")

    def update_notes_to_highlight(self, state, value):
        if state == "down":
            self.notes_to_highlight = value


class GroupHighlighter(BoxLayout):
    notes_or_octaves = StringProperty("Notes")

    def update_group_to_highlight(self, state, value):
        if state == "down":
            self.notes_or_octaves = value


class ScaleOptionsChooser(FloatLayout):
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")
    top_prop = NumericProperty(0)

    def on_size(self, instance, value):
        width, height = self.size
        target_ratio = 100/15
        # check which size is the limiting factor
        if width / height > target_ratio:
            # window is "wider" than targeted, so the limitation is the height.
            self.ids.box.height = height
            self.ids.box.width = height * target_ratio
        else:
            self.ids.box.width = width
            self.ids.box.height = width / target_ratio
        self.size = self.ids.box.size

    def slide(self, *args):
        if self.top == 0:
            self.top_prop = 150
        else:
            self.top_prop = 0


class ScaleOptionsChooserApp(App):
    def build(self):
        return ScaleOptionsChooser()


if __name__ == "__main__":
    ScaleOptionsChooserApp().run()