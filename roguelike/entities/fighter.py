"""Combat stats as a component, not inheritance."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    from roguelike.entities.entity import Entity
    from roguelike.entities.status_effects import StatusEffect


class Fighter:
    def __init__(
        self,
        hp: int,
        defense: int,
        power: int,
        on_hit_status: List[Tuple[str, float, int]] | None = None,
    ):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.on_hit_status = on_hit_status or []  # [(status_name, chance, duration)]

        self.entity: Optional["Entity"] = None
        self.status_effects: List["StatusEffect"] = []

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> int:
        new_hp = min(self.hp + amount, self.max_hp)
        healed = new_hp - self.hp
        self.hp = new_hp
        return healed

    def take_damage(self, amount: int) -> int:
        new_hp = max(self.hp - amount, 0)
        taken = self.hp - new_hp
        self.hp = new_hp
        return taken

    def add_status_effect(self, effect: "StatusEffect") -> None:
        self.status_effects.append(effect)

    def tick_status_effects(self, engine: "Engine") -> None:
        """Tick all active status effects. If one kills the entity, handle death immediately."""
        for effect in self.status_effects[:]:
            effect.tick(self.entity, engine)
            if self.entity and self.entity.fighter and not self.entity.fighter.is_alive:
                from roguelike.engine.actions import _handle_death
                _handle_death(self.entity, engine)
                return
            if effect.duration <= 0:
                self.status_effects.remove(effect)
