"""AI components for enemies. Attached to Entity via composition."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine
    from roguelike.entities.entity import Entity


class BaseAI:
    def take_turn(self, entity: Entity, engine: Engine) -> None:
        raise NotImplementedError()


class BasicMonster(BaseAI):
    """Simple hostile AI: chase player if within 8 tiles, attack if adjacent."""

    def take_turn(self, entity: Entity, engine: Engine) -> None:
        player = engine.player
        if not player.fighter or not player.fighter.is_alive:
            return

        dx = player.x - entity.x
        dy = player.y - entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance

        if distance > 8:
            return  # Out of "sight" range

        if distance <= 1:
            # Melee attack
            from roguelike.engine.actions import perform_attack
            perform_attack(entity, player, engine)
            return

        # Step toward player
        step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

        dest_x = entity.x + step_x
        dest_y = entity.y + step_y

        if not engine.game_map.is_walkable(dest_x, dest_y):
            return

        for other in engine.entities:
            if (
                other is not entity
                and other.blocks_movement
                and other.x == dest_x
                and other.y == dest_y
            ):
                return

        entity.move(step_x, step_y)
