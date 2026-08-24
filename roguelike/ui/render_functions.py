"""All drawing lives here, kept out of Engine so rendering can be swapped
or unit-tested independently of game logic later."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import numpy as np
import tcod

from roguelike.ui import layout

if TYPE_CHECKING:
    from roguelike.entities.entity import Entity
    from roguelike.world.game_map import GameMap


def render_map(console: tcod.console.Console, game_map: "GameMap") -> None:
    """Render the map with FOV — visible tiles bright, explored dim, unexplored hidden."""
    
    # Get viewport slice
    viewport = (
        slice(layout.MAP_X, layout.MAP_X + game_map.width),
        slice(layout.MAP_Y, layout.MAP_Y + game_map.height),
    )
    
    # Start with empty (black) tiles
    ch = np.full((game_map.width, game_map.height), ord(" "), dtype=np.int32)
    fg = np.zeros((game_map.width, game_map.height, 3), dtype=np.uint8)
    bg = np.zeros((game_map.width, game_map.height, 3), dtype=np.uint8)
    
    # Visible tiles (bright)
    visible = game_map.tiles["visible"]
    ch[visible] = game_map.tiles["dark"]["ch"][visible]
    fg[visible] = game_map.tiles["dark"]["fg"][visible]
    bg[visible] = game_map.tiles["dark"]["bg"][visible]
    
    # Explored but not visible tiles (dimmer)
    explored_only = game_map.tiles["explored"] & ~visible
    ch[explored_only] = game_map.tiles["dark"]["ch"][explored_only]
    fg[explored_only] = game_map.tiles["dark"]["fg"][explored_only] // 2
    bg[explored_only] = game_map.tiles["dark"]["bg"][explored_only] // 2
    
    # Render to console - assign fg and bg separately
    console.rgb[viewport]["fg"] = fg
    console.rgb[viewport]["bg"] = bg
    console.ch[viewport] = ch


def render_entities(
    console: tcod.console.Console, 
    entities: Iterable["Entity"],
    game_map: "GameMap",
) -> None:
    for entity in entities:
        # Only draw entities that are in visible tiles
        if game_map.tiles[entity.x, entity.y]["visible"]:
            console.print(
                x=layout.MAP_X + entity.x,
                y=layout.MAP_Y + entity.y,
                string=entity.char,
                fg=entity.color,
            )

def render_sidebar(console: tcod.console.Console, player: "Entity") -> None:
    console.draw_frame(
        x=layout.SIDEBAR_X,
        y=layout.SIDEBAR_Y,
        width=layout.SIDEBAR_WIDTH,
        height=layout.MAP_HEIGHT,
        title="Character",
        clear=True,
        fg=(255, 255, 255),
        bg=(0, 0, 0),
    )
    console.print(
        x=layout.SIDEBAR_X + 2,
        y=layout.SIDEBAR_Y + 2,
        string=f"{player.name}",
    )
    console.print(
        x=layout.SIDEBAR_X + 2,
        y=layout.SIDEBAR_Y + 4,
        string=f"pos: {player.x},{player.y}",
    )
    if player.fighter is not None:
        console.print(
            x=layout.SIDEBAR_X + 2,
            y=layout.SIDEBAR_Y + 6,
            string=f"HP: {player.fighter.hp}/{player.fighter.max_hp}",
            fg=(0, 200, 0) if player.fighter.hp > player.fighter.max_hp // 3 else (200, 0, 0),
        )


def render_log(console: tcod.console.Console, messages: list[str]) -> None:
    console.draw_frame(
        x=layout.LOG_X,
        y=layout.LOG_Y,
        width=layout.SCREEN_WIDTH,
        height=layout.LOG_HEIGHT,
        title="Log",
        clear=True,
        fg=(255, 255, 255),
        bg=(0, 0, 0),
    )
    # Render the most recent messages, oldest at top, newest at bottom.
    visible = messages[-(layout.LOG_HEIGHT - 2) :]
    for i, message in enumerate(visible):
        console.print(x=layout.LOG_X + 2, y=layout.LOG_Y + 1 + i, string=message)
        
def render_items(console: tcod.console.Console, items: list, game_map: "GameMap") -> None:
    """Render items on the ground."""
    for item in items:
        if game_map.tiles[item.x, item.y]["visible"]:
            console.print(
                x=layout.MAP_X + item.x,
                y=layout.MAP_Y + item.y,
                string=item.char,
                fg=item.color,
            )