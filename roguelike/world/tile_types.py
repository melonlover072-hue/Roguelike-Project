"""Defines the numpy structured dtype used for every tile on the map.

Using a structured array (instead of a Python object per tile) means the
whole map can be rendered and queried with vectorized numpy operations
instead of nested Python loops, which is much faster.
"""
from __future__ import annotations

import numpy as np

# Graphic: the (character, foreground, background) triple tcod expects
# for a single console cell.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes for RGB foreground.
        ("bg", "3B"),  # 3 unsigned bytes for RGB background.
    ]
)

# A tile: whether it can be walked on / seen through, and what it looks like.
tile_dt = np.dtype(
    [
        ("walkable", bool),
        ("transparent", bool),
        ("visible", bool),    # For FOV
        ("explored", bool),   # For map memory
        ("dark", graphic_dt),
    ]
)


def new_tile(*, walkable: int, transparent: int, dark: tuple) -> np.ndarray:
    return np.array((walkable, transparent, False, False, dark), dtype=tile_dt)


FLOOR = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (50, 50, 50)),
)

WALL = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (255, 255, 255), (20, 20, 20)),
)
