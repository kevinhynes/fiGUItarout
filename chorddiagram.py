from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty, \
    StringProperty
from kivy.clock import Clock
from kivy.metrics import dp

from music_constants import chrom_scale
ROW_HEIGHT = dp(95)


class ChordDiagram(Widget):
    voicing = ListProperty([None, None, None, None, None])
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)
    chord_name = StringProperty('')

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
        self.chrom_scale = chrom_scale

    def on_size(self, *args):
        if any(self.voicing):
            self.draw_diagram()

    def draw_diagram(self):
        if not self.voicing or not any(fret_num for fret_num in self.voicing):
            return
        slid_voicing = self.slide_voicing(self.voicing)
        min_fret = min(fret_num for fret_num in slid_voicing if fret_num is not None)
        has_fret_0 = any(fret_num == 0 for fret_num in slid_voicing)
        if has_fret_0:
            self.nut_opac = 1
            self.ids.fret_label.text = ''
            min_fret = 1
        else:
            self.nut_opac = 0
            self.ids.fret_label.text = str(min_fret)

        # fret markers closest to nut need to move the most step_y's.
        for i, fret_num in enumerate(slid_voicing):
            if fret_num is None:
                self.draw_muted_string(i)
            elif fret_num == 0:
                self.draw_open_string(i)
            else:
                self.draw_fingered_string(i, fret_num, min_fret)

        self.disable_opac = 0

    def slide_voicing(self, voicing):
        # ALL chord voicings are rooted at C. Slide appropriate number of frets.
        slid_voicing = voicing[:]  # Make a copy to avoid infinite loop.
        for i, fret_num in enumerate(slid_voicing):
            if fret_num is not None:
                slid_voicing[i] = fret_num + self.note_idx
        if all(fret_num is None or fret_num >= 12 for fret_num in slid_voicing):
            slid_voicing = [fret_num % 12 for fret_num in self.voicing if fret_num is not None]
        return slid_voicing

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
    voicing = ListProperty([None, None, None, None, None, None])
    display = ObjectProperty(None)
    chord_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.update_diagram, 0.1)

    def on_size(self, *args):
        target_ratio = 27 / 28  # width / height
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

    def on_voicing(self, *args):
        self.update_diagram()

    def update_diagram(self, *args):
        # if self.display:
            # Major 13th chord has 7 notes, guitar only has 6 strings.
            # chord_possible_on_guitar = bin(self.bin_chord_shape) in self.display.chords_to_voicings
            # print(f'ChordDiagramContainer.update_diagram() - chord_possible_on_guitar {chord_possible_on_guitar}')
            # print(f'ChordDiagramContainer.update_diagram() - bin_chord_shape {self.bin_chord_shape}')
        if self.is_chord_in_key():
            # print(f'ChordDiagramContainer.update_diagram() - draw')
            self.chord_diagram.voicing = self.voicing
            self.chord_diagram.draw_diagram()
        else:
            # print(f'ChordDiagramContainer.update_diagram() - disable')
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
        # Are all the notes that make this chord also in this mode/key?
        chord_in_key = rotated_mode & chord_mask == chord_mask
        return chord_in_key


class ChordDiagramMain(FloatLayout):
    bin_chord_shape = NumericProperty(0)
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    display = ObjectProperty(None)
    voicings = ListProperty([])
    chord_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.popup:
                self.popup.dismiss()
                self.popup = None
            else:
                content = ChordDiagramPopupContent(note_idx=self.note_idx,
                                                   chord_name=self.chord_name,
                                                   voicings=self.voicings)
                self.popup = ChordDiagramPopup(content=content, width=self.row.width)
                self.popup.open()
            return True
        return super().on_touch_down(touch)

    def on_voicings(self, *args):
        self.cd_container.voicing = self.voicings[0]


class ChordDiagramPopupContent(ScrollView):

    def __init__(self, note_idx, chord_name, voicings, **kwargs):
        super().__init__(**kwargs)
        self.scroll_box = BoxLayout(orientation='horizontal',
                                    size_hint=[None, None])
        sb_width = boxes = 0
        for voicing in voicings:
            if boxes > 10:
                return
            cdc = ChordDiagramContainer(pos_hint={'center_x': 0.5})
            cdc.voicing = voicing
            cdc.note_idx = note_idx
            cdc.chord_name = chord_name
            sb_width += cdc.width
            self.scroll_box.add_widget(cdc)
        self.scroll_box.width = sb_width
        self.add_widget(self.scroll_box)


class ChordDiagramPopup(Popup):
    pass


class ChordDiagramApp(App):
    def build(self):
        return ChordDiagramContainer()


if __name__ == "__main__":
    ChordDiagramApp().run()


