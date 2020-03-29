from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('spotifylogin.kv')


class SpotifyLoginPopup(Popup):
    login_func = ObjectProperty()

    def __init__(self, **kwargs):
        self.instruction_text = """
        Log into your Spotify premium account using these instructions:
            1) Make sure you're logged into Spotify on your device.
            2) Enter your Spotify username below and press submit.
            3) If a new tab opened in your web browser:
                Copy and paste that URL into the terminal you're running this from.
                        (It's okay if the web page failed to load!)
            4) If no new tab opened, you already have a valid token.
            5) You're all set! 
        """
        super().__init__(**kwargs)
