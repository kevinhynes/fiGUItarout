from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty, \
    StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

# from kivy.lang import Builder
# Builder.load_file('chorddiagram.kv')


import json

from music_constants import chrom_scale
ROW_HEIGHT = dp(95)


class ChordDiagramBubble(Bubble):

    def __init__(self, voicing, chord_diagram, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = [None, None]
        self.pos_hint = {'center': [0.5, 0.5]}
        self.size = [100, 50]
        self.voicing = voicing
        self.chord_diagram = chord_diagram

    def select(self, *args):
        print('selected!')
        self.chord_diagram.popup.voicing = self.voicing
        self.chord_diagram.remove_bubble()

    def delete(self, *args):
        print(self.voicing)
        with open('impossible_fingerings.json', 'r') as read_file:
            impossible_fingerings = json.load(read_file)
        impossible_fingerings += [self.voicing]
        print(impossible_fingerings)
        with open('impossible_fingerings.json', 'w') as write_file:
            json.dump(impossible_fingerings, write_file)
        self.chord_diagram.remove_bubble()


class ChordDiagram(FloatLayout):
    chrom_scale = chrom_scale
    voicing = ListProperty([None, None, None, None, None])
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)
    chord_name = StringProperty('')
    chord_num = NumericProperty()
    mode_filter = NumericProperty(0b101011010101)
    display = ObjectProperty(None)
    chord_in_key = BooleanProperty(False)
    diagram = ObjectProperty(None)

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
        self.is_popup = False
        self.bubble = None
        self.popup = None
        self.selected = False
        self.disabled = False

    def on_chord_num(self, *args):
        self.update_diagram()

    def on_note_idx(self, *args):
        self.update_diagram()

    def on_root_note_idx(self, *args):
        self.update_diagram()

    def on_mode_filter(self, *args):
        self.update_diagram()

    def on_voicing(self, *args):
        self.update_diagram()

    def on_size(self, *args):
        target_ratio = 27 / 28  # width / height
        if self.width / self.height > target_ratio:
            # available space is wider than desired width
            self.diagram.height = self.height
            self.diagram.width = target_ratio * self.height
        else:
            self.diagram.height = self.width / target_ratio
            self.diagram.width = self.width
        if any(self.voicing):
            self.update_diagram()

    ####################################  DRAWING METHODS  #########################################
    def update_diagram(self, *args):
        if self.is_chord_in_key():
            self.voicing = self.voicing
            self.draw_diagram()
        else:
            self.disable()

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

        # C Major Scale =   0b101011010101
        #                     C D EF G A B
        # Any Major Chord = 0b100010010000
        # To test if D Major is in C Major scale, rotate C Major Scale 2 bits, so D is leftmost.
        # C rooted at D =   0b101101010110
        # D Major Chord =   0b100010010000
        # D Major Chord has 1 bit set that is not in C rooted at D, therefore
        # D Major Chord is not in the C Major scale.
        if self.note_idx >= self.root_note_idx:
            num_shifts = self.note_idx - self.root_note_idx
        else:
            num_shifts = 12 - (self.root_note_idx - self.note_idx)
        rotated_mode = do_circular_bit_rotation(num_shifts, self.mode_filter)
        chord_mask = int(self.chord_num)
        # Are all the notes that make this chord also in this mode/key?
        chord_in_key = rotated_mode & chord_mask == chord_mask
        return chord_in_key

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
        self.disabled = False

    def slide_voicing(self, voicing):
        # ALL chord voicings are rooted at C. Slide appropriate number of frets.
        slid_voicing = voicing[:]  # Make a copy to avoid infinite loop.
        for i, fret_num in enumerate(slid_voicing):
            if fret_num is not None:
                slid_voicing[i] = fret_num + self.note_idx
        if all(fret_num is None or fret_num >= 12 for fret_num in slid_voicing):
            slid_voicing[:] = [fret_num % 12 if fret_num is not None else None for fret_num in slid_voicing]
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

        # fret_y moves marker up the fretboard vertically, to lower notes.
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
        self.disabled = True

    ####################################  POPUP METHODS  ###########################################
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y) and self.is_popup:
            if self.selected:
                self.center = self.ox, self.oy
                self.selected = False
            elif not self.bubble:
                self.bubble = bubble = ChordDiagramBubble(self.voicing, self)
                self.bind(pos=bubble.setter('pos'))
                self.add_widget(bubble)
                print('bubble added')
            else:
                super().on_touch_down(touch)
                if self.bubble:
                    self.remove_bubble()
            if self.selected:
                self.center = self.ox, self.oy
                self.selected = False
            return True

    def remove_bubble(self, *args):
        self.remove_widget(self.bubble)
        self.bubble = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y) and self.is_popup:
            self.selected = True
            self.ox, self.oy = self.cur_x, self.cur_y = self.center
            return True

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y) and self.is_popup and self.selected:
            dx, dy = touch.x - self.cur_x, touch.y - self.cur_y
            self.translate(dx, dy)
            return True

    def translate(self, dx, dy):
        self.center_x = self.cur_x = self.cur_x + dx
        self.center_y = self.cur_y = self.cur_y + dy


class ChordDiagramMain(FloatLayout):
    note_idx = NumericProperty(0)
    root_note_idx = NumericProperty(0)
    chord_num = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    chord_diagram = ObjectProperty(None)
    display = ObjectProperty(None)
    voicings = ListProperty([])
    chord_name = StringProperty('')
    voicing = ListProperty([None, None, None, None, None, None])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.popup:
                self.popup.dismiss()
                self.popup = None
            elif not self.chord_diagram.disabled:
                full_chord_name = chrom_scale[self.note_idx] + " " + self.chord_name
                title = full_chord_name + " Alternative Voicings"
                content = ChordDiagramPopupContent(note_idx=self.note_idx,
                                                   root_note_idx=self.root_note_idx,
                                                   chord_num=self.chord_num,
                                                   mode_filter=self.mode_filter,
                                                   chord_name=self.chord_name,
                                                   voicings=self.voicings)
                self.popup = ChordDiagramPopup(title=title,
                                               content=content,
                                               width=content.width * 1.2)
                content.bind(voicing=self.popup.setter('voicing'))
                self.popup.bind(voicing=self.setter('voicing'))
                self.popup.open()
            return True
        return super().on_touch_down(touch)

    def on_voicings(self, *args):
        self.chord_diagram.voicing = self.voicings[0]

    def on_voicing(self, *args):
        self.chord_diagram.voicing = self.voicing


class ChordDiagramPopup(Popup):
    voicing = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = [None, None]
        self.height = ROW_HEIGHT * 7


class ChordDiagramPopupContent(ScrollView):
    voicing = ListProperty()

    def __init__(self, note_idx, root_note_idx, chord_num,
                 mode_filter, chord_name, voicings, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint = {'center_x': 0.5}
        self.size_hint = [None, None]
        self.height = ROW_HEIGHT * 6
        self.scroll_grid = BoxLayout(orientation='horizontal',
                                     size_hint=[None, None],
                                     pos_hint={'center_x': 0.5})
        self.add_columns()
        self.build_title_bar()
        self.build_columns(note_idx, root_note_idx, chord_num, mode_filter, chord_name, voicings)
        # Child widgets are displayed right to left in horizontal BoxLayout; reverse this.
        self.scroll_grid.children = self.scroll_grid.children[::-1]
        self.width = self.scroll_grid.width
        self.add_widget(self.scroll_grid)

    def add_columns(self):
        for i in range(4):
            column = BoxLayout(orientation='vertical',
                               size_hint=[None, None],
                               pos_hint={'top': 1},
                               spacing=1)
            self.scroll_grid.add_widget(column)

    def build_title_bar(self):
        # Add labels for chords rooted at string 6, 5, 4, 3.
        # String 6 is children[0], 5 is children[1], 4 is children[2], 3 is children[3].
        for i in range(6, 2, -1):
            label = Label(text='Root ' + str(i) + ' string', size_hint_y=None, height=ROW_HEIGHT/2)
            column = self.scroll_grid.children[6 - i]
            column.add_widget(label)

    def build_columns(self, note_idx, root_note_idx, chord_num, mode_filter, chord_name, voicings):
        def get_col_idx(voicing):
            for i, fret_num in enumerate(voicing):
                if fret_num is not None:
                    return i
        for voicing in voicings:
            column_idx = get_col_idx(voicing)
            column = self.scroll_grid.children[column_idx]
            cd = ChordDiagram()
            cd.is_popup = True
            cd.popup = self
            cd.note_idx = note_idx
            cd.root_note_idx = root_note_idx
            cd.chord_num = chord_num
            cd.mode_filter = mode_filter
            cd.chord_name = chord_name
            cd.voicing = voicing
            column.add_widget(cd)

        # Set scroll_grid width.
        self.scroll_grid.width = column.width * 4

        # Set the column and scroll_grid heights.
        for column_idx in range(4):
            column = self.scroll_grid.children[column_idx]
            height = ROW_HEIGHT * len(column.children) - (ROW_HEIGHT / 2)
            column.height = height
            self.scroll_grid.height = max(self.scroll_grid.height, height)


class ChordDiagramApp(App):
    def build(self):
        return ChordDiagram()


if __name__ == "__main__":
    ChordDiagramApp().run()


