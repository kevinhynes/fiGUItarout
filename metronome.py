from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty
from kivy.graphics import Ellipse, Color, InstructionGroup
from kivy.animation import Animation


from threading import Thread, Event
import time, wave, pyaudio, math


class TitleBar(BoxLayout):

    def validate_text(self, text):
        bpm = ""
        i = 0
        while i < len(text) and text[i].isdigit():
            bpm += text[i]
            i += 1
        if bpm and 1 <= int(bpm) <= 300:
            bpm = int(bpm)
            self.metronome.bpm = bpm
        # In case bpm was invalid, out of range, or same value as before, make sure text is updated.
        self.metronome.bpm += 1
        self.metronome.bpm -= 1


class BeatMarker(InstructionGroup):

    def __init__(self, cx=1, cy=1, r=1, **kwargs):
        super().__init__(**kwargs)
        self.anim_color = Color(0, 1, 0, 0)
        self.anim_circle = Ellipse()
        self.color = Color(1, 1, 1, 0.5)
        self.marker = Ellipse()

        self.add(self.anim_color)
        self.add(self.anim_circle)
        self.add(self.color)
        self.add(self.marker)

        self.pos = cx, cy
        self.size = [2*r, 2*r]

    @property
    def pos(self):
        return self.pos

    @pos.setter
    def pos(self, pos):
        self.anim_circle.pos = pos
        self.marker.pos = pos

    @property
    def size(self):
        return self.size

    @size.setter
    def size(self, size):
        d, d = size
        self.r = d/2
        self.max_rdiff = self.r * 0.2
        self.anim_circle.size = size
        self.marker.size = size

    def update_animation(self, animation, metronome, progress):
        rdiff = progress * self.max_rdiff
        cx, cy = self.marker.pos
        self.anim_circle.pos = cx - rdiff, cy - rdiff
        self.anim_circle.size = [2 * (self.r + rdiff), 2 * (self.r + rdiff)]
        self.anim_color.a = progress

    def end_animation(self, animation, metronome):
        self.anim_color.a = 0
        # cx, cy = self.marker.pos
        # d, d = self.marker.size
        self.anim_circle.pos = self.marker.pos
        self.anim_circle.size = self.marker.size


class BeatBar(FloatLayout):
    num_beats = NumericProperty(4)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.beatmarkers = InstructionGroup()
        for i in range(self.num_beats):
            beatmarker = BeatMarker()
            self.beatmarkers.add(beatmarker)
        self.canvas.add(self.beatmarkers)

    def on_num_beats(self, instance, num_beats):
        while num_beats > len(self.beatmarkers.children):
            beatmarker = BeatMarker()
            self.beatmarkers.add(beatmarker)
        while num_beats < len(self.beatmarkers.children):
            self.beatmarkers.children.pop()
        self.update_beatmarkers()

    def on_size(self, *args):
        self.update_beatmarkers()

    def on_pos(self, *args):
        # Needed for slide up menu.
        self.update_beatmarkers()

    def update_beatmarkers(self):
        target_ratio = self.num_beats / 1
        aspect_ratio = self.width / self.height
        percent_radius = 0.6  # circle shouldn't take up the whole square
        if aspect_ratio > target_ratio:
            side = self.height
            r = side / 2 * percent_radius
            rdiff = side / 2 - r
            dx = (self.width - (self.num_beats * side)) / 2
            cx, cy = self.x + dx + rdiff, self.y + rdiff
            step_x = side
            for beatmarker in self.beatmarkers.children:
                beatmarker.pos = [cx, cy]
                beatmarker.size = [2*r, 2*r]
                cx += step_x
        else:
            side = self.width / self.num_beats
            r = side / 2 * percent_radius
            rdiff = side / 2 - r
            dy = (self.height - side) / 2
            cx, cy = self.x + rdiff, self.y + dy + rdiff
            step_x = side
            for beatmarker in self.beatmarkers.children:
                beatmarker.pos = [cx, cy]
                beatmarker.size = [2*r, 2*r]
                cx += step_x


############################################################################################
# Playing with some sound stuff here...
# Combination of NumPy and SciPy to write a sin wave .wav file.
# https://www.youtube.com/watch?v=lbV2SoeAggU nightstatic
import numpy as np
from scipy.io import wavfile
sps = 44100
freq_hz = 660.0
duration_s = 0.2
each_sample_number = np.arange(duration_s * sps)
waveform = np.sin(2 * np.pi * each_sample_number * freq_hz / sps)
waveform_quiet = waveform * 0.3
waveform_integers = np.int16(waveform_quiet * 32767)
# Write the .wav file
wavfile.write('sine.wav', sps, waveform_integers)


# simpleaudio can play NumPy arrays directly.
# import simpleaudio as sa
# Start playback
# play_obj = sa.play_buffer(waveform_integers, 1, 2, sps)
# Wait for playback to finish before exiting
# play_obj.wait_done()
############################################################################################


class Metronome(FloatLayout):
    needle_angle = NumericProperty(0)
    num_beats = NumericProperty(4)
    bpm = NumericProperty(200)

    def __init__(self, **kwargs):
        self.box = BoxLayout()
        self.beatbar = FloatLayout()
        self.buttonbar = BoxLayout()
        self.max_needle_angle = 30
        super().__init__(**kwargs)
        self.spb = 60 / self.bpm
        self.time_sig = 4

        self.sine_file = "./sine.wav"  # Written from NumPy array

        self.player = pyaudio.PyAudio()
        sine = wave.open(self.sine_file, "rb")
        self.sine_data = sine.readframes(2048)
        self.stream = self.player.open(
            format=self.player.get_format_from_width(sine.getsampwidth()),
            channels=sine.getnchannels(),
            rate=sine.getframerate(),
            output=True)

        self.stopped = True
        self.needle_animation = Animation()
        self.beatmarker_animation = Animation()

    def on_size(self, *args):
        target_ratio = 0.75
        width, height = self.size
        if width / height > target_ratio:
            self.box.height = height
            self.box.width = target_ratio * height
        else:
            self.box.width = width
            self.box.height = width / target_ratio

    def on_bpm(self, instance, bpm):
        self.spb = 60 / self.bpm
        self.stop()

    def increment_bpm(self, val):
        if 1 < self.bpm < 300:
            self.bpm += val

    def play(self, *args):
        if self.stopped:
            self.stopped = False
            thread = Thread(target=self._play, daemon=True)
            thread.start()

    def _play(self):
        start = time.time()
        delta = self.spb
        goal = start + delta
        forward = True
        while not self.stopped:
            beat_num = (time.time() - start) // delta
            self.animate_needle(self.spb, forward)
            self.animate_beatmarker(0.1, beat_num)
            self.stream.write(self.sine_data)
            time.sleep(goal - time.time())
            forward = not forward
            goal += delta

    def stop(self):
        if not self.stopped:
            self.beatmarker_animation.stop(self)
            self.needle_animation.stop(self)
            self.stopped = True
            self.needle_angle = 0

    def animate_needle(self, duration, forward):
        self.needle_animation.stop(self)
        if forward:
            self.needle_angle = -self.max_needle_angle
            self.needle_animation = Animation(needle_angle=self.max_needle_angle, duration=duration)
        else:
            self.needle_angle = self.max_needle_angle
            self.needle_animation = Animation(needle_angle=-self.max_needle_angle, duration=duration)
        self.needle_animation.start(self)

    def animate_beatmarker(self, duration, beat_num):
        self.beatmarker_animation.stop(self)
        self.beatmarker_animation = Animation(duration=duration)
        beat_idx = int(beat_num % self.num_beats)
        beatmarker = self.beatbar.beatmarkers.children[beat_idx]
        self.beatmarker_animation.bind(on_progress=beatmarker.update_animation)
        self.beatmarker_animation.bind(on_complete=beatmarker.end_animation)
        self.beatmarker_animation.start(self)


class MetronomeApp(App):
    def build(self):
        return Metronome()


if __name__ == "__main__":
    MetronomeApp().run()

