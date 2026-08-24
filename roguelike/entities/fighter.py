"""Combat stats as a component, not inheritance.

A Fighter is attached to an Entity (`entity.fighter = Fighter(...)`) rather
than Entity itself growing hp/attack/defense fields directly. This is what
lets the exact same class serve the player and every monster in Phase 2 --
an Entity with no Fighter is just scenery/an item, an Entity with one can
fight.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from roguelike.entities.entity import Entity


class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

        # Set by Entity.__init__ when this Fighter is attached -- lets combat
        # code go from "this Fighter took damage" back to "this Entity died"
        # (for messages, removing corpses from the map, etc.) without every
        # caller having to pass the owning entity around separately.
        self.entity: Optional["Entity"] = None

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> int:
        """Heal up to `amount`, clamped at max_hp. Returns the amount actually healed."""
        new_hp = min(self.hp + amount, self.max_hp)
        healed = new_hp - self.hp
        self.hp = new_hp
        return healed

    def take_damage(self, amount: int) -> int:
        """Apply damage, clamped at 0. Returns the amount actually taken."""
        new_hp = max(self.hp - amount, 0)
        taken = self.hp - new_hp
        self.hp = new_hp
        return taken
