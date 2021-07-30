# This application renders a simulated magnetic compass on an embedded display. The input is a single
# integer indicating what heading to display in the range (0,359).
# import usb_cdc
from adafruit_gizmo import tft_gizmo
import time
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
import displayio

# use built in display (MagTag, PyPortal, PyGamer, PyBadge, CLUE, etc.)
# see guide for setting up external displays (TFT / OLED breakouts, RGB matrices, etc.)
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-and-display-bus
display = tft_gizmo.TFT_Gizmo()

# uart = usb_cdc.data
# print(uart.connected)

# while True:
#    print(uart.readline())

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

import board
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# try uncommenting different font files if you like
font_file = "/Helvetica-Bold-16.bdf"
# font_file = "fonts/Junction-regular-24.pcf"

# Set text, font, and color
text = "N"
font = bitmap_font.load_font(font_file)
# color = 0xFF00FF
color = 0xFFFFFF

# How many degrees are visible on the display
tot_visible_degrees = 90
ppd = DISPLAY_WIDTH / tot_visible_degrees
tick_pad = 40
tick_30_height = 40
tick_10_height = 20
tick_5_height = 10
tick_30_width = 6
tick_10_width = 4
tick_5_width = 2
MESSAGE=0x0018fd
ERROR=0xfd1800

def msg(text, color=MESSAGE):
    heading_label = label.Label(font, text=text, color=color, scale=1)
    heading_label.anchor_point = (0.5, 0.5)    
    heading_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)
    display.show(heading_label);
    
msg("Loading...",color=MESSAGE)

def string_width(text, font):
    w = 0
    for c in text:
        g = font.get_glyph(ord(c))
        w = w + g.width
    return w


def create_group(text, visible_degrees=30, scale=4, color=0xFFFFFF):
    group = displayio.Group()

    heading_label = label.Label(font, text=text, color=color, scale=scale)
    heading_label.anchor_point = (0.5, 0.5)

    heading_label.x = -int(string_width(text, font) * scale / 2)
    heading_label.y = int(DISPLAY_WIDTH / 2)
    group.append(heading_label)
    for i in range(visible_degrees):
        if i % 30 == 0:
            rect = Rect(
                int(i * ppd),
                int(DISPLAY_HEIGHT / 2) + tick_pad,
                tick_30_width,
                tick_30_height,
                fill=color,
            )
            group.append(rect)
        elif i % 10 == 0:
            rect = Rect(
                int(i * ppd),
                int(DISPLAY_HEIGHT / 2) + tick_pad + (tick_pad - tick_10_height),
                tick_10_width,
                tick_10_height,
                fill=color,
            )
            group.append(rect)
        elif i % 5 == 0:
            rect = Rect(
                int(i * ppd) + 1,
                int(DISPLAY_HEIGHT / 2) + tick_pad + (tick_pad - tick_5_height),
                tick_5_width,
                tick_5_height,
                fill=color,
            )
            group.append(rect)
    return group


group_data = [
    ("N", 4),
    ("330", 2),
    ("300", 2),
    ("E", 4),
    ("240", 2),
    ("210", 2),
    ("S", 4),
    ("150", 2),
    ("120", 2),
    ("E", 4),
    ("60", 2),
    ("30", 2),
]

groups = []

#
# Create tiles
#
for i, g in enumerate(group_data):
    g_ = create_group(g[0], scale=g[1])
    groups.append(g_)
    

# Simulate the supplied compass heading
def heading(degrees):
    compass = displayio.Group()
    #compass.y = int(DISPLAY_HEIGHT / 2 - 20)
    x = 0
    compass.x = 0
    if degrees < 0 or degrees > 359:
        msg("Bad Heading",color=ERROR)
    else:
        index = int((360-degrees) / 30) 
        i = index-1
        if i < 0:
            i = len(groups) - i
        for j in range(3):
            if i == len(groups):
                i = 0
            g_ = groups[i+j]
            g_.x = x
            compass.append(g_)
            x = x + int(30 * ppd)
    
    offset = int((30*index) * ppd) - degrees
    print(offset)
    compass.x = compass.x + offset
    compass.append(Line(int(DISPLAY_WIDTH / 2),0,int(DISPLAY_WIDTH / 2),DISPLAY_HEIGHT,0xaaaaaa))
    compass.y = compass.y - 30
    return compass

display.show(heading(187))

while True:
    pass
#    for i in range(0 - 100, DISPLAY_WIDTH + 100):
#        compass.x = i
#        time.sleep(0.001)
