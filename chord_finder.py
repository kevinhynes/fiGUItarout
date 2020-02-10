import collections, itertools, json
from typing import List
from music_constants import chrom_scale, chrom_scale_no_acc, chord_names_to_nums, standard_tuning


# FINDING CHORDS IN A GIVEN KEY
# All chords are defined by the distance between their notes (ignoring inversions for now).
# Chords are constants.  Key signatures determine which chords "naturally" occur.
# C Major chord (C-E-G) "naturally" falls into C Major (C-D-E-F-G-A-B),
# but C Dom 7 (C-E-G-A#) does not, since it contains A#.

# Chords rooted at C:        C     C#    D     D#    E     F     F#    G     G#    A     A#    B
# Major Chord Shape:         1     0     0     0     1     0     0     1     0     0     0     0
# C Major = C-E-G            C                       E                 G
# Dominant 7 Chord Shape:    1     0     0     0     1     0     0     1     0     0     1     0
# C Dominant 7 = C-E-G-A#    C                       E                 G                 A#

# Chords rooted at A:        A     A#    B     C     C#    D     D#    E     F     F#    G     G#
# Major Chord Shape:         1     0     0     0     1     0     0     1     0     0     0     0
# A Major = A-C#-E           A                       C#                E
# Dominant 7 Chord Shape:    1     0     0     0     1     0     0     1     0     0     1     0
# A Dominant 7 = A-C#-E-G    A                       C#                E                 G


def list_chords_in_key(root_note_idx: int, mode: int) -> List[str]:
    '''
    Given a root note and mode, collect all chords that naturally fall into this key.
    Chords are defined as binary numbers in the chord_names_to_nums dict.
    '''

    def do_circular_bit_rotation(note_idx, dummy_mode):
        rotate_bit = 0b100000000000 & dummy_mode
        if rotate_bit:
            rotate_bit = 1
        else:
            rotate_bit = 0
        dummy_mode <<= 1
        note_idx = (note_idx + 1) % 12
        while 0b100000000000 & dummy_mode == 0:
            dummy_mode <<= 1
            rotate_bit <<= 1
            note_idx = (note_idx + 1) % 12
        dummy_mode &= 0b111111111111
        dummy_mode |= rotate_bit
        return note_idx, dummy_mode

    def list_chords_in_key_at_this_root(note_idx, dummy_mode):
        root_note = chrom_scale[note_idx]
        chord_list = []
        for chord_name, chord_num in chord_names_to_nums.items():
            if dummy_mode & chord_num == chord_num:
                chord_list.append(root_note + " " + chord_name)
        return chord_list

    chord_list = []
    note_idx = root_note_idx
    for _ in range(7):
        chords_this_root = list_chords_in_key_at_this_root(note_idx, mode)
        chord_list.extend(chords_this_root)
        note_idx, mode = do_circular_bit_rotation(note_idx, mode)
    return chord_list


# For testing:
# root_note_idx = 9
# major_scale = 0b101011010101
# minor_scale = 0b101101011010
# mode = minor_scale
# chord_list = list_chords_in_key(root_note_idx, minor_scale)


# FINDING ALL POSSIBLE VOICINGS/FINGERINGS OF A CHORD ON GUITAR
#   Need to search guitar fretboard for voicings of a given chord.
# 	A chord is defined by the distance between its notes.
# 	This creates a shape, as an integer or "binary string".
# 	Many chords are similar ie they are built of the same parts.
# 	For example Major 6 is 1-3-5-6 and Major is 1-3-5.
# 	Thus, searching for a Major 6 separately from a Major will cause
# 	the algorithm to have to repeat calculations for finding a 1-3-5.
#   Consider additional Major chords:
#       - Major 7, Major 9, Major 11, Major 13, Major add9,
#       Major add11, Major add13, Major7 add11, Major7 add13,
#       Major 9 add13..

#   Confusingly, this logic can be extended to all other chords.
#   A depth-first search can be performed that chooses to
#   1) include this string/fret_num, 2) not include this string/fret_num.
#   For example at some point we will arrive at the minor third interval.
#   When we include it, the search will go on to build minor chords.
#   When we do not include it, *some* of the search will go on to build major chords.
#   The problem is that many of the chords that will be caught with this method
#   are non-sense chords (like a 0b111111000000 chord); this is a bit brute-force.

#   Chords are "in key" when the binary chord shape & the rotated mode == the binary chord shape.
#   (equivocally, we can rotate the chord shape and compare to the unrotated mode).

#   If this is used as a means of searching the guitar fretboard, then all Major chords
#   (from a certain starting string) will originate from the same search.

#   Chords are valid when they have at least 3 bits set.

#   The maximum portion of the fretboard that should ever get searched would be basically the
#   root note fret number +/- 3 frets inclusive.

#   All chord shapes are specific to a tuning.  All chord shapes are valid starting at different
#   root notes.  It doesn't make sense to search for C Major and F Major chords in
#   standard tuning.  This is repeat work.  The Major chord shape will be the same, just at
#   a different fret number.

#   1) Search guitar fretboard for every possible C-chord in a specific tuning.
#   2) Pick up all possible chords (combinations) containing 3 unique notes.
#   3) Save the result; it won't ever change for that guitar tuning.
#   4) Given a key signature (root note, mode), figure out which chords are in key.
#   5) Build chord diagrams from there, based on that.


def build_chord_voicings_for_tuning(tuning):
    def chord_voicing_dfs(string_idx: int, bin_chord_shape: int, is_triad: bool, voicing: List[int],
                          min_fret: int, max_fret: int) -> None:
        '''
        Explore the fretboard from the original string_idx,  creating ALL possible chords
        and save the voicing to a dictionary based on chord quality (major, minor, etc).
        '''
        # There are no more strings.
        if string_idx < 0:
            return

        string = fretboard[string_idx]

        # Search for the C note on this string and start recursion - only happens once.
        if all(note is None for note in voicing):
            fret_num = 3  # If C note is lower than fret 3, chords will be missed.
            while string[fret_num] % 12 != 0:
                fret_num += 1
            voicing[string_idx] = fret_num
            chord_voicing_dfs(string_idx - 1, 0b100000000000, False, voicing, fret_num, fret_num)
            return

        # Skip this string (the string at original string_idx will never be skipped).
        chord_voicing_dfs(string_idx - 1, bin_chord_shape, is_triad, voicing, min_fret, max_fret)

        # I'm restricting a guitar chord to a span of 4 frets (inclusive).
        # This range will target between 4 to 8 frets - 8 at first, 4 later in recursion.
        for fret_num in range(max(max_fret - 3, 0), min(min_fret + 4, 24)):
            octave, note_idx = divmod(string[fret_num], 12)
            bin_note = 2 ** (11 - note_idx)
            voicing = voicing[:string_idx] + [fret_num] + voicing[string_idx + 1:]
            if not is_triad:
                is_triad = bin(bin_chord_shape | bin_note).count('1') >= 3
            if is_triad:
                chords_to_voicings[bin(bin_chord_shape | bin_note)].append(voicing[::-1])

            chord_voicing_dfs(string_idx - 1, bin_chord_shape | bin_note, is_triad, voicing,
                              min(min_fret, fret_num), max(max_fret, fret_num))

    def chord_voicing_sort(voicing):
        '''
        The chord voicings picked up by the DFS are sporadic. Sort so that:
          1) voicings with a lot of intermittent string skipping come last
          2) 'fuller' chords come first: 6 strings - 5 strings - 4 strings...

        `voicing` is a list of length 6 where voicing[string_idx] = fret_num.

        If a string isn't played, fret_num is None.  Otherwise it is an integer.
        '''
        groups = list(itertools.groupby(voicing, key=type))
        if groups[0][0].__name__ == 'NoneType':
            # 'full' chords rooted at 6th, 5th, 4th and 3rd string are all equal.
            groups.pop(0)
        skips = len(groups)
        num_strings = sum([1 for fret_num in voicing if fret_num is not None])
        return skips, -num_strings

    print("calculating")
    fretboard = [[note_val for note_val in range(string_val, string_val + 24)] for string_val in
                 tuning][::-1]
    chords_to_voicings = collections.defaultdict(list)
    for string_idx in range(2, 6):
        chord_voicing_dfs(string_idx, 0b000000000000, False, [None, None, None, None, None, None],
                          0, 24)

    for bin_chord_shape, chord_voicings in chords_to_voicings.items():
        chord_voicings.sort(key=chord_voicing_sort)
        chords_to_voicings[bin_chord_shape] = chord_voicings

    tuning_to_chord_voicings = {}
    tuning_to_chord_voicings[str(tuning)] = chords_to_voicings
    with open('chord_voicings_by_tuning.json', 'w') as write_file:
        json.dump(tuning_to_chord_voicings, write_file)
    print("saved")
    return chords_to_voicings


def get_chord_voicings_for_tuning(tuning):
    with open('chord_voicings_by_tuning.json') as read_file:
        chord_voicings_by_tuning = json.load(read_file)

    if chord_voicings_by_tuning.get(str(tuning), None):
        chords_to_voicings = chord_voicings_by_tuning.get(str(tuning))
        print("retreived")
    else:
        chords_to_voicings = build_chord_voicings_for_tuning(tuning)
    return chords_to_voicings


if __name__ == "__main__":
    get_chord_voicings_for_tuning(standard_tuning)
