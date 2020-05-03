from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
Window.maximize()
from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from songlibrary import SongLibraryPopup
from spotifylogin import SpotifyLoginPopup
import song_library_funcs as slf

import spotipy

Builder.load_file("style.kv")
Builder.load_file("slideupmenu.kv")
Builder.load_file("scaleoptionschooser.kv")
Builder.load_file("keysigchooser.kv")
Builder.load_file("keysigdisplay.kv")
Builder.load_file("keysigtitlebar.kv")
Builder.load_file("chorddisplay.kv")
Builder.load_file("metronome.kv")
Builder.load_file("tuner.kv")
Builder.load_file("numfretschanger.kv")
Builder.load_file("fretboard.kv")
Builder.load_file("piano.kv")
Builder.load_file("instrumentrack.kv")
Builder.load_file("songbuilder.kv")


class MainPage(FloatLayout):
    spt_conn = ObjectProperty()
    songplayer = ObjectProperty()
    songbuilder = ObjectProperty()
    fretboard = ObjectProperty()
    piano = ObjectProperty()
    keysigtitlebar = ObjectProperty

    def __init__(self,  **kwargs):
        self.device_id = None
        super().__init__(**kwargs)

    def show_song_library(self, *args):
        self.song_library_popup = SongLibraryPopup()
        self.song_library_popup.open()

    def show_spotify_login_popup(self, *args):
        self.spotify_log_in_popup = SpotifyLoginPopup(login_func=self.log_in_to_spotify)
        self.spotify_log_in_popup.open()

    def log_in_to_spotify(self, username):
        self.spotify_log_in_popup.dismiss()
        scope = 'user-library-read user-modify-playback-state'
        token = spotipy.util.prompt_for_user_token(username, scope,
                                                   client_id="b8a306fd829d4ea4a757cb1411baf0eb",
                                                   client_secret="a00b878607994e4fbcc08cf9c053bd21",
                                                   redirect_uri="http://localhost:5000/callback/spotify")
        self.spt_conn = spotipy.Spotify(auth=token)
        self.set_device_id()

    def set_device_id(self):
        results = self.spt_conn.devices()
        for device in results['devices']:
            if device['type'] == 'Computer':
                self.device_id = device['id']
                break

    def play(self, songplayer_widget):
        gp_song = songplayer_widget.gp_song
        flat_song = songplayer_widget.flat_song
        artist, album, title = gp_song.artist.title(), gp_song.album.title(), gp_song.title.title()
        lead_in = slf.get_saved_song_lead_in(artist, album, title)
        tempo_mult = slf.get_saved_song_tempo_multiplier(artist, album, title)
        if songplayer_widget is self.songplayer:
            # Prepare data to be played.
            self.keysigtitlebar.prep_play(flat_song, 0, tempo_mult)
            self.fretboard.prep_play(flat_song, 0, tempo_mult)
            self.piano.prep_play(flat_song, 0, tempo_mult)
            songplayer_widget.prep_play()
            # Start playing on Spotify, then play all the widgets.
            self.play_gp_song_on_spotify(songplayer_widget.gp_song)
            songplayer_widget.play()
            self.keysigtitlebar.play(lead_in)
            self.fretboard.play(lead_in)
            self.piano.play_thread(lead_in)
        if songplayer_widget is self.songbuilder:
            songplayer_widget.prep_play()
            self.play_gp_song_on_spotify(songplayer_widget.gp_song)
            songplayer_widget.play()

    def stop(self, songplayer_widget):
        if songplayer_widget is self.songplayer:
            print("stop SongPlayer")
            songplayer_widget.stop()
            self.keysigtitlebar.stop()
            self.fretboard.stop()
            self.piano.stop()
        if songplayer_widget is self.songbuilder:
            print("stop SongBuilder")
            songplayer_widget.stop()

    def play_gp_song_on_spotify(self, gp_song):
        artist, album, title = gp_song.artist, gp_song.album, gp_song.title
        self.play_on_spotify(artist, album, title)

    def play_on_spotify(self, artist, album, title):
        track_uri = self.get_track_uri(artist, album, title)
        if track_uri:
            self.spt_conn.start_playback(uris=[track_uri], device_id=self.device_id)

    def get_track_uri(self, artist, album, title):
        artist, album, title = artist.lower(), album.lower(), title.lower()
        if title == "mouths like sidewinder missles":
            title = "mouths like sidewinder misssles"
        if title == "coure d'alene":
            title = "coeur d'alene"
        if title == "but, it's far better to learn":
            title = "it's far better to learn"
        if title == "it's so simple!":
            title = "it's so simple"
        if title == "stairway to heaven":
            title = "stairway to heaven - 2012 remaster"

        print(f"Searching for {artist + ' ' + album}")
        results = self.spt_conn.search(artist + ' ' + album)
        for track in results['tracks']['items']:
            print(track['name'])
            if track['name'].lower() == title:
                print(f"\tFound {track['name']} with artist and album")
                return track['uri']

        print(f"Searching for {artist + ' ' + title}")
        results = self.spt_conn.search(artist + " " + title)
        for track in results['tracks']['items']:
            print(track['name'])
            if track['name'].lower() == title:
                print(f"\tFound {track['name']} with artist and title")
                return track['uri']

        print(f"Searching for {artist}")
        results = self.spt_conn.search(artist)
        for track in results['tracks']['items']:
            print(track['name'])
            if track['name'].lower() == title:
                print(f"\tFound {track['name']} with artist and title")
                return track['uri']

        print(f"\tNo exact match found for {artist} - {title}")
        results_log = open('./results_log.txt', 'w')
        results_log.write(str(results))
        return None


class MainApp(App):

    def play(self, songplayer_widget):
        self.mainpage.play(songplayer_widget)

    def stop(self, songplayer_widget):
        self.mainpage.stop(songplayer_widget)

    def build(self):
        self.mainpage = MainPage()
        return self.mainpage


if __name__ == "__main__":
    MainApp().run()