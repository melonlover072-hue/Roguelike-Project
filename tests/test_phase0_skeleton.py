"""Phase 0 smoke tests. None of these touch tcod's window/context, so they
run fine in CI with no display attached -- only game logic is under test.
"""
from roguelike.engine.actions import MovementAction
from roguelike.engine.engine import Engine
from roguelike.entities.entity import Entity
from roguelike.world.game_map import GameMap


def make_engine(width=30, height=20):
    game_map = GameMap(width, height)
    player = Entity(x=5, y=5, char="@", color=(255, 255, 255), name="Player")
    return Engine(player=player, game_map=game_map), game_map


def test_game_map_in_bounds():
    game_map = GameMap(30, 20)
    assert game_map.in_bounds(0, 0)
    assert game_map.in_bounds(29, 19)
    assert not game_map.in_bounds(-1, 0)
    assert not game_map.in_bounds(30, 20)


def test_test_room_is_walkable_in_the_middle():
    game_map = GameMap(30, 20)
    assert game_map.is_walkable(15, 10)


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
    # Force the player right up against the room's left wall.
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
