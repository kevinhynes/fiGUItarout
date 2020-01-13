from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, ListProperty


class ScaleTextChooser(BoxLayout):
    scale_text = StringProperty("")


class IndexedCheckBox(CheckBox):

    def __init__(self, idx=0, **kwargs):
        super().__init__(**kwargs)
        self.idx = idx
        self.active = True

    def on_active(self, checkbox, is_active):
        if self.parent:
            self.parent.highlight(self.idx, is_active)


class NoteSelector(BoxLayout):
    highlights = ListProperty([True]*12)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(12):
            checkbox = IndexedCheckBox(i)
            self.add_widget(checkbox)

    def highlight(self, checkbox_idx, is_active):
        self.highlights[checkbox_idx] = is_active


class ScaleColorChooser(BoxLayout):
    highlights = ListProperty([True]*12)
    scale_text = StringProperty("")

    def on_highlights(self, *args):
        print(self.highlights)


class ScaleOptionsChooser(FloatLayout):

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


class ScaleOptionsChooserApp(App):
    def build(self):
        return ScaleOptionsChooser()


if __name__ == "__main__":
    ScaleOptionsChooserApp().run()