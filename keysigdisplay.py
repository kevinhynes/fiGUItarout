from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import InstructionGroup, Color
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.animation import Animation

from markers import Marker
from colors import white, black, gray, rainbow, reds, blues
from music_constants import chrom_scale, chrom_scale_no_acc, scale_degrees

import guitarpro
import time
from typing import List
from functools import partial
from threading import Thread

scale_texts = {
    "": chrom_scale,
    "Notes": chrom_scale,
    "Notes - No Accidentals": chrom_scale_no_acc,
    "Scale Degrees": scale_degrees}

scale_highlights = {
    "": 0b111111111111,
    "All": 0b111111111111,
    "R": 0b100000000000,
    "R, 3": 0b100110000000,
    "R, 5": 0b100000110000,
    "R, 3, 5": 0b100110110000,
    }



class KeySigDisplay(FloatLayout):
    root_note_idx = NumericProperty(0)
    mode_filter = NumericProperty(0b111111111111)
    box_x = NumericProperty(0)
    box_y = NumericProperty(0)
    box_pos = ReferenceListProperty(box_x, box_y)
    scale_text = StringProperty("")
    notes_to_highlight = StringProperty("")
    notes_or_octaves = StringProperty("")

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
    anim_props = ReferenceListProperty(m0_anim_prop, m1_anim_prop, m2_anim_prop, m3_anim_prop,
                                       m4_anim_prop, m5_anim_prop, m6_anim_prop, m7_anim_prop,
                                       m8_anim_prop, m9_anim_prop, m10_anim_prop, m11_anim_prop)

    m0_hit_prop = NumericProperty(0)
    m1_hit_prop = NumericProperty(0)
    m2_hit_prop = NumericProperty(0)
    m3_hit_prop = NumericProperty(0)
    m4_hit_prop = NumericProperty(0)
    m5_hit_prop = NumericProperty(0)
    m6_hit_prop = NumericProperty(0)
    m7_hit_prop = NumericProperty(0)
    m8_hit_prop = NumericProperty(0)
    m9_hit_prop = NumericProperty(0)
    m10_hit_prop = NumericProperty(0)
    m11_hit_prop = NumericProperty(0)
    hit_props = ReferenceListProperty(m0_hit_prop, m1_hit_prop, m2_hit_prop, m3_hit_prop,
                                      m4_hit_prop, m5_hit_prop, m6_hit_prop, m7_hit_prop,
                                      m8_hit_prop, m9_hit_prop, m10_hit_prop, m11_hit_prop, )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_markers = InstructionGroup()
        self._add_markers()
        self.canvas.add(self.note_markers)
        self.stopped = False
        self.play_instrs = []

    def _add_markers(self):
        for i in range(12):
            self.note_markers.add(Marker())

    def update_markers(self):
        x, y = self.ids.box.pos
        w, h = self.ids.box.size
        r1 = h / 2
        r2 = r1 * 0.9
        rdiff = r1 - r2
        mask = 2048
        for i, marker in enumerate(self.note_markers.children):
            c1x, c1y = x + w / 12 * i, y
            c2x, c2y = c1x + rdiff, c1y + rdiff
            included = mask & self.mode_filter
            highlighted = mask & scale_highlights[self.notes_to_highlight]
            mask >>= 1
            if self.scale_text == "Scale Degrees":
                note_idx = i
            else:
                note_idx = (self.root_note_idx + i) % 12

            note_text = scale_texts[self.scale_text][note_idx]

            if self.notes_or_octaves == "Notes":
                color = rainbow[i]
            else:
                color = rainbow[0]
            color_idx = i
            marker.update(i, note_text, c1x, c1y, r1, c2x, c2y, r2, included, highlighted, color)

    def on_size(self, instance, value):
        width, height = self.size
        target_ratio = 12
        if width / height > target_ratio:
            self.ids.box.height = height
            self.ids.box.width = height * target_ratio
        else:
            self.ids.box.width = width
            self.ids.box.height = width / target_ratio

    def on_box_pos(self, instance, value):
        self.update_markers()

    def on_root_note_idx(self, instance, value):
        self.update_markers()

    def on_mode_filter(self, instance, value):
        self.update_markers()

    def on_scale_text(self, *args):
        self.update_markers()

    def on_notes_to_highlight(self, *args):
        self.update_markers()

    def on_notes_or_octaves(self, *args):
        self.update_markers()

    ### SONG PLAYING METHODS
    def prep_play(self, flat_song: List[List[guitarpro.models.Measure]], track_num=0, tempo_mult=1):
        flat_track = flat_song[track_num]
        self.build_play_instr(flat_track, tempo_mult)

    def build_play_instr(self, flat_track: List[guitarpro.models.Measure], tempo_mult: float) -> None:
        # Build list of notes to play length of that beat in seconds.
        play_instrs = []
        for gp_measure in flat_track:
            for gp_voice in gp_measure.voices[:-1]:
                for gp_beat in gp_voice.beats:
                    beat_instr = self.build_beat_instr(gp_beat, tempo_mult)
                    play_instrs.append(beat_instr)

        # Eliminate faulty ghost notes.
        for i, beat_instr in enumerate(play_instrs):
            for note_idx, val in enumerate(beat_instr.notes):
                if val == -2:
                    prev_beat_instr = play_instrs[i-1]
                    beat_instr.notes[note_idx] = prev_beat_instr.notes[note_idx]
        self.play_instrs = play_instrs

    def build_beat_instr(self, gp_beat: guitarpro.models.Beat, tempo_mult: float):
        tempo = gp_beat.voice.measure.tempo.value
        spb = 60 / (tempo * tempo_mult)
        percent_quarter_note = 4 / gp_beat.duration.value
        percent_quarter_note *= (gp_beat.duration.tuplet.times / gp_beat.duration.tuplet.enters)
        if gp_beat.duration.isDotted:
            percent_quarter_note *= 3 / 2
        elif gp_beat.duration.isDoubleDotted:
            percent_quarter_note *= 7 / 4
        seconds = spb * percent_quarter_note
        beat_instr = KeySigDisplayBeat()
        beat_instr.seconds = seconds
        for gp_note in gp_beat.notes:
            octave, note_idx = divmod(gp_note.realValue, 12)
            beat_instr.notes[note_idx] = 1
            if gp_note.effect.ghostNote or gp_note.type.name == 'tie':
                beat_instr.notes[note_idx] = -2
        return beat_instr

    def play_thread(self, lead_in):
        # The GuitarPro songs' tempo are of form BPM where the B(eat) is always a quarter note.
        thread = Thread(target=partial(self._play_thread_animation, lead_in), daemon=True)
        thread.start()

    def _play_thread_animation(self, lead_in):
        self.stopped = False
        markers = self.note_markers.children
        anim_props = self.anim_props
        idx = 0
        time.sleep(lead_in)
        start = time.time()
        goal = start
        while not self.stopped:
            if idx == len(self.play_instrs):
                return
            beat_instr = self.play_instrs[idx]
            seconds = beat_instr.seconds
            for i, val in enumerate(beat_instr.notes):
                if val == 1:
                    # note_idx = (self.root_note_idx + i) % 12
                    note_idx = (i - self.root_note_idx) % 12
                    self.anim_props[note_idx] = 0
                    # Using dict unpacking to access the right property...
                    anim = Animation(**{'m{}_anim_prop'.format(note_idx): 1}, duration=seconds)
                    anim.bind(on_start=markers[note_idx].initiate_animation)
                    anim.bind(on_progress=markers[note_idx].update_animation)
                    anim.bind(on_complete=markers[note_idx].end_animation)
                    hit_anim = Animation(**{'m{}_anim_prop'.format(note_idx): 1},
                                         duration=min(0.125, seconds))
                    hit_anim.bind(on_start=markers[note_idx].initiate_hit_animation)
                    hit_anim.bind(on_progress=markers[note_idx].update_hit_animation)
                    hit_anim.bind(on_complete=markers[note_idx].end_hit_animation)
                    hit_anim.start(self)
                    anim.start(self)
            goal += seconds
            idx += 1
            time.sleep(max(goal - time.time(), 0))

    def stop(self):
        self.stopped = True


class KeySigDisplayBeat:
    def __init__(self):
        self.seconds = 0
        self.notes = [-1] * 12


class KeySigDisplayApp(App):
    def build(self):
        return KeySigDisplay()


if __name__ == "__main__":
    KeySigDisplayApp().run()