# 
# circuitpy-compass (code.py)
#
# This application renders a simulated magnetic compass on an embedded display. The input is a single
# integer indicating what heading to display in the range (0,359).
#
# Copyright (C) 2021 Dan Stieglitz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import usb_cdc
import displayio
import board
import time
from adafruit_gizmo import tft_gizmo
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# use built in display (MagTag, PyPortal, PyGamer, PyBadge, CLUE, etc.)
# see guide for setting up external displays (TFT / OLED breakouts, RGB matrices, etc.)
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-and-display-bus
display = tft_gizmo.TFT_Gizmo()

uart = usb_cdc.data
#print(uart.connected)

DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

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
# pixels per degree heading
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

compass = displayio.Group()
group_data = [
    ("N", 4),
    ("3", 2),
    ("6", 2),
    ("E", 4),
    ("12", 2),
    ("15", 2),
    ("S", 4),
    ("21", 2),
    ("24", 2),
    ("W", 4),
    ("30", 2),
    ("33", 2),
]
group_data.reverse()

# Helper method to wrap index calculations around the length of the array
def circ_index(idx, tot=len(group_data)):
    if idx >= tot - 1:
        return idx - tot
    elif idx < 0:
        return tot + idx
    else:
        return idx

# Convert degrees to the group index
def to_index(degrees):
    return int((360-degrees) / 30) - 1

def to_degrees(index):
    return 360 - (circ_index(index + 1) * 30)

#
# Create tiles
#
x=0
left=330
pad=2
pad_px = -int((30*pad) *ppd)
# adjust for extra groups and alignment
compass.x = pad_px
#for i, g in enumerate(group_data):
# cap the ends with an extra couple of groups to simulate a round compass
for i in range(-pad,len(group_data)+pad):
    #print(i)
    #print(circ_index(i))
    g = group_data[circ_index(i)]
    g_ = create_group(g[0], scale=g[1])
    g_.x = x
    compass.append(g_)
    x = x + int(30 * ppd)

updating = False

# Simulate the supplied compass heading
def heading(degrees, compass=compass):
    if degrees < 0 or degrees > 359:
        msg("Bad Heading",color=ERROR)
        
    global updating
    global left
    updating = True
    # clear the existing configuration
#    t = len(compass)
#    for i in range(0,t):
#        compass.pop()

    #print("after clearing="+str(len(compass)))
    # find the index of the group that contains the desired heading
    index = to_index(degrees)
    #print("index="+str(index))

    #left=to_degrees(circ_index(index-2))
    #print("left="+str(left))
    midpoint=left-int(tot_visible_degrees/2)
    if midpoint < 0:
        midpoint = 360 + midpoint
    #print("midpoint="+str(midpoint))
    right=midpoint-int(tot_visible_degrees/2)
    if right < 0:
        right = 360 + right
    #print("right="+str(right))

    # calculate the number of pixels we need to move the groups to show the
    # correct heading
    offset = int((degrees-midpoint)*ppd)
    # print("offset="+str(offset))

    compass.x = offset + pad_px
    
#    x = offset

#    else:
#        i = circ_index(index-2)
#        # print("i="+str(i))
#        for n in range(5):
#            l = circ_index(i+n,len(compass))
#            # print("l="+str(l)+" at "+str(x))
#            #g_ = groups[l]
#            #g_.x = x
#            #compass.append(g_)
#            #x = x + int(30 * ppd)

#    compass.append(Line(int(DISPLAY_WIDTH / 2),0,int(DISPLAY_WIDTH / 2),DISPLAY_HEIGHT,0xaaaaaa))
#    cts = label.Label(font, text=str(degrees), color=color, scale=1)
#    cts.anchor_point = (0.5, 0.5)
#    cts.anchored_position = (DISPLAY_WIDTH / 2, 50)
#    # compass.append(cts)
    updating = False

compass.y = compass.y - 30
display.show(compass)

cur_head = 0
heading(127)

def test_loop():
    for i in range(0,359):
        heading(i)
        time.sleep(0.001)

def main_loop():
    i = 0
    global cur_head
    global updating
    try:
        data = uart.readline()
        p = data.split()
        key = p[0]
        #print(key)
        val = int(p[1])
        print(str(val))
        i = i + 1
        if key == b'HDG':
            if not updating:
                print("updating to "+str(val))
                cur_head = val
                heading(cur_head)
    except Exception as e:
        pass
        #msg(str(e),color=ERROR)

while True:
    main_loop()
    pass
#    test_loop()

