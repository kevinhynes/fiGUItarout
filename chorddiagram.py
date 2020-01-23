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
    line_weight = NumericProperty(1)
    nut_height = NumericProperty(0)
    nut_opac = NumericProperty(1)

    s6_open_mark_opac = NumericProperty(1)
    s5_open_mark_opac = NumericProperty(1)
    s4_open_mark_opac = NumericProperty(1)
    s3_open_mark_opac = NumericProperty(1)
    s2_open_mark_opac = NumericProperty(1)
    s1_open_mark_opac = NumericProperty(1)

    s6_x_mark_opac = NumericProperty(1)
    s5_x_mark_opac = NumericProperty(1)
    s4_x_mark_opac = NumericProperty(1)
    s3_x_mark_opac = NumericProperty(1)
    s2_x_mark_opac = NumericProperty(1)
    s1_x_mark_opac = NumericProperty(1)

    marker_radius = NumericProperty(0)
    s6_marker_opac = NumericProperty(1)
    s5_marker_opac = NumericProperty(1)
    s4_marker_opac = NumericProperty(1)
    s3_marker_opac = NumericProperty(1)
    s2_marker_opac = NumericProperty(1)
    s1_marker_opac = NumericProperty(1)

    s6_red = NumericProperty(1)
    s5_red = NumericProperty(1)
    s4_red = NumericProperty(1)
    s3_red = NumericProperty(1)
    s2_red = NumericProperty(1)
    s1_red = NumericProperty(1)

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


