chrom_scale = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
chrom_scale_no_acc = ['C', 'C/D', 'D', 'D/E', 'E', 'F', 'F/G', 'G', 'G/A', 'A', 'A/B', 'B']
scale_degrees = ["1", "♭2", "2", "♭3", "3", "4", "♯4/♭5", "5", "♯5/♭6", "6", "♭7", "7"]
flat = u'\u266D'
sharp = u'\u266F'

rest = u'\u1D13x'

standard_tuning = (28, 33, 38, 43, 47, 52)

chord_names_to_nums = {
    'Major'     : 0b100010010000, 'Major 6': 0b100010010100, 'Major 7': 0b100010010001,
    'Major 9'   : 0b101010010001, 'Major 11': 0b101011010001,

    'Minor'     : 0b100100010000, 'Minor 6': 0b100100010100, 'Minor 7': 0b100100010010,
    'Minor 9'   : 0b101100010010, 'Minor 11': 0b101101010010, 'Minor Major 7': 0b100100010001,

    'Dominant 7': 0b100010010010, 'Dominant 9': 0b101010010010, 'Dominant 11': 0b101011010010,

    'Sus 2'     : 0b101000010000, 'Sus 4': 0b100001010000,

    'Diminished': 0b100100100000, 'Diminished 7': 0b100100100100,

    'Augmented' : 0b100010001000, 'Augmented 7': 0b100010001010,
    }

basic_chord_names_to_nums = {
    'Major': 0b100010010000,
    'Minor': 0b100100010000,
    'Diminished': 0b100100100000,
    'Augmented': 0b100010001000,
    'Dominant 7': 0b100010010010,
    'Sus 2': 0b101000010000,
    }

major_chord_shapes = {
    'Major'  : 0b100010010000, 'Major 6': 0b100010010100, 'Major 7': 0b100010010001,
    'Major 9': 0b101010010001, 'Major 11': 0b101011010001,
    }

minor_chord_shapes = {
    'Minor'  : 0b100100010000, 'Minor 6': 0b100100010100, 'Minor 7': 0b100100010010,
    'Minor 9': 0b101100010010, 'Minor 11': 0b101101010010, 'Minor Major 7': 0b100100010001,
    }

dom_chord_shapes = {
    'Dominant 7': 0b100010010010, 'Dominant 9': 0b101010010010, 'Dominant 11': 0b101011010010,
    }

sus_chord_shapes = {
    'Sus 2': 0b101000010000, 'Sus 4': 0b100001010000,
    }

dim_chord_shapes = {
    'Diminished': 0b100100100000, 'Diminished 7': 0b100100100100,
    }

aug_chord_shapes = {
    'Augmented': 0b100010001000, 'Augmented 7': 0b100010001010,
    }
