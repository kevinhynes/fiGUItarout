from kivy.graphics import Color


black = Color(0, 0, 0, 1)
white = Color(1, 1, 1, 1)
gray = Color(0.5, 0.5, 0.5, 1)
brown = Color(rgba=[114 / 255, 69 / 255, 16 / 255, 1])

rainbow = [Color(hsv=[i / 12, 1, 0.95]) for i in range(12)]
reds = [Color(hsv=[0, i / 12, 1]) for i in range(12)][::-1]
blues = [Color(hsv=[0.6, i / 12, 1]) for i in range(12)][::-1]

octave_colors = [
    rainbow[9],
    rainbow[10],
    rainbow[0],  # Lowest octave in standard tuning is octave 2.
    rainbow[2],
    rainbow[4],
    rainbow[6],
    rainbow[8],
]


