"""Phase 0/1/2 smoke tests."""
import numpy as np

from roguelike.engine.actions import (
    MovementAction,
    PickupAction,
    SelectItemAction,
    perform_attack,
)
from roguelike.engine.engine import Engine
from roguelike.entities.entity import Entity
from roguelike.entities.enemies import create_rat, create_wolf
from roguelike.entities.fighter import Fighter
from roguelike.entities.item import Potion
from roguelike.world import tile_types
from roguelike.world.game_map import GameMap


def make_engine():
    game_map = GameMap.__new__(GameMap)
    game_map.width, game_map.height = 10, 10
    game_map.depth = 1
    game_map.tiles = np.full((10, 10), fill_value=tile_types.WALL, order="F")
    game_map.tiles[2:8, 2:8] = tile_types.FLOOR
    game_map.rooms = [(2, 2, 6, 6)]
    game_map.corridors = []
    game_map.up_stairs = None
    game_map.down_stairs = None

    player = Entity(
        x=5,
        y=5,
        char="@",
        color=(255, 255, 255),
        name="Player",
        fighter=Fighter(hp=30, defense=2, power=5),
    )
    return Engine(player=player, game_map=game_map), game_map


def test_game_map_in_bounds():
    game_map = GameMap(30, 20)
    assert game_map.in_bounds(0, 0)
    assert game_map.in_bounds(29, 19)
    assert not game_map.in_bounds(-1, 0)
    assert not game_map.in_bounds(30, 20)


def test_generated_map_has_walkable_tiles():
    game_map = GameMap(30, 20)
    assert game_map.tiles["walkable"].any()


def test_generated_map_is_fully_connected():
    from collections import deque

    game_map = GameMap(60, 40)
    if not game_map.rooms:
        return

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
    engine.player.x, engine.player.y = 2, 5
    assert not game_map.is_walkable(1, 5)

    MovementAction(dx=-1, dy=0).perform(engine)

    assert engine.player.x == 2
    assert engine.player.y == 5


def test_movement_action_blocked_by_map_edge_does_not_crash():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 0, 0
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
    assert taken == 10
    assert fighter.hp == 0
    assert not fighter.is_alive


def test_fighter_heal_clamps_at_max_hp():
    fighter = Fighter(hp=30, defense=2, power=5)
    fighter.take_damage(5)
    healed = fighter.heal(999)
    assert healed == 5
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
    engine.player.fighter.take_damage(15)

    potion = Potion(healing_amount=10)
    potion.apply_effect(engine)

    assert engine.player.fighter.hp == 25
    assert "feel better" in engine.messages[-1]


def test_potion_at_full_health_does_not_overheal_or_crash():
    engine, _ = make_engine()

    potion = Potion(healing_amount=10)
    potion.apply_effect(engine)

    assert engine.player.fighter.hp == 30
    assert "already at full health" in engine.messages[-1]


def test_pickup_action_with_full_inventory_does_not_destroy_item():
    """Manual pickup must not destroy items when inventory is full."""
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    engine.inventory = [Potion() for _ in range(engine.max_inventory_size)]
    stuck_potion = Potion(x=5, y=5)
    engine.items_on_ground.append(stuck_potion)

    PickupAction().perform(engine)

    assert len(engine.inventory) == engine.max_inventory_size
    assert stuck_potion in engine.items_on_ground


def test_spawn_enemy_adds_a_fighter_entity_to_engine():
    engine, _ = make_engine()
    starting_count = len(engine.entities)

    enemy = engine.spawn_enemy(create_rat)

    assert len(engine.entities) == starting_count + 1
    assert enemy in engine.entities
    assert enemy.fighter is not None
    assert enemy.fighter.is_alive


def test_spawn_enemy_never_overlaps_an_existing_entity():
    engine, _ = make_engine()
    for _ in range(20):
        engine.spawn_enemy(create_rat)

    positions = [(e.x, e.y) for e in engine.entities]
    assert len(positions) == len(set(positions)), "Two entities ended up on the same tile"


# --- Phase 2: Combat & AI tests ---

def test_bump_attack_deals_damage():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    # Wolf has 10 HP / defense 1; player power 5 deals 4 damage, survives
    enemy = create_wolf(x=6, y=5)
    engine.entities.append(enemy)
    start_hp = enemy.fighter.hp

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter.hp < start_hp
    assert engine.player.x == 5  # Did not move onto enemy tile
    assert "attacks Wolf" in engine.messages[-2]


def test_bump_attack_kills_enemy():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    enemy = create_rat(x=6, y=5)
    engine.entities.append(enemy)
    # Rat has 5 HP, player deals max(5-0,1)=5 -- rat dies in one hit

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter is None
    assert enemy.char == "%"
    assert "dies" in engine.messages[-1]


def test_pickup_action_adds_to_inventory():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5
    potion = Potion(x=5, y=5)
    engine.items_on_ground.append(potion)

    PickupAction().perform(engine)

    assert potion in engine.inventory
    assert potion not in engine.items_on_ground


def test_enemy_ai_moves_toward_player():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5
    enemy = create_rat(x=2, y=2)
    engine.entities.append(enemy)
    start_pos = (enemy.x, enemy.y)

    enemy.ai.take_turn(enemy, engine)

    assert (enemy.x, enemy.y) != start_pos


def test_enemy_ai_attacks_when_adjacent():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    enemy = create_rat(x=6, y=5)
    engine.entities.append(enemy)
    start_hp = engine.player.fighter.hp

    enemy.ai.take_turn(enemy, engine)

    assert engine.player.fighter.hp < start_hp
    assert "Rat attacks" in engine.messages[-1]


def test_inventory_use_consumes_potion():
    engine, _ = make_engine()
    engine.player.fighter.take_damage(15)  # 15/30

    potion = Potion(healing_amount=10)
    engine.inventory.append(potion)

    SelectItemAction(0, "use").perform(engine)

    assert engine.player.fighter.hp == 25
    assert potion not in engine.inventory
    assert engine.game_state == "playing"
