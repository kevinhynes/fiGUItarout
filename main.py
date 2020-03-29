from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
Window.maximize()
# Window.size = (500, 300)
from kivy.clock import Clock
from songlibrary import SongLibraryPopup
from spotifylogin import SpotifyLoginPopup

import spotipy

Builder.load_file("style.kv")
Builder.load_file("slideupmenu.kv")
Builder.load_file("fretboarddisplay.kv")
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

    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

        # Clock.schedule_once(self.play_on_spotify, 5)

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

    def play_on_spotify(self, *args):
        results = self.spt_conn.search(q="blink 182")
        track_id = results['tracks']['items'][0]['id']
        self.spt_conn.start_playback(uris=['spotify:track:' + track_id])


class MainApp(App):
    def build(self):
        return MainPage()


if __name__ == "__main__":
    MainApp().run()