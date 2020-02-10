import sqlite3, itertools, collections, ast
from typing import List, DefaultDict
from music_constants import standard_tuning

chord_num_lookup = {
    'Major'     : 0b100010010000, 'Major 6': 0b100010010100, 'Major 7': 0b100010010001,
    'Major 9'   : 0b101010010001, 'Major 11': 0b101011010001,

    'Minor'     : 0b100100010000, 'Minor 6': 0b100100010100, 'Minor 7': 0b100100010010,
    'Minor 9'   : 0b101100010010, 'Minor 11': 0b101101010010, 'Minor Major 7': 0b100100010001,

    'Dominant 7': 0b100010010010, 'Dominant 9': 0b101010010010, 'Dominant 11': 0b101011010010,

    'Sus 2'     : 0b101000010000, 'Sus 4': 0b100001010000,

    'Diminished': 0b100100100000, 'Diminished 7': 0b100100100100,

    'Augmented' : 0b100010001000, 'Augmented 7': 0b100010001010,
    }


def chord_voicing_sort(voicing):
    '''
    Sort so that:
      1) voicings with a lot of intermittent string skipping come last
      2) 'fuller' chords come first: 6 strings - 5 strings - 4 strings...

    `voicing` is a list of length 6 where voicing[string_idx] = fret_num.

    If a string isn't played, fret_num is None.  Otherwise it is an integer.
    '''
    groups = list(itertools.groupby(voicing, key=type))
    if groups[-1][0].__name__ == 'NoneType':
        # 'full' chords rooted at 6th, 5th, 4th and 3rd string are all equal.
        groups.pop()
    skips = len(groups)
    num_strings = sum([1 for fret_num in voicing if fret_num is not None])
    return skips, -num_strings


def get_string_idx(master_voicing):
    # Voicing in list form is backwards compared to ChordDiagram drawing.
    # Voicing indexes match string indexes ie voicing == [1st, ... 5th, 6th]
    # Start recursion after skipping the rightmost string; keep root note of chord.
    string_idx = 5
    while master_voicing[string_idx] is None:
        string_idx -= 1
    return string_idx - 1


# 1) Build fretboard for a given tuning
# 2) Master Voicing DFS -> Pick up all 'full' chords without any skipped strings.
# 3) Chord Chunk DFS -> Build a subset of 'chord chunks' for a given master voicing.  DFS on
#                       a master_voicing to skip some strings and see if we can still create
#                       the same chord with strings skipped.

def build_master_voicings(tuning: List[int]) -> DefaultDict:
    def master_voicing_dfs(string_idx: int, chord_num: int, is_triad: bool, voicing: List[int],
                           min_fret: int, max_fret: int) -> None:
        if string_idx < 0:
            return
        string = fretboard[string_idx]
        # Search for the C note on this string and start recursion - only happens once.
        if all(note is None for note in voicing):
            fret_num = 3  # If C note is lower than fret 3, chords will be missed.
            while string[fret_num] % 12 != 0:
                fret_num += 1
            voicing[string_idx] = fret_num
            master_voicing_dfs(string_idx - 1, 0b100000000000, False, voicing, fret_num, fret_num)
            return

        # I'm restricting a guitar chord to a span of 4 frets (inclusive).
        # This range will target between 4 to 8 frets - 8 at first, 4 later in recursion.
        for fret_num in range(max(max_fret - 3, 0), min(min_fret + 4, 24)):
            octave, note_idx = divmod(string[fret_num], 12)
            note_bit = 2 ** (11 - note_idx)
            voicing = voicing[:string_idx] + [fret_num] + voicing[string_idx + 1:]
            if not is_triad:
                is_triad = bin(chord_num | note_bit).count('1') >= 3
            if is_triad and string_idx == 0:
                master_voicings[chord_num | note_bit].append(voicing[:])

            master_voicing_dfs(string_idx - 1, chord_num | note_bit, is_triad, voicing,
                               min(min_fret, fret_num), max(max_fret, fret_num))

    fretboard = [[note_val for note_val in range(string_val, string_val + 24)] for string_val in
                 tuning][::-1]
    master_voicings = collections.defaultdict(list)
    for string_idx in range(2, 6):
        master_voicing_dfs(string_idx, 0, False, [None, None, None, None, None, None], 0, 24)
    return master_voicings


def build_chord_chunk_voicings(tuning: List[int], master_voicings: DefaultDict):
    def voicing_to_chord_num(voicing: List):
        chord_num = 0b000000000000
        for i, fret_num in enumerate(voicing):
            if fret_num is not None:
                string = fretboard[i]
                note_val = string[fret_num]
                octave, note_idx = divmod(note_val, 12)
                note_bit = 2 ** (11 - note_idx)
                chord_num |= note_bit
        return chord_num

    def chord_chunk_dfs(string_idx: int, chord_num: int, master_voicing: List,
                        voicing: List) -> DefaultDict:
        if string_idx < 0:
            return
        # If we can skip this string to produce the same chord - skip it, record it, and keep going.
        voicing_without = voicing[:string_idx] + [None] + voicing[string_idx + 1:]
        chord_num_without = voicing_to_chord_num(voicing_without)
        if chord_num_without == chord_num:
            chord_chunks[tuple(master_voicing)].append(voicing_without[:])
            chord_chunk_dfs(string_idx - 1, chord_num, master_voicing, voicing_without)
        # Include it so future strings may be skipped.
        chord_chunk_dfs(string_idx - 1, chord_num, master_voicing, voicing)

    fretboard = [[note_val for note_val in range(string_val, string_val + 24)] for string_val in
                 tuning][::-1]
    chord_chunks = collections.defaultdict(list)
    for chord_num, master_voicings_list in master_voicings.items():
        for master_voicing in master_voicings_list:
            string_idx = get_string_idx(master_voicing)
            chord_chunk_dfs(string_idx, chord_num, master_voicing, master_voicing[:])

    for master_voicing, chord_chunk_list in chord_chunks.items():
        chord_chunks[master_voicing].sort(key=chord_voicing_sort)
    return chord_chunks


def build_voicing_data(tuning: List, master_voicings: DefaultDict, chord_chunks: DefaultDict) -> List:
    # Up until now, voicings have been backwards from what ChordDiagram draws; reverse them here.
    data = []
    for chord_num, master_voicing_list in master_voicings.items():
        for master_voicing in master_voicing_list:
            root_string = get_string_idx(master_voicing) + 2  # Reusing function differently.
            master_data = (str(tuning), chord_num, root_string, str(master_voicing[::-1]),
                           str(master_voicing[::-1]))
            data.append(master_data)
            subset = chord_chunks[tuple(master_voicing)]
            for chord_chunk_voicing in subset:
                chord_chunk_data = (str(tuning), chord_num, root_string, str(master_voicing[::-1]),
                                    str(chord_chunk_voicing[::-1]))
                data.append(chord_chunk_data)
    return data


def insert_data_for_tuning(tuning: List) -> None:
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        master_voicings = build_master_voicings(tuning)
        chord_chunks = build_chord_chunk_voicings(tuning, master_voicings)
        voicing_data = build_voicing_data(tuning, master_voicings, chord_chunks)
        cursor.executemany("INSERT INTO ChordVoicings VALUES(?, ?, ?, ?, ?)", voicing_data)
        return


def check_table_data_exists(tuning: List) -> None:
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS ChordVoicings(
                        tuning TEXT,
                        chord_num INT,
                        root_string INT,
                        master_voicing TEXT,
                        voicing TEXT)
                        """)
        cursor.execute("SELECT * FROM ChordVoicings WHERE tuning = ?", [str(tuning)])
        rows = cursor.fetchall()
        if not rows:
            insert_data_for_tuning(tuning)
        return


def get_all_voicings(tuning: List) -> List:
    check_table_data_exists(tuning)
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ChordVoicings WHERE tuning = ?", [str(tuning)])
        rows = cursor.fetchall()
        return rows


def get_master_voicings(tuning: List) -> List:
    check_table_data_exists(tuning)
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM ChordVoicings WHERE tuning = ?
                          AND voicing = master_voicing""", [str(tuning)])
        rows = cursor.fetchall()
        return rows


def get_chord_num_master_voicings(tuning: List, chord_num: int) -> List:
    check_table_data_exists(tuning)
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT voicing FROM ChordVoicings WHERE tuning = ? 
                       AND chord_num = ?
                       AND master_voicing = voicing""", [str(tuning), chord_num])
        rows = cursor.fetchall()
        voicings = [ast.literal_eval(tup[0]) for tup in rows]
        return voicings

def get_chord_voicings_from_query(tuning: List, query: str, params: List) -> List:
    check_table_data_exists(tuning)
    with sqlite3.connect("chord_voicing_DB.db") as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        voicings = [ast.literal_eval(tup[0]) for tup in rows]
        return voicings


if __name__ == "__main__":
    # Some testing:
    # rows = get_all_voicings(standard_tuning)
    rows = get_chord_num_master_voicings(standard_tuning, 2192)  # 2192 is the Major chord_num.
    print(*rows, sep="\n")
