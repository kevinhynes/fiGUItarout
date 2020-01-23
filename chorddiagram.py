from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty, ReferenceListProperty


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
    open_mark_opacs = ReferenceListProperty(s6_open_mark_opac, s5_open_mark_opac, s4_open_mark_opac,
                                            s3_open_mark_opac, s2_open_mark_opac, s1_open_mark_opac)

    s6_x_mark_opac = NumericProperty(1)
    s5_x_mark_opac = NumericProperty(1)
    s4_x_mark_opac = NumericProperty(1)
    s3_x_mark_opac = NumericProperty(1)
    s2_x_mark_opac = NumericProperty(1)
    s1_x_mark_opac = NumericProperty(1)
    x_mark_opacs = ReferenceListProperty(s6_x_mark_opac, s5_x_mark_opac, s4_x_mark_opac,
                                         s3_x_mark_opac, s2_x_mark_opac, s1_x_mark_opac)

    marker_radius = NumericProperty(0)
    s6_marker_opac = NumericProperty(1)
    s5_marker_opac = NumericProperty(1)
    s4_marker_opac = NumericProperty(1)
    s3_marker_opac = NumericProperty(1)
    s2_marker_opac = NumericProperty(1)
    s1_marker_opac = NumericProperty(1)
    marker_opacs = ReferenceListProperty(s6_marker_opac, s5_marker_opac, s4_marker_opac,
                                         s3_marker_opac, s2_marker_opac, s1_marker_opac)

    s6_red = NumericProperty(1)
    s5_red = NumericProperty(1)
    s4_red = NumericProperty(1)
    s3_red = NumericProperty(1)
    s2_red = NumericProperty(1)
    s1_red = NumericProperty(1)
    marker_reds = ReferenceListProperty(s6_red, s5_red, s4_red, s3_red, s2_red, s1_red)

    s6_fret_y = NumericProperty(0)
    s5_fret_y = NumericProperty(0)
    s4_fret_y = NumericProperty(0)
    s3_fret_y = NumericProperty(0)
    s2_fret_y = NumericProperty(0)
    s1_fret_y = NumericProperty(0)
    fret_ys = ReferenceListProperty(s6_fret_y, s5_fret_y, s4_fret_y, s3_fret_y, s2_fret_y, s1_fret_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_voicing(self, *args):
        self.draw_diagram()

    def draw_diagram(self):
        has_fret_0 = False
        min_fret = min(fret_num for fret_num in self.voicing if fret_num is not None)
        # fret markers closest to nut need to move the most step_y's.
        for i, fret_num in enumerate(self.voicing):
            if fret_num is None:
                self.draw_muted_string(i)
            elif fret_num == 0:
                has_fret_0 = True
                self.draw_open_string(i)
            else:
                self.draw_fingered_string(i, fret_num, min_fret)

        if has_fret_0:
            self.nut_opac = 1
            self.ids.fret_label.text = ''
        else:
            self.nut_opac = 0
            self.ids.fret_label.text = str(min_fret)


    def draw_muted_string(self, string_idx):
        self.open_mark_opacs[string_idx] = 0
        self.x_mark_opacs[string_idx] = 1
        self.marker_opacs[string_idx] = 0
        self.marker_reds[string_idx] = 0
        self.fret_ys[string_idx] = 0

    def draw_open_string(self, string_idx):
        self.open_mark_opacs[string_idx] = 1
        self.marker_opacs[string_idx] = 0
        self.marker_reds[string_idx] = 0
        self.fret_ys[string_idx] = 0
        self.x_mark_opacs[string_idx] = 0

    def draw_fingered_string(self, string_idx, fret_num, min_fret):
        self.open_mark_opacs[string_idx] = 0
        self.marker_opacs[string_idx] = 1
        self.marker_reds[string_idx] = 0
        self.fret_ys[string_idx] = 0
        self.x_mark_opacs[string_idx] = 0

        fret_y = self.step_y * 3
        steps_down = fret_num - min_fret
        self.fret_ys[string_idx] = fret_y - steps_down * self.step_y

    def on_size(self, *args):
        if any(self.voicing):
            self.on_voicing()

    # def on_touch_down(self, touch):
    #     self.voicing = [0, 1, 0, 2, 3, None][::-1]


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


