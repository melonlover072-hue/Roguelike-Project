"""Actions decouple 'what key was pressed' from 'what happens in the game'."""
from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike.engine.fov import compute_fov
from roguelike.entities.item import Consumable, Equipment

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine
    from roguelike.entities.entity import Entity


class Action:
    def perform(self, engine: "Engine") -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: "Engine") -> None:
        raise SystemExit()


class WaitAction(Action):
    def perform(self, engine: "Engine") -> None:
        pass


class PickupAction(Action):
    def perform(self, engine: "Engine") -> None:
        for item in engine.items_on_ground[:]:
            if item.x == engine.player.x and item.y == engine.player.y:
                if item.pick_up(engine):
                    engine.items_on_ground.remove(item)
                return
        engine.add_message("There is nothing here to pick up.")


class DescendAction(Action):
    def perform(self, engine: "Engine") -> None:
        engine.descend()


class AscendAction(Action):
    def perform(self, engine: "Engine") -> None:
        engine.ascend()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def perform(self, engine: "Engine") -> None:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy

        if not engine.game_map.is_walkable(dest_x, dest_y):
            return

        # Check for disguised mimic on destination tile
        for entity in engine.entities:
            if getattr(entity, "disguised", False) and entity.x == dest_x and entity.y == dest_y:
                entity.disguised = False
                entity.name = entity.real_name
                entity.char = "m"
                entity.blocks_movement = True
                entity.color = (180, 140, 100)
                engine.add_message(f"The {entity.disguised_name} was a mimic!")
                perform_attack(engine.player, entity, engine)
                return

        # Check for a living enemy to bump-attack
        target = None
        for entity in engine.entities:
            if (
                entity is not engine.player
                and entity.blocks_movement
                and entity.x == dest_x
                and entity.y == dest_y
                and entity.fighter
                and entity.fighter.is_alive
            ):
                target = entity
                break

        if target:
            perform_attack(engine.player, target, engine)
            return

        engine.player.move(self.dx, self.dy)
        engine.update_fov()


class InventoryUseAction(Action):
    def perform(self, engine: "Engine") -> None:
        if not engine.inventory:
            engine.add_message("Your inventory is empty.")
            return
        engine.game_state = "inventory_use"


class InventoryDropAction(Action):
    def perform(self, engine: "Engine") -> None:
        if not engine.inventory:
            engine.add_message("Your inventory is empty.")
            return
        engine.game_state = "inventory_drop"


class InventoryEquipAction(Action):
    def perform(self, engine: "Engine") -> None:
        if not engine.inventory:
            engine.add_message("Your inventory is empty.")
            return
        engine.game_state = "inventory_equip"


class SelectItemAction(Action):
    def __init__(self, index: int, mode: str):
        self.index = index
        self.mode = mode

    def perform(self, engine: "Engine") -> None:
        if self.index < 0 or self.index >= len(engine.inventory):
            engine.add_message("Invalid selection.")
            engine.game_state = "playing"
            return

        item = engine.inventory[self.index]

        if self.mode == "use":
            item.use(engine)
        elif self.mode == "drop":
            item.drop(engine)
        elif self.mode == "equip":
            if isinstance(item, Equipment):
                if getattr(item, "equipped", False):
                    item.unequip(engine)
                else:
                    item.equip(engine)
            else:
                engine.add_message(f"The {item.display_name} cannot be equipped.")

        engine.game_state = "playing"


class CancelMenuAction(Action):
    def perform(self, engine: "Engine") -> None:
        engine.game_state = "playing"
        engine.add_message("Cancelled.")


def perform_attack(attacker: "Entity", target: "Entity", engine: "Engine") -> None:
    """Shared combat routine used by both player bump-attacks and enemy AI."""
    if attacker.fighter is None or target.fighter is None:
        return

    damage = max(attacker.fighter.power - target.fighter.defense, 1)
    target.fighter.take_damage(damage)

    engine.add_message(f"{attacker.name} attacks {target.name} for {damage} damage!")

    # On-hit status effects (e.g. poison)
    if target.fighter and target.fighter.is_alive and attacker.fighter.on_hit_status:
        for status_name, chance, duration in attacker.fighter.on_hit_status:
            if engine.rng.random() < chance:
                if status_name == "poison":
                    from roguelike.entities.status_effects import Poison
                    target.fighter.add_status_effect(Poison(damage_per_turn=2, duration=duration))
                    engine.add_message(f"{target.name} is poisoned!")

    if not target.fighter.is_alive:
        _handle_death(target, engine)


def _handle_death(entity: "Entity", engine: "Engine") -> None:
    """Handle an entity dying — messages, corpse conversion, loot drops."""
    engine.add_message(f"{entity.name} dies!")
    entity.char = "%"
    entity.color = (139, 0, 0)
    entity.blocks_movement = False
    entity.name = f"remains of {entity.name}"
    entity.fighter = None
    entity.ai = None

    # Drop pre-built loot (e.g. goblin weapons)
    if hasattr(entity, "loot") and entity.loot:
        for item in entity.loot:
            item.x = entity.x
            item.y = entity.y
            engine.items_on_ground.append(item)
        engine.add_message(f"The {entity.name} drops something!")

    # Roll loot table
    if hasattr(entity, "loot_table") and entity.loot_table:
        for factory, chance in entity.loot_table:
            if engine.rng.random() < chance:
                item = factory(x=entity.x, y=entity.y)
                engine.items_on_ground.append(item)
                engine.add_message(f"The {entity.name} drops a {item.name}!")
