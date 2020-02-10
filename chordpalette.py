from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line

from music_constants import chrom_scale, standard_tuning, chord_names_to_nums, \
    basic_chord_names_to_nums
from chord_voicing_generator import get_chord_voicings_from_query

Builder.load_file('chorddiagram.kv')
from chorddiagram import ChordDiagram


class BackGroundColorWidget(Widget):
    pass


class ChordPaletteDisplay(FloatLayout):
    pass


class ChordPalette(ScrollView, BackGroundColorWidget):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    note_idxs = ListProperty([0, 0, 0, 0, 0, 0, 0])
    tuning = ListProperty(standard_tuning)
    box = ObjectProperty(None)
    root_string_option = StringProperty("All")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(root_note_idx=self.update_note_idxs, mode_filter=self.update_note_idxs)

    def on_kv_post(self, base_widget):
        self.titlebar = ChordPaletteTitleBar()
        self.box.add_widget(self.titlebar)
        Clock.schedule_once(self.update_note_idxs, 0)

    def update_note_idxs(self, *args):
        self.note_idxs = []
        mode_str = bin(self.mode_filter)[2:]
        for i, bit in enumerate(mode_str):
            if bit == '1':
                note_idx = (self.root_note_idx + i) % 12
                self.note_idxs.append(note_idx)
        print(len(self.note_idxs), self.note_idxs)
        self.titlebar.update_headers(self.note_idxs)

    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.x, touch.y):
    #         if self.mode_filter == 0b101011010101:
    #             self.mode_filter = 0b101010010100
    #         else:
    #             self.mode_filter = 0b101011010101
    #         # self.root_note_idx += 1
    #         return True
    #     return super().on_touch_down(touch)

    def add_row(self, *args):
        chord_row = ChordPaletteRow(width=self.titlebar.width, note_idxs=self.note_idxs,
                                    root_note_idx=self.root_note_idx, mode_filter=self.mode_filter)
        self.box.height += chord_row.height
        self.box.add_widget(chord_row)
        return chord_row

    def build_basic_chord_row(self, *args):
        selected_rows = [child for child in self.box.children if
                         hasattr(child, 'selected') and child.selected is True]
        if not selected_rows:
            selected_rows.append(self.add_row())
        for row in selected_rows:
            chord_diagrams = row.children[::-1][1:]
            self.update_row(self.note_idxs, chord_diagrams, basic_chord_names_to_nums)

    def update_row(self, note_idxs, chord_diagrams, chord_dict):
        for cd, note_idx in zip(chord_diagrams, note_idxs):
            cd.note_idx = note_idx
            for chord_name, chord_num in chord_dict.items():
                cd.chord_name = chord_name
                cd.chord_num = chord_num
                if cd.is_chord_in_key():
                    cd.voicing = self.get_chord_diagram_voicing(chord_num)
                    break

    def get_chord_diagram_voicing(self, chord_num):
        sql = """SELECT voicing FROM ChordVoicings WHERE tuning = ?
                 AND chord_num = ?"""
        sql_params = [str(self.tuning), chord_num]
        if self.voicing_option != "All":
            sql += " AND master_voicing = voicing"
        if self.root_string_option != "All":
            sql += " AND root_string = ?"
            sql_params.append(int(self.root_string_option))
        voicings = get_chord_voicings_from_query(self.tuning, sql, sql_params)
        print(len(voicings))
        default = [None, 3, 2, 0, 1, 0]
        return voicings[0] if voicings else default


class ChordPaletteTitleBar(BoxLayout, BackGroundColorWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_headers(self, note_idxs):
        # Number of columns in title bar may change.
        # Children of BoxLayout are displayed right to left.
        child_count = len(note_idxs) + 1
        while len(self.children) > child_count:
            self.remove_widget(self.children[0])
        while len(self.children) < child_count:
            self.add_widget(Label())
        for label, note_idx in zip(reversed(self.children[:-1]), note_idxs):
            label.text = chrom_scale[note_idx]
        self.children[-1].text = "Chord Palette"


class ChordPaletteRow(BoxLayout, BackGroundColorWidget):

    def __init__(self, note_idxs, root_note_idx, mode_filter, **kwargs):
        super().__init__(**kwargs)
        select_button = Button(text="Select Row")
        select_button.bind(on_press=self.select)
        self.add_widget(select_button)
        self.selected = False
        for i, note_idx in enumerate(note_idxs):
            self.add_widget(ChordDiagram(root_note_idx=root_note_idx,
                                         mode_filter=mode_filter,
                                         note_idx=note_idx))

    def select(self, *args):
        if not self.selected:
            self.outline_color = Color(1, 0, 0, 1)
            self.outline = Line(rectangle=(*self.pos, *self.size), width=2, dash_offset=2)
            self.canvas.add(self.outline_color)
            self.canvas.add(self.outline)
            self.selected = True
        else:
            self.canvas.remove(self.outline_color)
            self.canvas.remove(self.outline)
            self.selected = False


class ChordPaletteOptionsBar(FloatLayout):
    root_string_option = StringProperty('All')
    voicing_option = StringProperty('All')

    def update_root_string_option(self, radio_button, value):
        if radio_button.state == 'down':
            self.root_string_option = value

    def update_voicing_option(self, radio_button, value):
        if radio_button.state == 'down':
            self.voicing_option = value

    def on_root_string_option(self, *args):
        print(self.root_string_option, args)

    def on_voicing_option(self, *args):
        print(self.root_string_option, args)


class ChordPaletteApp(App):
    def build(self):
        return ChordPaletteDisplay()


if __name__ == "__main__":
    ChordPaletteApp().run()
