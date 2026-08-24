"""A generic object on the map: the player, monsters, or items.

Stats live on an optional `Fighter` component (see fighter.py), attached via
composition rather than Entity growing hp/attack fields itself -- an Entity
with no Fighter is scenery or an item; one with a Fighter can fight.
"""
from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.entities.fighter import Fighter


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

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
