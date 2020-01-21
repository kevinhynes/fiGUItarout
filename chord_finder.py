from kivy.storage.jsonstore import JsonStore

from music_constants import chrom_scale, chrom_scale_no_acc, chord_shapes, standard_tuning

import collections


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
    for chord_name, chord_shape in chord_shapes.items():
        if dummy_mode & chord_shape == chord_shape:
            chord_list.append(root_note + " " + chord_name)
    return chord_list


# note_idx = 0
# scale = 0b101011010101
#
# for _ in range(7):
#     print(chrom_scale[note_idx], " ", bin(scale))
#     chords_this_root = list_chords_in_key_at_this_root(note_idx, scale)
#     print(*chords_this_root, sep="\n")
#     note_idx, scale = do_circular_bit_rotation(note_idx, scale)


# Notes to self:
# 1) Need to search guitar fretboard for voicings of a given chord.
# 	A chord is defined by a shape, which is a "binary string".
# 	Many chords are similar ie they are built of the same parts.
# 	For example Major 6 is 1-3-5-6 and Major is 1-3-5.
# 	Thus, searching for a Major 6 separately from a Major will cause
# 	the algorithm to have to repeat calculations for finding a 1-3-5.
#   Consider additional Major chords:
#       - Major 7, Major 9, Major 11, Major 13, Major add9,
#       Major add11, Major add13, Major7 add11, Major7 add13,
#       Major 9 add13..

#   Confusingly, this logic can be extended to all other chords
#   A depth-first search can be performed that chooses to
#   1) include this digit, 2) not include this digit.
#   For example at some point we will arrive at the minor third interval.
#   When we include it, the search will go on to build minor chords.
#   When we do not include it, *some* of the search will go on to build major chords.
#   The problem is that many of the chords that will be explored with this method
#   are non-sensical or 'expensive'.

#   Chords are valid when they have at least 3 bits set.

#   Chords are "in key" when the binary chord shape & the rotated mode == the binary chord shape.
#   (equivocally, we can rotate the chord shape and compare to the unrotated mode).

#   If this is used as a means of searching the guitar fretboard, then all Major chords
#   (from a certain starting note) will originate from the same search.

#   All chord shapes are specific to a tuning.  All chord shapes are valid starting at different
#   root notes.  It doesn't make sense to search for C Major and F Major chords in
#   standard tuning.  This is repeat work.  The Major chord shape will be the same, just at
#   a different fret number.

#   So... search guitar fretboard for every possible chord in a specific tuning.
#   Pick up all major, minor, suspended, etc chord shapes.
#   Then figure out which chords are in key.
#   Then build chord diagrams based on that.

#   Since chord shapes that get built are semi root-note agnostic, just build it for C.

#   The maximum portion of the fretboard that should ever get searched would be basically the
#   root note fret number +/- 3 frets inclusive.

#   When the chord contains same notes as one of the open strings, opportunity for 'wide'
#   chords using open strings.

#   Performing the DFS is easy, how to validate & classify the chords that get built from
#   this combinatoric process?

#   Need to list out all the binary chord shapes that are actually meaningful I guess?



def chord_voicing_dfs(string_idx, chord_shape, is_triad, voicing, min_fret, max_fret):
    # There are no more strings.
    if string_idx < 0:
        return

    string = fretboard[string_idx]

    # Search for the C note on this string and start recursion - only happens once.
    if all(note is None for note in voicing):
        fret_num = 0
        while string[fret_num] % 12 != 0:
            fret_num += 1
        voicing[string_idx] = fret_num
        chord_voicing_dfs(string_idx-1, 0b100000000000, False, voicing, fret_num, fret_num)
        return

    # Skip this string (the string at original string_idx will never be skipped).
    chord_voicing_dfs(string_idx - 1, chord_shape, is_triad, voicing, min_fret, max_fret)

    # I'm restricting a guitar chord to a span of 4 frets (inclusive).
    # This range will target between 4 to 8 frets - 8 at first, 4 later in recursion.
    for fret_num in range(max(max_fret-3, 0), min(min_fret+4, 12)):
        octave, note_idx = divmod(string[fret_num], 12)
        note_in_bin = 2**(11 - note_idx)
        voicing = voicing[:string_idx] + [fret_num] + voicing[string_idx+1:]
        if not is_triad:
            is_triad = bin(chord_shape | note_in_bin).count('1') >= 3
        if is_triad:
            chord_to_voicings[chord_shape | note_in_bin].append(voicing)

        chord_voicing_dfs(string_idx-1, chord_shape | note_in_bin, is_triad,
                          voicing, min(min_fret, fret_num), max(max_fret, fret_num))



chord_voicings_by_tuning = JsonStore("chord_voicings_by_tuning.json")
tuning = standard_tuning
if chord_voicings_by_tuning.exists(str(tuning)):
    chord_to_voicings = chord_voicings_by_tuning.get(str(tuning))["chord_to_voicings"]
    print("retreived")
else:
    print("calculating")
    fretboard = [[note_val for note_val in range(string_val, string_val+12)]
                 for string_val in standard_tuning][::-1]
    chord_to_voicings = collections.defaultdict(list)
    chord_voicing_dfs(5, 0b000000000000, False, [None, None, None, None, None, None], 0, 12)
    chord_voicings_by_tuning.put(str(tuning), chord_to_voicings=chord_to_voicings)
    print("saved")

for chord_name, chord_shape in chord_shapes.items():
    if chord_to_voicings.get(str(chord_shape), None):
        print(chord_name, *chord_to_voicings[str(chord_shape)], sep='\n')
