"""Level population: enemies, items, etc."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from roguelike.entities.enemies import (
    create_rat, create_bat, create_kobold, create_giant_ant, create_slime, create_cat,
    create_wolf, create_skeleton, create_goblin,
    create_orc, create_hobgoblin, create_zombie, create_imp, create_giant_spider,
    create_ogre, create_wraith, create_troll, create_mimic, create_chimera,
    create_dark_knight, create_dragon,
    create_rat_king, create_goblin_shaman, create_rust_monster,
)
from roguelike.world.item_spawner import spawn_items

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine


def populate_level(engine: "Engine", depth: int) -> None:
    """Spawn enemies and items for the current level based on depth."""
    engine.items_on_ground = spawn_items(engine.game_map, depth=depth)

    # --- Early pests (depth 1-2) ---
    for _ in range(max(4 - depth, 1)):
        engine.spawn_enemy(create_rat)
    for _ in range(max(3 - depth, 0)):
        engine.spawn_enemy(create_bat)

    if depth >= 1:
        for _ in range(2):
            engine.spawn_enemy(create_kobold)
        for _ in range(2):
            engine.spawn_enemy(create_giant_ant)
        for _ in range(1):
            engine.spawn_enemy(create_cat)

    if depth >= 2:
        for _ in range(2):
            engine.spawn_enemy(create_slime)

    # --- Mid-depth (depth 2-5) ---
    if depth >= 2:
        for _ in range(min(depth, 3)):
            engine.spawn_enemy(create_wolf)
        engine.spawn_enemy(create_skeleton)

    if depth >= 3:
        for _ in range(min(depth - 2, 3)):
            engine.spawn_enemy(create_orc)
        for _ in range(2):
            engine.spawn_enemy(create_zombie)
        for _ in range(min(depth - 2, 2)):
            engine.spawn_enemy(create_imp)

    if depth >= 4:
        for _ in range(min(depth - 3, 2)):
            engine.spawn_enemy(create_hobgoblin)
        for _ in range(min(depth - 3, 2)):
            engine.spawn_enemy(create_giant_spider)

    # --- Deep horrors (depth 5-8) ---
    if depth >= 5:
        for _ in range(min(depth - 4, 2)):
            engine.spawn_enemy(create_ogre)
        for _ in range(min(depth - 4, 2)):
            engine.spawn_enemy(create_wraith)

    if depth >= 6:
        for _ in range(min(depth - 5, 2)):
            engine.spawn_enemy(create_troll)
        engine.spawn_enemy(create_mimic)

    if depth >= 7:
        for _ in range(min(depth - 6, 1)):
            engine.spawn_enemy(create_chimera)

    # --- Very deep (depth 9+) ---
    if depth >= 9:
        engine.spawn_enemy(create_dark_knight)
        engine.spawn_enemy(create_dragon)

    # --- Goblins with equipment ---
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

    # --- Rare spawns ---
    if engine.rng.random() < 0.10:
        engine.spawn_enemy(create_rat_king)
    if engine.rng.random() < 0.08:
        engine.spawn_enemy(create_goblin_shaman)
    if depth >= 3 and engine.rng.random() < 0.05:
        engine.spawn_enemy(create_rust_monster)
