"""Entry point. Kept thin on purpose: window/context setup only."""
from __future__ import annotations

from pathlib import Path

import tcod

from roguelike.engine.engine import Engine
from roguelike.entities.entity import Entity
from roguelike.entities.fighter import Fighter
from roguelike.ui import layout
from roguelike.world.game_map import GameMap
from roguelike.world.level_generator import populate_level

TILE_SIZE = 16

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
]


def load_tileset() -> "tcod.tileset.Tileset | None":
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
    game_map = GameMap(layout.MAP_WIDTH, layout.MAP_HEIGHT, depth=1)

    # Get a valid starting position
    start_x, start_y = game_map.get_random_floor_tile()

    player = Entity(
        x=start_x,
        y=start_y,
        char="@",
        color=(255, 255, 255),
        name="Player",
        fighter=Fighter(hp=30, defense=2, power=5),
    )

    engine = Engine(player=player, game_map=game_map)
    populate_level(engine, depth=1)

    # Initial FOV calculation
    engine.update_fov()

    tileset = load_tileset()

    with tcod.context.new(
        columns=layout.SCREEN_WIDTH,
        rows=layout.SCREEN_HEIGHT,
        tileset=tileset,
        title="ADOM-inspired Roguelike -- Phase 2",
        vsync=True,
    ) as context:
        console = tcod.console.Console(layout.SCREEN_WIDTH, layout.SCREEN_HEIGHT, order="F")

        while True:
            engine.render(console)
            context.present(console)
            engine.handle_events()


if __name__ == "__main__":
    main()
