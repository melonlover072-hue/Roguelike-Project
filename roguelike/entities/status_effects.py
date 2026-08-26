"""Status effects that attach to Fighters and tick each turn."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine
    from roguelike.entities.entity import Entity


class StatusEffect:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def tick(self, entity: Entity, engine: Engine) -> None:
        """Apply per-turn effect and decrement duration."""
        self.duration -= 1


class Poison(StatusEffect):
    """Deals damage each turn for a duration."""

    def __init__(self, damage_per_turn: int = 2, duration: int = 3):
        super().__init__("poison", duration)
        self.damage_per_turn = damage_per_turn

    def tick(self, entity: Entity, engine: Engine) -> None:
        if entity.fighter:
            entity.fighter.take_damage(self.damage_per_turn)
            engine.add_message(
                f"{entity.name} takes {self.damage_per_turn} poison damage!"
            )
        super().tick(entity, engine)
