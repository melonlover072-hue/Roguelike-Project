"""All drawing lives here, kept out of Engine so rendering can be swapped
or unit-tested independently of game logic later."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import tcod

from roguelike.ui import layout

if TYPE_CHECKING:
    from roguelike.entities.entity import Entity
    from roguelike.world.game_map import GameMap


def render_map(console: tcod.console.Console, game_map: "GameMap") -> None:
    """Blit the map's tile graphics into the map viewport region.

    Phase 0 has no FOV yet, so this just draws every tile's "dark" graphic
    unconditionally -- Phase 1 adds a visible/explored mask here without
    needing to change anything outside this function.
    """
    console.rgb[
        layout.MAP_X : layout.MAP_X + game_map.width,
        layout.MAP_Y : layout.MAP_Y + game_map.height,
    ] = game_map.tiles["dark"]


def render_entities(console: tcod.console.Console, entities: Iterable["Entity"]) -> None:
    for entity in entities:
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
