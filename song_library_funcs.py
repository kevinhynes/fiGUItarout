import sqlite3
from typing import List, Tuple


# Create the database and table.
def create_song_lib_db():
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS SongLibrary")
        cursor.execute("""CREATE TABLE IF NOT EXISTS SongLibrary(
                        Artist TEXT,
                        Album TEXT,
                        Title TEXT,
                        Filepath TEXT)
                        """)
        return


# Queries.
def get_all_songs() -> List:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Artist, Title FROM SongLibrary")
        rows = cursor.fetchall()
        return rows


def get_songs_by_artist(artist: str) -> List:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM SongLibrary WHERE Artist = ?", (artist,))
        rows = cursor.fetchall()
        return rows


def get_artists() -> List[str]:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT Artist FROM SongLibrary")
        rows = cursor.fetchall()
        str_list = [tup[0] for tup in rows]
        return str_list


def get_albums_by_artist(artist: str) -> List[str]:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT Album FROM SongLibrary WHERE Artist = ?", (artist,))
        rows = cursor.fetchall()
        str_list = [tup[0] for tup in rows]
        return str_list
    

def get_songs_on_album(artist: str, album: str) -> List[str]:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT Title FROM SongLibrary
                       WHERE Artist = ? AND Album = ?""", (artist, album))
        rows = cursor.fetchall()
        str_list = [tup[0] for tup in rows]
        return str_list


def get_saved_song_file(artist: str, album: str, song: str) -> str:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT Filepath FROM SongLibrary
                          WHERE Artist = ? AND Album = ? AND Title = ?""", (artist, album, song))
        rows = cursor.fetchall()
        str_list = [tup[0] for tup in rows]
        return str_list[0]


# Write to database.
def save_song_to_library(artist: str, album: str, title: str, filepath: str) -> None:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO SongLibrary (Artist, Album, Title, Filepath)
                          VALUES (?, ?, ?, ?)""", (artist, album, title, filepath))
        return


# create_song_lib_db()