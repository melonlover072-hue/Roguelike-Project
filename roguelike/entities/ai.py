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
        distance = max(abs(dx), abs(dy))

        if distance > 8:
            return

        if distance <= 1:
            from roguelike.engine.actions import perform_attack
            perform_attack(entity, player, engine)
            return

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


class CowardlyAI(BaseAI):
    """Flees when hurt (<= 50% HP); fights normally otherwise."""

    def take_turn(self, entity: Entity, engine: Engine) -> None:
        player = engine.player
        if not player.fighter or not player.fighter.is_alive:
            return
        if not entity.fighter or not entity.fighter.is_alive:
            return

        # Flee if hurt
        if entity.fighter.hp <= entity.fighter.max_hp // 2:
            dx = entity.x - player.x
            dy = entity.y - player.y
            step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
            step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
            dest_x = entity.x + step_x
            dest_y = entity.y + step_y
            if engine.game_map.is_walkable(dest_x, dest_y):
                blocked = False
                for other in engine.entities:
                    if (
                        other is not entity
                        and other.blocks_movement
                        and other.x == dest_x
                        and other.y == dest_y
                    ):
                        blocked = True
                        break
                if not blocked:
                    entity.move(step_x, step_y)
                    return
            # Can't flee — fight instead

        BasicMonster().take_turn(entity, engine)


class SlowAI(BaseAI):
    """Acts only every N turns (default 2)."""

    def __init__(self, speed: int = 2):
        self.speed = speed
        self.turn_count = 0

    def take_turn(self, entity: Entity, engine: Engine) -> None:
        self.turn_count += 1
        if self.turn_count % self.speed != 0:
            return
        BasicMonster().take_turn(entity, engine)


class MimicAI(BaseAI):
    """Waits disguised until the player is adjacent, then reveals and attacks."""

    def take_turn(self, entity: Entity, engine: Engine) -> None:
        if getattr(entity, "disguised", False):
            distance = entity.distance_to(engine.player)
            if distance <= 1:
                entity.disguised = False
                entity.name = entity.real_name
                entity.char = "m"
                entity.blocks_movement = True
                entity.color = (180, 140, 100)
                engine.add_message(f"The {entity.disguised_name} was a mimic!")
                from roguelike.engine.actions import perform_attack
                perform_attack(entity, engine.player, engine)
                return
            return
        BasicMonster().take_turn(entity, engine)
