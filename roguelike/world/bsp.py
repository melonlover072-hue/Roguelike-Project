"""BSP (Binary Space Partitioning) algorithm for dungeon generation, and room placement within the generated partitions.
"""

from __future__ import annotations

import random
from typing import Optional, Tuple


class BSPNode:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left: Optional[BSPNode] = None
        self.right: Optional[BSPNode] = None
        self.room: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h

    def split(self, min_size: int = 6, max_ratio: float = 0.7) -> bool:
        """Recursively split this node. Returns True if split happened."""
        if self.left or self.right:
            return False  # Already split

        # Decide horizontal or vertical split
        if self.width > self.height and self.width / self.height >= 1.25:
            split_horizontal = False
        elif self.height > self.width and self.height / self.width >= 1.25:
            split_horizontal = True
        else:
            split_horizontal = random.choice([True, False])

        # Check if we can split
        if split_horizontal:
            max_split = self.height - min_size
        else:
            max_split = self.width - min_size

        if max_split <= min_size:
            return False  # Too small to split

        # Pick split point
        split = random.randint(min_size, max_split)

        # Create children
        if split_horizontal:
            self.left = BSPNode(self.x, self.y, self.width, split)
            self.right = BSPNode(self.x, self.y + split, self.width, self.height - split)
        else:
            self.left = BSPNode(self.x, self.y, split, self.height)
            self.right = BSPNode(self.x + split, self.y, self.width - split, self.height)

        return True

    def create_rooms(self, min_room_size: int = 3) -> None:
        """Recursively create rooms in leaf nodes."""
        if self.left or self.right:
            if self.left:
                self.left.create_rooms(min_room_size)
            if self.right:
                self.right.create_rooms(min_room_size)
        else:
            # Leaf node - create room
            room_width = random.randint(min_room_size, max(min_room_size, self.width - 2))
            room_height = random.randint(min_room_size, max(min_room_size, self.height - 2))
            room_x = self.x + random.randint(1, max(1, self.width - room_width - 1))
            room_y = self.y + random.randint(1, max(1, self.height - room_height - 1))
            self.room = (room_x, room_y, room_width, room_height)

    def get_rooms(self) -> list:
        """Return all rooms from leaf nodes."""
        if self.left or self.right:
            rooms = []
            if self.left:
                rooms.extend(self.left.get_rooms())
            if self.right:
                rooms.extend(self.right.get_rooms())
            return rooms
        elif self.room:
            return [self.room]
        return []