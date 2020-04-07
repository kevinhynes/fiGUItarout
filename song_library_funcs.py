import sqlite3
from typing import List


# Create the database and table.
def create_song_lib_db():
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS SongLibrary")
        cursor.execute("""CREATE TABLE IF NOT EXISTS SongLibrary(
                        Artist TEXT,
                        Album TEXT,
                        Title TEXT,
                        Filepath TEXT,
                        EditInstructions TEXT,
                        LeadIn INT,
                        TempoMultiplier INT)
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

def get_saved_song_info(artist: str, album: str, title: str) -> List[str]:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT Filepath, EditInstructions FROM SongLibrary
                          WHERE Artist = ? AND Album = ? AND Title = ?""", (artist, album, title))
        rows = cursor.fetchall()  # -> [(str, str)]
        if not rows:
            return
        str_list = list(rows[0])
        return str_list

def get_saved_song_lead_in(artist: str, album: str, title: str) -> int:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT LeadIn FROM SongLibrary
                          WHERE Artist = ? AND Album = ? AND Title = ?""", (artist, album, title))
        rows = cursor.fetchall()
        if not rows:
            return
        print('lead_in', rows)
        return rows[0][0]

def get_saved_song_tempo_multiplier(artist: str, album: str, title: str) -> int:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT TempoMultiplier FROM SongLibrary
                          WHERE Artist = ? AND Album = ? AND Title = ?""", (artist, album, title))
        rows = cursor.fetchall()
        if not rows:
            return
        print('tempo_mult', rows)
        return rows[0][0]

# Write to database.
def save_song_to_library(artist: str, album: str, title: str, filepath: str, edit_instructions: str) -> None:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO SongLibrary (Artist, Album, Title, Filepath, 
                                                   EditInstructions, LeadIn, TempoMultiplier)
                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                 (artist, album, title, filepath, edit_instructions, 0, 1))
        return

def update_edit_instructions(artist: str, album: str, title: str, edit_instructions: str) -> None:
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE SongLibrary SET EditInstructions = ? 
                          WHERE Artist = ? AND Album = ? AND Title = ?""",
                          (edit_instructions, artist, album, title))


# def update_table():
#     with sqlite3.connect("song_library_DB.db") as connection:
#         cursor = connection.cursor()
#         cursor.execute("""UPDATE SongLibrary SET LeadIn = 8 WHERE Title = 'Blue'""")


def update_lead_in(seconds, artist, album, title):
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE SongLibrary SET LeadIn = ?
                          WHERE Artist = ? AND Album = ? AND Title = ?""",
                       (seconds, artist, album, title))


def update_tempo_multiplier(multiplier, artist, album, title):
    with sqlite3.connect("song_library_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE SongLibrary SET TempoMultiplier = ?
                          WHERE Artist = ? AND Album = ? AND Title = ?""",
                       (multiplier, artist, album, title))


if __name__ == "__main__":
    # update_lead_in(8.95,  'Saosin', 'S/T', "But, It'S Far Better To Learn")
    # update_tempo_multiplier(1.01,  'Saosin', 'S/T', "But, It'S Far Better To Learn")
    pass