"""The Engine owns game state and the main loop. It deliberately knows
nothing about SDL/tcod window setup (that's main.py's job)
"""
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
        
        # Initialize RNG
        self.rng = np.random.default_rng()
        
        # Inventory and equipment
        self.inventory: List[Item] = []
        self.items_on_ground: List[Item] = []
        self.equipment: Dict[str, Equipment] = {}
        self.max_inventory_size = 20

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = input_handlers.handle_event(event)
            if action is not None:
                action.perform(self)

    def render(self, console: tcod.console.Console) -> None:
        render_functions.render_map(console, self.game_map)
        render_functions.render_items(console, self.items_on_ground, self.game_map)
        render_functions.render_entities(console, self.entities, self.game_map)
        render_functions.render_sidebar(console, self.player)
        render_functions.render_log(console, self.messages)

    def update_fov(self) -> None:
        """Recompute FOV based on player's current position."""
        from roguelike.engine.fov import compute_fov
        
        compute_fov(
            game_map=self.game_map,
            x=self.player.x,
            y=self.player.y,
            radius=8,
        )

    def add_message(self, message: str) -> None:
        """Add a message to the log."""
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    def spawn_enemy(self, enemy_factory) -> Entity:
        """Create an enemy and place it on a random floor tile."""

        for _ in range(100):  # Safety cap -- never hang the game over a spawn.
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