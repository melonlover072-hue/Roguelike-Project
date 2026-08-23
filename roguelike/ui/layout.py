"""Single source of truth for screen geometry.

ADOM-style UI is three regions of one character grid: a map viewport, a
stats sidebar, and a message log. Keeping the numbers here (instead of
scattered as magic numbers through render code) means resizing the layout
later is a one-file change.
"""

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 45

SIDEBAR_WIDTH = 20
LOG_HEIGHT = 8

MAP_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT - LOG_HEIGHT

# Top-left corner offsets of each region within the full screen console.
MAP_X, MAP_Y = 0, 0
SIDEBAR_X, SIDEBAR_Y = MAP_WIDTH, 0
LOG_X, LOG_Y = 0, MAP_HEIGHT
