"""A generic object on the map: the player, monsters, or items.

Phase 0 keeps this deliberately minimal (position + appearance + a movement
blocker flag). Phase 2 onward will move stats, AI, and inventory onto this
via composition (an `ai` attribute, an `inventory` attribute, etc.) rather
than growing this class into a god object -- that split is set up now so
later phases don't require reworking this file.
"""
from __future__ import annotations

from typing import Tuple


class Entity:
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: Tuple[int, int, int],
        name: str = "<Unnamed>",
        blocks_movement: bool = True,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
