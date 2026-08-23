"""Phase 0 map: a single hardcoded room, just enough to prove collision
and rendering work. Real procedural generation (BSP rooms, cellular-automata
caves) replaces `_carve_test_room` in Phase 1 -- nothing above this module
needs to change when that happens, which is the point of keeping map data
and map generation separate from the start.
"""
from __future__ import annotations

import numpy as np

from roguelike.world import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Everything starts as solid wall; we carve out floor space.
        self.tiles = np.full((width, height), fill_value=tile_types.WALL, order="F")
        self._carve_test_room()

    def _carve_test_room(self) -> None:
        """Hardcoded rectangular room, used only until Phase 1 replaces this
        with real generation. Deliberately simple so collision logic can be
        proven correct before anything procedural is layered on top."""
        x1, y1 = 2, 2
        x2, y2 = self.width - 3, self.height - 3
        self.tiles[x1:x2, y1:y2] = tile_types.FLOOR

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns True if x and y are inside the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        return bool(self.tiles[x, y]["walkable"])
