"""Level population: enemies, items, etc."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from roguelike.entities.enemies import create_rat, create_wolf, create_skeleton, create_goblin
from roguelike.world.item_spawner import spawn_items

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine


def populate_level(engine: "Engine", depth: int) -> None:
    """Spawn enemies and items for the current level based on depth."""
    engine.items_on_ground = spawn_items(engine.game_map, depth=depth)

    # Rats: fewer as you go deeper
    for _ in range(max(6 - depth, 2)):
        engine.spawn_enemy(create_rat)

    # Wolves: more as you go deeper
    for _ in range(min(depth, 3)):
        engine.spawn_enemy(create_wolf)

    # Skeletons appear at depth 2+
    if depth >= 2:
        engine.spawn_enemy(create_skeleton)

    # Goblins with equipment chance
    num_goblins = min(depth + 1, 5)
    for _ in range(num_goblins):
        weapon = None
        roll = engine.rng.random()
        if roll < 0.15:
            weapon = "axe"
        elif roll < 0.35:
            weapon = "sword"
        elif roll < 0.60:
            weapon = "dagger"

        factory = functools.partial(create_goblin, weapon=weapon)
        engine.spawn_enemy(factory)
