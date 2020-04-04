from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.lang import Builder

import song_library_funcs as slf

Builder.load_file('songlibrary.kv')


class SongLibraryPopup(Popup):
    load_saved_file = ObjectProperty()


class SongLibrary(Carousel):
    load_saved_file = ObjectProperty()
    artist = StringProperty('')
    album = StringProperty('')
    song = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.artists_page = SongLibraryPage(name='Artists', carousel=self)
        self.albums_page = SongLibraryPage(name='Albums', carousel=self)
        self.songs_page = SongLibraryPage(name='Songs', carousel=self)
        for page in (self.artists_page, self.albums_page, self.songs_page):
            self.add_widget(page)

    def on_press(self, button):
        if self.current_slide.name == 'Artists':
            self.artist = button.text
            self.load_next(mode='next')
        elif self.current_slide.name == 'Albums':
            self.album = button.text
            self.load_next(mode='next')
        elif self.current_slide.name == 'Songs':
            self.song = button.text

    def on_artist(self, *args):
        albums = slf.get_albums_by_artist(self.artist)
        self.albums_page.update_list(albums)

    def on_album(self, *args):
        songs = slf.get_songs_on_album(self.artist, self.album)
        self.songs_page.update_list(songs)

    def on_song(self, *args):
        filepath, edit_instructions = slf.get_saved_song_info(self.artist, self.album, self.song)
        self.load_saved_file(filepath, edit_instructions)


class SongLibraryPage(FloatLayout):

    def __init__(self, name=None, carousel=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.carousel = carousel
        self.header = SongLibraryHeader(text=name.title())
        self.add_widget(self.header)
        if name == 'Artists':
            artists = slf.get_artists()
            self.update_list(artists)

    def update_list(self, str_list):
        buttons = [child for child in self.children if isinstance(child, Button)]
        while len(str_list) < len(buttons):
            self.remove_widget(self.children[-1])
            buttons.pop()

        prev_widget = self.header
        while len(str_list) > len(buttons):
            button = Button(size_hint=[None, None], size=[350, 50])
            button.top = prev_widget.y
            prev_widget.bind(y=button.setter('top'))
            buttons.append(button)
            self.add_widget(button)
            button.bind(on_press=self.carousel.on_press)
            prev_widget = button

        for child, text in zip(buttons, str_list):
            child.text = text


class SongLibraryHeader(Label):
    pass