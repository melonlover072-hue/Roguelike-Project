"""The Engine owns game state and the main loop. It deliberately knows
nothing about SDL/tcod window setup (that's main.py's job)
"""
from __future__ import annotations

from typing import List, Dict

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
        # Optional: Keep log from growing too large
        if len(self.messages) > 100:
            self.messages.pop(0)
            from roguelike.entities.entity import Entity
from roguelike.entities.enemies import (
    create_rat,
    create_wolf,
    create_skeleton,
    create_goblin,
)


    def spawn_enemy(
    enemy_factory,
    x: int,
    y: int,
) -> Entity:
    return enemy_factory(x, y)