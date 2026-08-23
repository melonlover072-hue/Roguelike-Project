"""The Engine owns game state and the main loop. It deliberately knows
nothing about SDL/tcod window setup (that's main.py's job) so the engine
itself stays testable without needing a real display.
"""
from __future__ import annotations

from typing import List

import tcod

from roguelike.engine import input_handlers
from roguelike.entities.entity import Entity
from roguelike.ui import layout, render_functions
from roguelike.world.game_map import GameMap


class Engine:
    def __init__(self, player: Entity, game_map: GameMap):
        self.player = player
        self.game_map = game_map
        self.entities: List[Entity] = [player]
        self.messages: List[str] = ["Welcome, adventurer."]

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = input_handlers.handle_event(event)
            if action is not None:
                action.perform(self)

    def render(self, console: tcod.console.Console) -> None:
        console.clear()
        render_functions.render_map(console, self.game_map)
        render_functions.render_entities(console, self.entities)
        render_functions.render_sidebar(console, self.player)
        render_functions.render_log(console, self.messages)
