from music_constants import chrom_scale, chrom_scale_no_acc, chord_shapes


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
    dummy_mode <<=1
    note_idx = (note_idx + 1) % 12
    while 0b100000000000 & dummy_mode == 0:
        dummy_mode <<= 1
        rotate_bit <<= 1
        note_idx = (note_idx + 1) % 12
    dummy_mode &= 0b111111111111
    dummy_mode |= rotate_bit
    return note_idx, dummy_mode


def build_chord_list(note_idx, dummy_mode):
    root_note = chrom_scale[note_idx]
    chord_list = []
    for chord_name, chord_shape in chord_shapes.items():
        if dummy_mode & chord_shape == chord_shape:
            chord_list.append(root_note + " " + chord_name)
    return chord_list


note_idx = 0
scale = 0b101011010101

for _ in range(7):
    print(chrom_scale[note_idx], " ", bin(scale))
    chords_this_root = build_chord_list(note_idx, scale)
    print(*chords_this_root, sep="\n")
    note_idx, scale = do_circular_bit_rotation(note_idx, scale)
