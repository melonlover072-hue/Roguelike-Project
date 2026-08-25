"""The Engine owns game state and the main loop."""
from __future__ import annotations

from typing import List, Dict

import numpy as np
import tcod

from roguelike.engine import input_handlers
from roguelike.entities.entity import Entity
from roguelike.entities.item import Item, Equipment
from roguelike.ui import layout
from roguelike.ui import render_functions
from roguelike.world.game_map import GameMap


class Engine:
    def __init__(self, player: Entity, game_map: GameMap):
        self.player = player
        self.game_map = game_map
        self.entities: List[Entity] = [player]
        self.messages: List[str] = ["Welcome, adventurer."]
        self.game_state = "playing"

        # Initialize RNG
        self.rng = np.random.default_rng()

        # Inventory and equipment
        self.inventory: List[Item] = []
        self.items_on_ground: List[Item] = []
        self.equipment: Dict[str, Equipment] = {}
        self.max_inventory_size = 20

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = input_handlers.handle_event(event, self.game_state)
            if action is not None:
                old_state = self.game_state
                action.perform(self)
                if (
                    old_state == "playing"
                    and self.game_state == "playing"
                    and self.player.fighter
                    and self.player.fighter.is_alive
                ):
                    self.handle_enemy_turns()

    def handle_enemy_turns(self) -> None:
        for entity in self.entities[:]:
            if entity is self.player:
                continue
            if entity.ai and entity.fighter and entity.fighter.is_alive:
                entity.ai.take_turn(entity, self)

    def render(self, console: tcod.console.Console) -> None:
        render_functions.render_map(console, self.game_map)
        render_functions.render_items(console, self.items_on_ground, self.game_map)
        render_functions.render_entities(console, self.entities, self.game_map)
        render_functions.render_sidebar(console, self.player, self.inventory, self.equipment)
        render_functions.render_log(console, self.messages)

        if self.game_state == "inventory_use":
            render_functions.render_inventory_menu(
                console, self.inventory, self.equipment, "Use which item?"
            )
        elif self.game_state == "inventory_drop":
            render_functions.render_inventory_menu(
                console, self.inventory, self.equipment, "Drop which item?"
            )
        elif self.game_state == "inventory_equip":
            render_functions.render_inventory_menu(
                console, self.inventory, self.equipment, "Equip/unequip which item?"
            )

    def update_fov(self) -> None:
        from roguelike.engine.fov import compute_fov

        compute_fov(
            game_map=self.game_map,
            x=self.player.x,
            y=self.player.y,
            radius=8,
        )

    def add_message(self, message: str) -> None:
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    def spawn_enemy(self, enemy_factory) -> Entity:
        for _ in range(100):
            x, y = self.game_map.get_random_floor_tile()
            if any(entity.x == x and entity.y == y for entity in self.entities):
                continue

            enemy = enemy_factory(x, y)
            self.entities.append(enemy)
            return enemy

        raise RuntimeError(
            "spawn_enemy: couldn't find a free tile after 100 attempts -- "
            "map may be too small or too crowded for the number of entities requested."
        )
