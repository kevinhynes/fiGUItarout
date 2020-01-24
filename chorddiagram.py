from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty, ReferenceListProperty
from kivy.clock import Clock


class ChordDiagram(Widget):
    voicing = ListProperty([None, None, None, None, None])
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)

    draw_x = NumericProperty(0)
    draw_y = NumericProperty(0)
    step_x = NumericProperty(0)
    step_y = NumericProperty(0)
    line_weight = NumericProperty(1)
    nut_height = NumericProperty(0)
    nut_opac = NumericProperty(1)
    disable_opac = NumericProperty(0)

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

    def on_size(self, *args):
        if any(self.voicing):
            self.slide_voicing()

    def on_note_idx(self, *args):
        if self.voicing:
            self.slide_voicing()

    def on_root_note_idx(self, *args):
        if self.voicing:
            self.slide_voicing()

    def on_voicing(self, *args):
        self.slide_voicing()

    def slide_voicing(self):
        # ALL chord voicings are rooted at C. Slide appropriate number of frets.
        slid_voicing = self.voicing[:]  # Make a copy to avoid infinite loop.
        for i, fret_num in enumerate(slid_voicing):
            if fret_num is not None:
                slid_voicing[i] = fret_num + self.note_idx
        if all(fret_num is None or fret_num >= 12 for fret_num in slid_voicing):
            slid_voicing = [fret_num % 12 for fret_num in self.voicing if fret_num is not None]
        self.draw_diagram(slid_voicing)

    def draw_diagram(self, voicing):
        if not voicing:
            return
        has_fret_0 = False
        min_fret = min(fret_num for fret_num in voicing if fret_num is not None)
        # fret markers closest to nut need to move the most step_y's.
        for i, fret_num in enumerate(voicing):
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
        self.disable_opac = 0

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

        # fret_y moves marker up the fretboard, to lower notes.
        fret_y = self.step_y * 3
        steps_down = fret_num - min_fret
        self.fret_ys[string_idx] = fret_y - steps_down * self.step_y

    def disable(self):
        for string_idx in range(6):
            self.open_mark_opacs[string_idx] = 0
            self.marker_opacs[string_idx] = 0
            self.marker_reds[string_idx] = 0
            self.fret_ys[string_idx] = 0
            self.x_mark_opacs[string_idx] = 0
        self.disable_opac = 1



class ChordDiagramContainer(FloatLayout):
    bin_chord_shape = NumericProperty()
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    voicings = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chord_diagram = ChordDiagram()
        self.bind(note_idx=self.chord_diagram.setter('note_idx'))
        self.bind(root_note_idx=self.chord_diagram.setter('root_note_idx'))
        self.bind(mode_filter=self.chord_diagram.setter('mode_filter'))
        self.add_widget(self.chord_diagram)
        Clock.schedule_once(self.update_diagram, 5)

    def on_size(self, *args):
        target_ratio = 21 / 26  # width / height
        if self.width / self.height > target_ratio:
            # available space is wider than desired width
            self.chord_diagram.height = self.height
            self.chord_diagram.width = target_ratio * self.height
        else:
            self.chord_diagram.width = self.width
            self.chord_diagram.height = self.width / target_ratio

    def on_bin_chord_shape(self, *args):
        self.update_diagram()

    def on_note_idx(self, *args):
        self.update_diagram()

    def update_diagram(self, *args):
        if self.display:
            # Major 13th chord has 7 notes, guitar only has 6 strings.
            chord_possible_on_guitar = bin(self.bin_chord_shape) in self.display.chords_to_voicings
            if chord_possible_on_guitar and self.is_chord_in_key():
                self.voicings = self.display.chords_to_voicings[bin(self.bin_chord_shape)]
                self.chord_diagram.voicing = self.voicings[0]
            else:
                self.chord_diagram.disable()

    def is_chord_in_key(self):
        def do_circular_bit_rotation(num_shifts, mode):
            for _ in range(num_shifts):
                rotate_bit = 0b100000000000 & mode
                mode <<= 1

                if rotate_bit:
                    rotate_bit = 1
                else:
                    rotate_bit = 0

                mode |= rotate_bit
                mode &= 0b111111111111
            return mode

        # TODO: how many left shifts are needed to rotate a mode based on root_note_idx and note_idx?
        # C -> B == 11.  B -> C = 1.. ?
        if self.note_idx >= self.root_note_idx:
            num_shifts = self.note_idx - self.root_note_idx
        else:
            num_shifts = 12 - (self.root_note_idx - self.note_idx)
        rotated_mode = do_circular_bit_rotation(num_shifts, self.mode_filter)
        chord_mask = int(self.bin_chord_shape)
        # Are all the notes that make this chord also in this mode?
        chord_in_key = rotated_mode & chord_mask == chord_mask
        return chord_in_key


class ChordDiagramApp(App):
    def build(self):
        return ChordDiagramContainer()


if __name__ == "__main__":
    ChordDiagramApp().run()


