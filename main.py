"""Entry point. Kept thin on purpose: window/context setup only, everything
else lives in the `roguelike` package so it can be imported and tested
without a real display.
"""
from __future__ import annotations

from pathlib import Path

import tcod

from roguelike.engine.engine import Engine
from roguelike.entities.entity import Entity
from roguelike.ui import layout
from roguelike.world.game_map import GameMap

TILE_SIZE = 16

# Common install locations for DejaVu Sans Mono (open-source, freely
# licensed under the Bitstream Vera Fonts license). On Linux this usually
# comes from the `fonts-dejavu-core` package; on macOS/Windows you may need
# to point this at any monospace TTF you have installed, or swap in a real
# codepage-437 tileset image later (see the note below).
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
]


def load_tileset() -> "tcod.tileset.Tileset | None":
    """Try to load a real monospace tileset so the window renders cleanly.

    Falls back to tcod's built-in default (tileset=None) if none of the
    candidate fonts exist -- that fallback works but looks rough and prints
    a font-loading warning, so this is worth fixing properly per-machine
    rather than living with the fallback long-term. Swapping in an actual
    codepage-437 bitmap tileset image (the traditional roguelike look) is a
    good Phase 7 polish item once the game itself is further along.
    """
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            return tcod.tileset.load_truetype_font(path, TILE_SIZE, TILE_SIZE)
    print(
        "No bundled monospace font found -- falling back to tcod's default "
        "tileset. Install `fonts-dejavu-core` (Linux) or edit FONT_CANDIDATES "
        "in main.py to point at a monospace TTF you have installed."
    )
    return None


def main() -> None:
    game_map = GameMap(layout.MAP_WIDTH, layout.MAP_HEIGHT)

    player = Entity(
        x=layout.MAP_WIDTH // 2,
        y=layout.MAP_HEIGHT // 2,
        char="@",
        color=(255, 255, 255),
        name="Player",
    )

    engine = Engine(player=player, game_map=game_map)
    tileset = load_tileset()

    with tcod.context.new(
        columns=layout.SCREEN_WIDTH,
        rows=layout.SCREEN_HEIGHT,
        tileset=tileset,
        title="ADOM-inspired Roguelike -- Phase 0",
        vsync=True,
    ) as context:
        console = tcod.console.Console(layout.SCREEN_WIDTH, layout.SCREEN_HEIGHT, order="F")

        while True:
            engine.render(console)
            context.present(console)
            engine.handle_events()


if __name__ == "__main__":
    main()
