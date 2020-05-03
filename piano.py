from kivy.app import App
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty, ReferenceListProperty
from kivy.graphics import InstructionGroup, Color, Line, Rectangle
from kivy.animation import Animation

from music_constants import chrom_scale, chrom_scale_no_acc, scale_degrees, standard_tuning, scale_highlights
from markers import Marker
from colors import black, white, rainbow, octave_colors

import time
import guitarpro
from typing import List
from functools import partial
from threading import Thread


scale_texts = {
    None: chrom_scale,
    "": chrom_scale,
    "Notes": chrom_scale,
    "Notes - No Accidentals": chrom_scale_no_acc,
    "Scale Degrees": scale_degrees}

class Piano(FloatLayout):
    keyboard_pos = ListProperty()
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b101011010101)
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")
    tuning = ListProperty(standard_tuning)

    m0_anim_prop = NumericProperty(0)
    m1_anim_prop = NumericProperty(0)
    m2_anim_prop = NumericProperty(0)
    m3_anim_prop = NumericProperty(0)
    m4_anim_prop = NumericProperty(0)
    m5_anim_prop = NumericProperty(0)
    m6_anim_prop = NumericProperty(0)
    m7_anim_prop = NumericProperty(0)
    m8_anim_prop = NumericProperty(0)
    m9_anim_prop = NumericProperty(0)
    m10_anim_prop = NumericProperty(0)
    m11_anim_prop = NumericProperty(0)

    m12_anim_prop = NumericProperty(0)
    m13_anim_prop = NumericProperty(0)
    m14_anim_prop = NumericProperty(0)
    m15_anim_prop = NumericProperty(0)
    m16_anim_prop = NumericProperty(0)
    m17_anim_prop = NumericProperty(0)
    m18_anim_prop = NumericProperty(0)
    m19_anim_prop = NumericProperty(0)
    m20_anim_prop = NumericProperty(0)
    m21_anim_prop = NumericProperty(0)
    m22_anim_prop = NumericProperty(0)
    m23_anim_prop = NumericProperty(0)

    m24_anim_prop = NumericProperty(0)
    m25_anim_prop = NumericProperty(0)
    m26_anim_prop = NumericProperty(0)
    m27_anim_prop = NumericProperty(0)
    m28_anim_prop = NumericProperty(0)
    m29_anim_prop = NumericProperty(0)
    m30_anim_prop = NumericProperty(0)
    m31_anim_prop = NumericProperty(0)
    m32_anim_prop = NumericProperty(0)
    m33_anim_prop = NumericProperty(0)
    m34_anim_prop = NumericProperty(0)
    m35_anim_prop = NumericProperty(0)

    m36_anim_prop = NumericProperty(0)
    m37_anim_prop = NumericProperty(0)
    m38_anim_prop = NumericProperty(0)
    m39_anim_prop = NumericProperty(0)
    m40_anim_prop = NumericProperty(0)
    m41_anim_prop = NumericProperty(0)
    m42_anim_prop = NumericProperty(0)
    m43_anim_prop = NumericProperty(0)
    m44_anim_prop = NumericProperty(0)
    m45_anim_prop = NumericProperty(0)
    m46_anim_prop = NumericProperty(0)
    m47_anim_prop = NumericProperty(0)

    m48_anim_prop = NumericProperty(0)
    m49_anim_prop = NumericProperty(0)
    m50_anim_prop = NumericProperty(0)
    m51_anim_prop = NumericProperty(0)
    m52_anim_prop = NumericProperty(0)
    m53_anim_prop = NumericProperty(0)
    m54_anim_prop = NumericProperty(0)
    m55_anim_prop = NumericProperty(0)
    m56_anim_prop = NumericProperty(0)
    m57_anim_prop = NumericProperty(0)
    m58_anim_prop = NumericProperty(0)
    m59_anim_prop = NumericProperty(0)

    anim_props = ReferenceListProperty(m0_anim_prop, m1_anim_prop, m2_anim_prop, m3_anim_prop,
                                       m4_anim_prop, m5_anim_prop, m6_anim_prop, m7_anim_prop,
                                       m8_anim_prop, m9_anim_prop, m10_anim_prop, m11_anim_prop,

                                       m12_anim_prop, m13_anim_prop, m14_anim_prop, m15_anim_prop,
                                       m16_anim_prop, m17_anim_prop, m18_anim_prop, m19_anim_prop,
                                       m20_anim_prop, m21_anim_prop, m22_anim_prop, m23_anim_prop,

                                       m24_anim_prop, m25_anim_prop, m26_anim_prop, m27_anim_prop,
                                       m28_anim_prop, m29_anim_prop, m30_anim_prop, m31_anim_prop,
                                       m32_anim_prop, m33_anim_prop, m34_anim_prop, m35_anim_prop,

                                       m36_anim_prop, m37_anim_prop, m38_anim_prop, m39_anim_prop,
                                       m40_anim_prop, m41_anim_prop, m42_anim_prop, m43_anim_prop,
                                       m44_anim_prop, m45_anim_prop, m46_anim_prop, m47_anim_prop,

                                       m48_anim_prop, m49_anim_prop, m50_anim_prop, m51_anim_prop,
                                       m52_anim_prop, m53_anim_prop, m54_anim_prop, m55_anim_prop,
                                       m56_anim_prop, m57_anim_prop, m58_anim_prop, m59_anim_prop)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Rectangle()
        self.key_outlines = InstructionGroup()
        self.black_keys = InstructionGroup()
        self.note_markers = InstructionGroup()
        self.canvas.add(white)
        self.canvas.add(self.background)
        self.canvas.add(black)
        self.canvas.add(self.key_outlines)
        self.canvas.add(self.black_keys)
        self.canvas.add(self.note_markers)
        self.key_midpoints = []        # For placing note markers.
        self.black_key_midpoints = []  # For placing black keys.
        self.rel_marker_heights = [0.1, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.5, 0.1, 0.5, 0.1]
        self.note_vals = [note_val for note_val in range(24, 24 + 61)]
        self.bind(pos=self.update_canvas, size=self.update_canvas)

        self.stopped = False

    def on_kv_post(self, *args):
        self._calc_key_midpoints()
        self._add_markers()
        self._add_key_outlines()
        self._add_black_keys()

    def _calc_key_midpoints(self):
        key_midpoints = []
        key_width = 1 / 35
        black_key_locs = {1, 2, 4, 5, 6}
        for i in range(1, 36):
            key_midpoints += [(i / 35) - key_width / 2]
            if i % 7 in black_key_locs:
                key_midpoints += [i / 35]
        self.key_midpoints = key_midpoints

    def _add_markers(self):
        for i in range(60):
            marker = Marker()
            self.note_markers.add(marker)

    def _add_key_outlines(self):
        x, y = self.ids.keyboard.pos
        w, h = self.ids.keyboard.size
        step = w / 35
        for i in range(35):
            outline = Line(rectangle=(x + step * i, y, step, h))
            self.key_outlines.add(outline)

    def _add_black_keys(self):
        # Total width = 5 octaves with 7 white keys each (black keys don't add to width).
        black_key_midpoints = []
        for i in range(35):
            if i % 7 in (1, 2, 4, 5, 6):
                black_key_midpoints += [i / 35]
                self.black_keys.add(Rectangle())
        self.black_key_midpoints = black_key_midpoints

    def update_canvas(self, *args):
        self.update_background()
        self.update_key_outlines()
        self.update_black_keys()
        self.update_note_markers()

    def update_background(self):
        self.background.pos = self.ids.keyboard.pos
        self.background.size = self.ids.keyboard.size

    def update_key_outlines(self):
        w, h = self.ids.keyboard.size
        x, y = self.ids.keyboard.pos
        step = w / 35
        key_outlines = [obj for obj in self.key_outlines.children if isinstance(obj, Line)]
        for i, outline in enumerate(key_outlines):
            outline.rectangle = (x + step * i, y, step, h)

    def update_black_keys(self):
        white_key_width = self.ids.keyboard.width / 35
        black_key_width = white_key_width * 0.55
        black_keys = [obj for obj in self.black_keys.children if isinstance(obj, Rectangle)]
        for center_x, black_key in zip(self.black_key_midpoints, black_keys):
            x = center_x * self.ids.keyboard.width - (black_key_width / 2)
            y = self.ids.keyboard.y + (self.ids.keyboard.height / 3)
            black_key.pos = (x, y)
            black_key.size = (black_key_width, self.ids.keyboard.height * (2/3))

    def update_note_markers(self):
        x, y = self.ids.keyboard.pos
        width, height = self.ids.keyboard.size
        key_width = width / 35
        r1 = (key_width / 2) * 0.65
        r2 = r1 * 0.9
        rdiff = r1 - r2
        for i, (note_val, marker) in enumerate(zip(self.note_vals, self.note_markers.children)):
            key_midpoint = self.key_midpoints[i]
            c1x = x + (key_midpoint * width) - r1
            c1y = y + self.rel_marker_heights[i % 12] * height
            c2x, c2y = c1x + rdiff, c1y + rdiff

            octave, note_idx = divmod(note_val, 12)
            included = int(bin(self.mode_filter)[2:][note_idx - self.root_note_idx])
            highlighted = int(bin(scale_highlights[self.notes_to_highlight])[2:][note_idx - self.root_note_idx])

            if self.notes_or_octaves == "Notes":
                color_idx = note_idx - self.root_note_idx
                color = rainbow[color_idx]
            else:
                # print(note_val, divmod(note_val, 12))
                color_idx = (octave - 1) % 8
                color = octave_colors[color_idx]

            if self.scale_text == "Scale Degrees":
                note_idx -= self.root_note_idx

            note_text = scale_texts[self.scale_text][note_idx]

            marker.update(i, note_text, c1x, c1y, r1, c2x, c2y, r2, included, highlighted, color)

    def on_size(self, *args):
        """Resize the BoxLayout that holds the fretboard to maintain a guitar neck aspect ratio."""
        target_ratio = 60 / 7
        width, height = self.size
        # Check which size is the limiting factor.
        if width / height > target_ratio:
            # Window is "wider" than target, so the limitation is the height.
            self.ids.keyboard.height = height
            self.ids.keyboard.width = height * target_ratio
        else:
            self.ids.keyboard.width = width
            self.ids.keyboard.height = width / target_ratio

    def on_keyboard_pos(self, *args):
        self.update_canvas()

    def on_root_note_idx(self, *args):
        self.update_canvas()

    def on_mode_filter(self, *args):
        self.update_canvas()

    def on_scale_text(self, *args):
        self.update_note_markers()

    def on_notes_to_highlight(self, *args):
        self.update_note_markers()

    def on_notes_or_octaves(self, *args):
        self.update_note_markers()

    def on_tuning(self, *args):
        # Piano will always use C as lowest note.
        lowest_guitar_octave, note_idx = divmod(self.tuning[0], 12)
        lowest_piano_octave, _ = divmod(self.note_vals[0], 12)
        if lowest_guitar_octave != lowest_piano_octave:
            low_c_note_val = lowest_guitar_octave * 12
            self.note_vals = [note_val for note_val in range(low_c_note_val, low_c_note_val + 61)]
            self.update_note_markers()

    ### SONG PLAYING METHODS
    def prep_play(self, flat_song: List[List[guitarpro.models.Measure]], track_num=0, tempo_mult=1):
        flat_track = flat_song[track_num]
        self.build_play_instrs(flat_track, tempo_mult)

    def build_play_instrs(self, flat_track: List[guitarpro.models.Measure], tempo_mult: float):
        play_instrs = []
        for gp_measure in flat_track:
            for gp_voice in gp_measure.voices[:-1]:
                for gp_beat in gp_voice.beats:
                    beat_instr = self.build_beat_instr(gp_beat, tempo_mult)
                    play_instrs.append(beat_instr)

        for i, beat_instr in enumerate(play_instrs):
            for key_idx, key_val in enumerate(beat_instr.keys):
                if key_val == -2:
                    play_instrs[i].keys[key_idx] = 1

        self.play_instrs = play_instrs

    def build_beat_instr(self, gp_beat: guitarpro.models.Beat, tempo_mult: float):
        tempo = gp_beat.voice.measure.tempo.value
        spb = 60 / (tempo * tempo_mult)
        percent_quarter_note = 4 / gp_beat.duration.value
        percent_quarter_note *= (gp_beat.duration.tuplet.times / gp_beat.duration.tuplet.enters)
        if gp_beat.duration.isDotted:
            percent_quarter_note *= 3/2
        elif gp_beat.duration.isDoubleDotted:
            percent_quarter_note *= 7/ 4
        seconds = spb * percent_quarter_note

        keys = [-1] * 60
        for gp_note in gp_beat.notes:
            if self.note_vals[0] <= gp_note.realValue <= self.note_vals[-1]:
                key_idx = gp_note.realValue - self.note_vals[0]
                if gp_note.effect.ghostNote or gp_note.type.name == 'tie':
                    keys[key_idx] = -2
                else:
                    keys[key_idx] = 1
        return PianoBeat(seconds=seconds, keys=keys)

    def play_thread(self, lead_in):
        # The GuitarPro songs' tempo are of form BPM where the B(eat) is always a quarter note.
        thread = Thread(target=partial(self._play_thread_animation, lead_in), daemon=True)
        thread.start()

    def _play_thread_animation(self, lead_in):
        self.stopped = False
        markers = self.note_markers.children
        idx = 0
        time.sleep(lead_in)
        start = time.time()
        goal = start
        while not self.stopped:
            if idx == len(self.play_instrs):
                return
            beat_instr = self.play_instrs[idx]
            seconds = beat_instr.seconds
            for key_idx, key in enumerate(beat_instr.keys):
                if key == 1:
                    self.anim_props[key_idx] = 0
                    anim = Animation(**{'m{}_anim_prop'.format(key_idx): 1}, duration=seconds)
                    anim.bind(on_start=markers[key_idx].initiate_animation)
                    anim.bind(on_progress=markers[key_idx].update_animation)
                    anim.bind(on_complete=markers[key_idx].end_animation)
                    anim.start(self)
            goal += seconds
            idx += 1
            time.sleep(max(goal - time.time(), 0))

    def stop(self):
        self.stopped = True


class PianoBeat:
    def __init__(self, seconds=0, keys=[-1]*60):
        self.seconds = seconds
        self.keys = keys


class PianoApp(App):
    def build(self):
        return Piano()


if __name__ == "__main__":
    PianoApp().run()