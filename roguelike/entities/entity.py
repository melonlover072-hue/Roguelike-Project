"""A generic object on the map: the player, monsters, or items."""
from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.entities.fighter import Fighter
    from roguelike.entities.ai import BaseAI


class Entity:
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: Tuple[int, int, int],
        name: str = "<Unnamed>",
        blocks_movement: bool = True,
        fighter: Optional["Fighter"] = None,
        ai: Optional["BaseAI"] = None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

        self.fighter = fighter
        if self.fighter is not None:
            self.fighter.entity = self

        self.ai = ai
        if self.ai is not None:
            self.ai.entity = self

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def distance_to(self, other: "Entity") -> int:
        return max(abs(other.x - self.x), abs(other.y - self.y))
