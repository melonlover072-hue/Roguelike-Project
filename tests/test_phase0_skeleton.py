"""Phase 0/1/2/3 smoke tests."""
import numpy as np

from roguelike.engine.actions import (
    MovementAction,
    PickupAction,
    SelectItemAction,
    perform_attack,
)
from roguelike.engine.engine import Engine
from roguelike.entities.ai import BasicMonster, CowardlyAI, SlowAI, MimicAI
from roguelike.entities.entity import Entity
from roguelike.entities.enemies import (
    create_rat, create_wolf, create_goblin,
    create_kobold, create_zombie, create_mimic, create_giant_spider,
    create_orc, create_dark_knight, create_dragon, create_rat_king,
)
from roguelike.entities.fighter import Fighter
from roguelike.entities.item import Potion, create_dagger, create_sword, create_axe
from roguelike.entities.status_effects import Poison
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
        name="Hero",
        fighter=Fighter(hp=30, defense=2, power=5),
    )
    return Engine(player=player, game_map=game_map), game_map


# --- Phase 0: Map tests ---

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


# --- Phase 1: Movement tests ---

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


# --- Phase 1: Fighter tests ---

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


# --- Phase 1: Item tests ---

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
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    engine.inventory = [Potion() for _ in range(engine.max_inventory_size)]
    stuck_potion = Potion(x=5, y=5)
    engine.items_on_ground.append(stuck_potion)

    PickupAction().perform(engine)

    assert len(engine.inventory) == engine.max_inventory_size
    assert stuck_potion in engine.items_on_ground


def test_pickup_action_adds_to_inventory():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5
    potion = Potion(x=5, y=5)
    engine.items_on_ground.append(potion)

    PickupAction().perform(engine)

    assert potion in engine.inventory
    assert potion not in engine.items_on_ground


# --- Phase 1: Spawn tests ---

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

    enemy = create_wolf(x=6, y=5)
    engine.entities.append(enemy)
    start_hp = enemy.fighter.hp

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter.hp < start_hp
    assert engine.player.x == 5
    assert "attacks Wolf" in engine.messages[-1]


def test_bump_attack_kills_enemy():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    enemy = create_rat(x=6, y=5)
    engine.entities.append(enemy)

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter is None
    assert enemy.char == "%"
    assert "dies" in engine.messages[-1]


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
    engine.player.fighter.take_damage(15)

    potion = Potion(healing_amount=10)
    engine.inventory.append(potion)

    SelectItemAction(0, "use").perform(engine)

    assert engine.player.fighter.hp == 25
    assert potion not in engine.inventory
    assert engine.game_state == "playing"


# --- Phase 3: Depth tests ---

def test_descend_increases_depth():
    engine, _ = make_engine()
    engine.depth = 1
    engine.game_map.down_stairs = (5, 5)
    engine.player.x, engine.player.y = 5, 5
    engine.descend()
    assert engine.depth == 2
    assert engine.game_map is not None


def test_cannot_ascend_from_depth_1():
    engine, _ = make_engine()
    engine.depth = 1
    engine.game_map.up_stairs = (5, 5)
    engine.player.x, engine.player.y = 5, 5
    engine.ascend()
    assert engine.depth == 1
    assert "can't leave" in engine.messages[-1]


def test_ascend_restores_previous_level():
    engine, _ = make_engine()
    engine.depth = 1
    engine.game_map.down_stairs = (5, 5)
    engine.player.x, engine.player.y = 5, 5

    engine.descend()
    assert engine.depth == 2

    engine.player.x, engine.player.y = engine.game_map.up_stairs
    engine.ascend()
    assert engine.depth == 1


# --- Phase 3: Equipment tests ---

def test_equipped_goblin_has_higher_power():
    naked = create_goblin(0, 0)
    armed = create_goblin(0, 0, weapon="axe")
    assert armed.fighter.power > naked.fighter.power


def test_killing_equipped_goblin_drops_weapon():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5
    engine.player.fighter.power = 8

    enemy = create_goblin(6, 5, weapon="dagger")
    engine.entities.append(enemy)

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter is None
    dropped = [i for i in engine.items_on_ground if i.name == "Dagger"]
    assert len(dropped) == 1


def test_equipping_weapon_increases_player_power():
    engine, _ = make_engine()
    base_power = engine.player.fighter.power

    sword = create_sword()
    engine.inventory.append(sword)
    sword.equip(engine)

    assert engine.player.fighter.power == base_power + 2
    assert "equip" in engine.messages[-1]


def test_unequipping_weapon_restores_player_power():
    engine, _ = make_engine()
    base_power = engine.player.fighter.power

    axe = create_axe()
    engine.inventory.append(axe)
    axe.equip(engine)
    assert engine.player.fighter.power == base_power + 3

    axe.unequip(engine)
    assert engine.player.fighter.power == base_power


# --- Phase 4: Status effects ---

def test_poison_ticks_and_deals_damage():
    engine, _ = make_engine()
    engine.player.fighter.take_damage(0)  # Ensure fighter exists
    start_hp = engine.player.fighter.hp

    engine.player.fighter.add_status_effect(Poison(damage_per_turn=2, duration=3))
    engine._tick_status_effects()

    assert engine.player.fighter.hp == start_hp - 2
    assert "poison" in engine.messages[-1].lower()


def test_poison_kills_entity():
    engine, _ = make_engine()
    enemy = create_rat(x=5, y=5)
    engine.entities.append(enemy)
    enemy.fighter.hp = 2  # Set low HP

    enemy.fighter.add_status_effect(Poison(damage_per_turn=5, duration=1))
    engine._tick_status_effects()

    assert enemy.fighter is None  # Died and was cleaned up
    assert enemy.char == "%"


def test_giant_spider_applies_poison_on_hit():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    spider = create_giant_spider(x=6, y=5)
    engine.entities.append(spider)
    # Force poison to always proc
    engine.rng = type("Rng", (), {"random": lambda self: 0.0})()

    MovementAction(dx=1, dy=0).perform(engine)

    assert len(engine.player.fighter.status_effects) > 0
    assert any(e.name == "poison" for e in engine.player.fighter.status_effects)


# --- Phase 4: Loot tables ---

def test_enemy_loot_table_drop():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5
    engine.player.fighter.power = 30  # One-shot anything

    enemy = create_rat_king(x=6, y=5)
    engine.entities.append(enemy)

    MovementAction(dx=1, dy=0).perform(engine)

    assert enemy.fighter is None
    # Rat King has 100% Potion drop
    dropped_potions = [i for i in engine.items_on_ground if isinstance(i, Potion)]
    assert len(dropped_potions) >= 1


# --- Phase 4: New AI behaviors ---

def test_cowardly_ai_flees_when_hurt():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    kobold = create_kobold(x=4, y=5)
    engine.entities.append(kobold)
    kobold.fighter.hp = 1  # Hurt (max_hp=6, so <= 3 would flee)
    start_x = kobold.x

    kobold.ai.take_turn(kobold, engine)

    assert kobold.x != start_x  # Should have fled away from player at (5,5)


def test_slow_ai_acts_every_other_turn():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    zombie = create_zombie(x=2, y=2)
    engine.entities.append(zombie)
    start_pos = (zombie.x, zombie.y)

    zombie.ai.take_turn(zombie, engine)  # turn_count = 1, should not act
    assert (zombie.x, zombie.y) == start_pos

    zombie.ai.take_turn(zombie, engine)  # turn_count = 2, should act
    assert (zombie.x, zombie.y) != start_pos


def test_mimic_reveals_when_bumped():
    engine, _ = make_engine()
    engine.player.x, engine.player.y = 5, 5

    mimic = create_mimic(x=6, y=5)
    engine.entities.append(mimic)
    assert getattr(mimic, "disguised", False)
    assert mimic.blocks_movement is False

    MovementAction(dx=1, dy=0).perform(engine)

    assert not getattr(mimic, "disguised", False)
    assert mimic.name == "Mimic"
    assert mimic.blocks_movement is True
    assert "mimic" in engine.messages[-2].lower()


# --- Phase 4: New enemy sanity checks ---

def test_new_enemies_have_fighters():
    enemies = [
        create_bat(0, 0),
        create_kobold(0, 0),
        create_orc(0, 0),
        create_dark_knight(0, 0),
        create_dragon(0, 0),
    ]
    for e in enemies:
        assert e.fighter is not None
        assert e.fighter.is_alive
        assert e.ai is not None
