from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty


class ChordDiagram(Widget):
    voicing = ListProperty([None, None, None, None, None])
    draw_x = NumericProperty(0)
    draw_y = NumericProperty(0)
    step_x = NumericProperty(0)
    step_y = NumericProperty(0)
    nut_height = NumericProperty(0)
    nut_opac = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChordDiagramContainer(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chord_diagram = ChordDiagram()
        self.add_widget(self.chord_diagram)

    def on_size(self, *args):
        target_ratio = 21 / 26  # width / height
        if self.width / self.height > target_ratio:
            # available space is wider than desired width
            self.chord_diagram.height = self.height
            self.chord_diagram.width = target_ratio * self.height
        else:
            self.chord_diagram.width = self.width
            self.chord_diagram.height = self.width / target_ratio


class ChordDiagramApp(App):
    def build(self):
        return ChordDiagramContainer()


if __name__ == "__main__":
    ChordDiagramApp().run()


