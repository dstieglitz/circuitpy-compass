# This application renders a simulated magnetic compass on an embedded display. The input is a single
# integer indicating what heading to display in the range (0,359).
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


group_data = [
    ("N", 4),
    ("30", 2),
    ("60", 2),
    ("E", 4),
    ("120", 2),
    ("150", 2),
    ("S", 4),
    ("210", 2),
    ("240", 2),
    ("W", 4),
    ("300", 2),
    ("330", 2),
]
group_data.reverse()

groups = []

# Helper method to wrap index calculations around the length of the array
def circ_index(idx, tot=len(group_data)):
    if idx >= tot:
        return idx - tot
    elif idx < 0:
        return tot + idx + 1
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
for i, g in enumerate(group_data):
    g_ = create_group(g[0], scale=g[1])
    groups.append(g_)

compass = displayio.Group()

# Simulate the supplied compass heading
def heading(degrees, compass=compass):
    # clear the existing configuration
    t = len(compass)
    for i in range(0,t):
        compass.pop()

    #print("after clearing="+str(len(compass)))
    # find the index of the group that contains the desired heading
    index = to_index(degrees)
    # print("index="+str(index))

    left=to_degrees(circ_index(index-2))
    # print("left="+str(left))
    midpoint=left-int(tot_visible_degrees/2)
    if midpoint < 0:
        midpoint = 360 + midpoint
    # print("midpoint="+str(midpoint))
    right=midpoint-int(tot_visible_degrees/2)
    if right < 0:
        right = 360 + right
    # print("right="+str(right))

    # calculate the number of pixels we need to move the groups to show the
    # correct heading
    offset = int((degrees-midpoint)*ppd)
    # print("offset="+str(offset))

    compass.x = 0
    x = offset

    if degrees < 0 or degrees > 359:
        msg("Bad Heading",color=ERROR)
    else:
        i = circ_index(index-2)
        # print("i="+str(i))
        for n in range(5):
            l = circ_index(i+n,len(groups))
            # print("l="+str(l)+" at "+str(x))
            g_ = groups[l]
            g_.x = x
            compass.append(g_)
            x = x + int(30 * ppd)

    compass.append(Line(int(DISPLAY_WIDTH / 2),0,int(DISPLAY_WIDTH / 2),DISPLAY_HEIGHT,0xaaaaaa))
    cts = label.Label(font, text=str(degrees), color=color, scale=1)
    cts.anchor_point = (0.5, 0.5)
    cts.anchored_position = (DISPLAY_WIDTH / 2, 50)
    # compass.append(cts)

compass.y = compass.y - 30
display.show(compass)

heading(0)

def test_loop():
    for i in range(0,359):
        heading(i)
        time.sleep(0.1)

def main_loop():
    try:
        data = uart.readline()
        p = data.split()
        print(str(p))
        key = p[0]
        val = p[1]
        if key==b'HDG':
            heading(int(p[1]))
    except Exception as e:
        pass
        #msg(str(e),color=ERROR)

while True:
    main_loop()
#    pass
#    test_loop()
