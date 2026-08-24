"""Phase 0/1 smoke tests. None of these touch tcod's window/context, so they
run fine in CI with no display attached -- only game logic is under test.
"""
import numpy as np

from roguelike.engine.actions import MovementAction
from roguelike.engine.engine import Engine
from roguelike.entities.entity import Entity
from roguelike.entities.fighter import Fighter
from roguelike.entities.item import Potion
from roguelike.world import tile_types
from roguelike.world.game_map import GameMap


def make_engine():
    """Build an engine around a small, hand-built, fully deterministic map --
    NOT the random BSP generator. Movement/collision tests need to know
    exactly which tiles are floor vs wall; a randomly generated map can't
    guarantee that from run to run, which is exactly what made the old
    version of these tests flaky (see test_generated_map_* below for the
    tests that actually exercise the random generator's properties instead).
    """
    game_map = GameMap.__new__(GameMap)  # Bypass __init__ / generation entirely.
    game_map.width, game_map.height = 10, 10
    game_map.depth = 1
    game_map.tiles = np.full((10, 10), fill_value=tile_types.WALL, order="F")
    game_map.tiles[2:8, 2:8] = tile_types.FLOOR  # A known 6x6 open room.
    game_map.rooms = [(2, 2, 6, 6)]
    game_map.corridors = []
    game_map.up_stairs = None
    game_map.down_stairs = None

    player = Entity(x=5, y=5, char="@", color=(255, 255, 255), name="Player")
    return Engine(player=player, game_map=game_map), game_map


def test_game_map_in_bounds():
    game_map = GameMap(30, 20)
    assert game_map.in_bounds(0, 0)
    assert game_map.in_bounds(29, 19)
    assert not game_map.in_bounds(-1, 0)
    assert not game_map.in_bounds(30, 20)


def test_generated_map_has_walkable_tiles():
    """No matter how the BSP tree splits, generation must produce at least
    one walkable tile -- a map that's solid wall everywhere is a generator
    bug, regardless of where any specific coordinate happens to land."""
    game_map = GameMap(30, 20)
    assert game_map.tiles["walkable"].any()


def test_generated_map_is_fully_connected():
    """Every room must be reachable from the first room via floor tiles.
    This is the real property that matters -- not whether any one fixed
    coordinate happens to be floor, which depends on random room placement
    and will vary from run to run."""
    from collections import deque

    game_map = GameMap(60, 40)
    if not game_map.rooms:
        return  # Degenerate case: nothing to check.

    start = (
        game_map.rooms[0][0] + game_map.rooms[0][2] // 2,
        game_map.rooms[0][1] + game_map.rooms[0][3] // 2,
    )
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (
                game_map.in_bounds(nx, ny)
                and game_map.is_walkable(nx, ny)
                and (nx, ny) not in seen
            ):
                seen.add((nx, ny))
                queue.append((nx, ny))

    for rx, ry, rw, rh in game_map.rooms:
        center = (rx + rw // 2, ry + rh // 2)
        assert center in seen, f"Room at {center} is unreachable from spawn"


def test_map_edges_are_walls():
    game_map = GameMap(30, 20)
    assert not game_map.is_walkable(0, 0)
    assert not game_map.is_walkable(29, 19)


def test_movement_action_moves_player_into_open_floor():
    engine, _ = make_engine()
    start_x, start_y = engine.player.x, engine.player.y
    MovementAction(dx=1, dy=0).perform(engine)
    assert engine.player.x == start_x + 1
    assert engine.player.y == start_y


def test_movement_action_blocked_by_wall_does_not_move_player():
    engine, game_map = make_engine()
    # Force the player right up against the test room's left wall (tile x=1
    # is guaranteed wall on the hand-built 10x10 map from make_engine()).
    engine.player.x, engine.player.y = 2, 5
    assert not game_map.is_walkable(1, 5)

    MovementAction(dx=-1, dy=0).perform(engine)

    assert engine.player.x == 2  # Unchanged: the wall blocked the move.
    assert engine.player.y == 5


def test_movement_action_blocked_by_map_edge_does_not_crash():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 0, 0
    # Off the top-left corner of the map entirely.
    MovementAction(dx=-1, dy=-1).perform(engine)
    assert engine.player.x == 0
    assert engine.player.y == 0


def test_fighter_take_damage_reduces_hp():
    fighter = Fighter(hp=30, defense=2, power=5)
    taken = fighter.take_damage(10)
    assert taken == 10
    assert fighter.hp == 20


def test_fighter_take_damage_clamps_at_zero_not_negative():
    fighter = Fighter(hp=10, defense=2, power=5)
    taken = fighter.take_damage(999)
    assert taken == 10  # Only 10 HP existed to take, not 999.
    assert fighter.hp == 0
    assert not fighter.is_alive


def test_fighter_heal_clamps_at_max_hp():
    fighter = Fighter(hp=30, defense=2, power=5)
    fighter.take_damage(5)  # hp: 25/30
    healed = fighter.heal(999)
    assert healed == 5  # Only 5 HP of headroom existed, not 999.
    assert fighter.hp == 30


def test_fighter_is_alive():
    fighter = Fighter(hp=1, defense=0, power=0)
    assert fighter.is_alive
    fighter.take_damage(1)
    assert not fighter.is_alive


def test_entity_with_fighter_sets_back_reference():
    fighter = Fighter(hp=10, defense=0, power=0)
    entity = Entity(x=0, y=0, char="@", color=(255, 255, 255), fighter=fighter)
    assert entity.fighter is fighter
    assert fighter.entity is entity


def test_entity_without_fighter_has_none():
    entity = Entity(x=0, y=0, char="!", color=(255, 255, 255))
    assert entity.fighter is None


def test_potion_heals_player_through_fighter_component():
    engine, _ = make_engine()
    engine.player.fighter = Fighter(hp=30, defense=2, power=5)
    engine.player.fighter.take_damage(15)  # hp: 15/30

    potion = Potion(healing_amount=10)
    potion.apply_effect(engine)

    assert engine.player.fighter.hp == 25
    assert "feel better" in engine.messages[-1]


def test_potion_at_full_health_does_not_overheal_or_crash():
    engine, _ = make_engine()
    engine.player.fighter = Fighter(hp=30, defense=2, power=5)  # Already full.

    potion = Potion(healing_amount=10)
    potion.apply_effect(engine)  # Must not raise, and must not exceed max_hp.

    assert engine.player.fighter.hp == 30
    assert "already at full health" in engine.messages[-1]
