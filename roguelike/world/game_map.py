""" GameMap class for the game, including BSP-based dungeon generation, room and corridor carving, and tile management.
"""
from __future__ import annotations

import numpy as np
import random

from roguelike.world import tile_types
from roguelike.world.bsp import BSPNode


class GameMap:
    def __init__(self, width: int, height: int, depth: int = 1):
        self.width = width
        self.height = height
        self.depth = depth
        self.tiles = np.full((width, height), fill_value=tile_types.WALL, order="F")
        self.rooms = []
        self.corridors = []
        self.up_stairs = None
        self.down_stairs = None
        
        self._generate_bsp_dungeon()

    def _generate_bsp_dungeon(self) -> None:
        """Generate a BSP-based dungeon level."""
        root = BSPNode(0, 0, self.width, self.height)
        
        # Split recursively
        nodes_to_split = [root]
        while nodes_to_split:
            node = nodes_to_split.pop()
            if node.split():
                nodes_to_split.extend([node.left, node.right])
        
        # Create rooms in leaves
        root.create_rooms()
        self.rooms = root.get_rooms()
        
        # Carve rooms
        for (x, y, w, h) in self.rooms:
            self._carve_room(x, y, w, h)
        
        # Connect rooms with corridors
        self._connect_rooms()
        
        # Place stairs
        self._place_stairs()

    def _carve_room(self, x: int, y: int, width: int, height: int) -> None:
        """Carve a room into the tile grid."""
        self.tiles[x:x+width, y:y+height] = tile_types.FLOOR

    def _connect_rooms(self) -> None:
        """Connect all rooms with simple L-shaped corridors."""
        for i in range(len(self.rooms) - 1):
            x1, y1, w1, h1 = self.rooms[i]
            x2, y2, w2, h2 = self.rooms[i + 1]
            
            # Room centers
            cx1 = x1 + w1 // 2
            cy1 = y1 + h1 // 2
            cx2 = x2 + w2 // 2
            cy2 = y2 + h2 // 2
            
            # L-shaped corridor
            self._carve_corridor(cx1, cy1, cx2, cy2)

    def _carve_corridor(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Carve an L-shaped corridor between two points."""
        # Horizontal then vertical
        if random.random() < 0.5:
            self._carve_horizontal(x1, x2, y1)
            self._carve_vertical(y1, y2, x2)
        # Vertical then horizontal
        else:
            self._carve_vertical(y1, y2, x1)
            self._carve_horizontal(x1, x2, y2)

    def _carve_horizontal(self, x1: int, x2: int, y: int) -> None:
        """Carve a horizontal corridor."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x, y] = tile_types.FLOOR

    def _carve_vertical(self, y1: int, y2: int, x: int) -> None:
        """Carve a vertical corridor."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x, y] = tile_types.FLOOR

    def _place_stairs(self) -> None:
        """Place up and down stairs in first/last rooms."""
        if not self.rooms:
            return
        
        # Up stairs in first room
        first_room = self.rooms[0]
        self.up_stairs = (first_room[0] + first_room[2] // 2, 
                          first_room[1] + first_room[3] // 2)
        
        # Down stairs in last room
        last_room = self.rooms[-1]
        self.down_stairs = (last_room[0] + last_room[2] // 2, 
                           last_room[1] + last_room[3] // 2)

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns True if x and y are inside the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        return bool(self.tiles[x, y]["walkable"])

    def get_random_floor_tile(self) -> tuple[int, int]:
        """Return a random walkable floor tile (prefer room centers)."""
        if self.rooms:
            # Pick a random room and use its center
            room = self.rooms[np.random.randint(len(self.rooms))]
            x, y, w, h = room
            return (x + w // 2, y + h // 2)
        
        # Fallback: find any walkable tile
        floor_tiles = np.argwhere(self.tiles["walkable"])
        if len(floor_tiles) == 0:
            return (self.width // 2, self.height // 2)
        
        idx = np.random.randint(len(floor_tiles))
        x, y = floor_tiles[idx]
        return (min(max(int(x), 0), self.width - 1), 
                min(max(int(y), 0), self.height - 1))