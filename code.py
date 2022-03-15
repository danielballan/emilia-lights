import time
import board
import digitalio
import random

import neopixel

NUM_PIXELS = 100
NUM_SPARKLES = 10
TIME_STEP = 0.1  # seconds
HIGH_BRIGHTNESS = 1
LOW_BRIGHTNESS = 0.03

led = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
strings = [
    neopixel.NeoPixel(board.D11, NUM_PIXELS, auto_write=False),
    neopixel.NeoPixel(board.D10, NUM_PIXELS, auto_write=False),
    neopixel.NeoPixel(board.D6, NUM_PIXELS, auto_write=False),
]
switches = [
    digitalio.DigitalInOut(pin) for pin in [board.A1, board.A2, board.A3, board.A4]
]
for switch in switches:
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.DOWN


def hex_to_channels(hex_code):
    """
    Convert hex code to (R, G, B) or (G, R, B) or (R, G, B, W).
    >>> hex_to_channels("#ff0000", "RGB")
    (255, 0, 0)
    """
    hex_value = hex_code.lstrip("#")
    r, g, b = tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))
    return g, r, b


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (g, r, b)


# These HEX codes were obtained by consulting the XKCD_COLORS in, for example,
# https://github.com/danielballan/twinkling-tree/blob/main/twinkling_tree/color_data.py
RED = hex_to_channels("#ff0000")
BLUE = hex_to_channels("#0343df")
PURPLE = hex_to_channels("#35063e")
PINK = hex_to_channels("#ff028d")
GREEN = hex_to_channels("#00ff00")

# Lay out the colors randomly into "canvases".
RED_AND_BLUE_AND_PURPLE_AND_PINK = [RED, BLUE, PURPLE, PINK]
RED_AND_BLUE_AND_PURPLE_AND_PINK_CANVAS = [
    random.choice(RED_AND_BLUE_AND_PURPLE_AND_PINK) for _ in range(NUM_PIXELS)
]
ELSA_MAGIC = [
    hex_to_channels("#d6fffa"),
    hex_to_channels("#0d75f8"),
    hex_to_channels("#020035"),
]
ELSA_MAGIC_CANVAS = [random.choice(ELSA_MAGIC) for _ in range(NUM_PIXELS)]
RAINBOW_CANVAS = [wheel(random.randint(0, 256)) for _ in range(NUM_PIXELS)]
BLACK_CANVAS = [(0, 0, 0) for _ in range(100)]


# Initialize the canvas.
canvas = BLACK_CANVAS.copy()
# Track the positions of "sparkle" pixels.
sparkle_layer = [random.randint(0, NUM_PIXELS - 1) for _ in range(3 * NUM_SPARKLES)]
while True:
    # Extract the state of each switch.
    switch_values = [switch.value for switch in switches]
    # Switch #4 controls brightness.
    brightness = HIGH_BRIGHTNESS if switch_values[3] else LOW_BRIGHTNESS
    # The arrangement of Switch #1 and Switch #2 together choose a pattern.
    # The on-board LED can be used for debugging.
    # Note that the on-board LED is RGB, while the strings are GRB.
    if switch_values[:2] == [True, True]:
        led[0] = (0, 255, 0)  # green
        canvas[:] = RAINBOW_CANVAS
    elif switch_values[:2] == [True, False]:
        led[0] = (255, 0, 0)  # red
        canvas[:] = RED_AND_BLUE_AND_PURPLE_AND_PINK_CANVAS
    elif switch_values[:2] == [False, True]:
        led[0] = (0, 0, 255)  # blue
        canvas[:] = ELSA_MAGIC_CANVAS
    else:
        led[0] = (0, 0, 0)
        canvas[:] = BLACK_CANVAS
    for i, string in enumerate(strings):
        string.brightness = brightness
        string[:] = canvas
        # If Switch #3 is on, draw a sparkling effect over top of canvas
        # (unless the canvas is black).
        if switch_values[2] and any(switch_values[:2]):
            for j in sparkle_layer[(NUM_SPARKLES * i) : (NUM_SPARKLES * (1 + i))]:
                string[j] = (255, 255, 255)
    led.show()
    for string in strings:
        string.show()
    time.sleep(TIME_STEP)
    # Remove one "sparkle" pixel and add one new one.
    sparkle_layer.pop(0)
    sparkle_layer.append(random.randint(0, NUM_PIXELS - 1))
