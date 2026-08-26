"""Enemy factories. Every creature that wants to kill the player lives here."""
from __future__ import annotations

from roguelike.entities.ai import BasicMonster, CowardlyAI, SlowAI, MimicAI
from roguelike.entities.entity import Entity
from roguelike.entities.fighter import Fighter
from roguelike.entities.item import (
    Potion,
    Scroll,
    create_dagger,
    create_sword,
    create_axe,
)


# --- Early depth pests (1-2) ---

def create_rat(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="r", color=(139, 69, 19), name="Rat",
        blocks_movement=True,
        fighter=Fighter(hp=5, defense=0, power=2),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.10)]
    return e


def create_bat(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="b", color=(120, 120, 120), name="Giant Bat",
        blocks_movement=True,
        fighter=Fighter(hp=3, defense=0, power=1),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.05)]
    return e


def create_kobold(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="k", color=(180, 140, 60), name="Kobold",
        blocks_movement=True,
        fighter=Fighter(hp=6, defense=0, power=2),
        ai=CowardlyAI(),
    )
    e.loot_table = [(Scroll, 0.10)]
    return e


def create_giant_ant(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="a", color=(150, 50, 50), name="Giant Ant",
        blocks_movement=True,
        fighter=Fighter(hp=8, defense=1, power=2),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.05)]
    return e


def create_slime(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="s", color=(50, 200, 100), name="Slime",
        blocks_movement=True,
        fighter=Fighter(hp=12, defense=0, power=1),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.10)]
    return e


def create_cat(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="c", color=(255, 200, 50), name="Feral Cat",
        blocks_movement=True,
        fighter=Fighter(hp=5, defense=2, power=2),
        ai=BasicMonster(),
    )
    e.loot_table = []
    return e


# --- Mid-depth threats (3-5) ---

def create_wolf(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="W", color=(180, 180, 180), name="Wolf",
        blocks_movement=True,
        fighter=Fighter(hp=10, defense=1, power=3),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.15)]
    return e


def create_skeleton(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="S", color=(220, 220, 200), name="Skeleton",
        blocks_movement=True,
        fighter=Fighter(hp=16, defense=2, power=5),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_dagger, 0.20)]
    return e


def create_orc(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="o", color=(60, 120, 60), name="Orc",
        blocks_movement=True,
        fighter=Fighter(hp=14, defense=2, power=4),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_dagger, 0.15), (Potion, 0.15)]
    return e


def create_hobgoblin(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="H", color=(160, 100, 40), name="Hobgoblin",
        blocks_movement=True,
        fighter=Fighter(hp=18, defense=3, power=5),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_sword, 0.10), (Potion, 0.20)]
    return e


def create_zombie(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="Z", color=(100, 140, 100), name="Zombie",
        blocks_movement=True,
        fighter=Fighter(hp=20, defense=0, power=3),
        ai=SlowAI(speed=2),
    )
    e.loot_table = [(Potion, 0.10)]
    return e


def create_imp(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="i", color=(255, 80, 80), name="Imp",
        blocks_movement=True,
        fighter=Fighter(hp=6, defense=0, power=3),
        ai=BasicMonster(),
    )
    e.loot_table = [(Scroll, 0.15)]
    return e


def create_giant_spider(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="S", color=(80, 80, 80), name="Giant Spider",
        blocks_movement=True,
        fighter=Fighter(
            hp=10, defense=1, power=3,
            on_hit_status=[("poison", 0.30, 3)],
        ),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 0.20)]
    return e


# --- Deep horrors (6-8) ---

def create_ogre(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="O", color=(160, 80, 40), name="Ogre",
        blocks_movement=True,
        fighter=Fighter(hp=35, defense=2, power=8),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_axe, 0.15), (Potion, 0.25)]
    return e


def create_wraith(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="W", color=(120, 120, 200), name="Wraith",
        blocks_movement=True,
        fighter=Fighter(hp=14, defense=4, power=5),
        ai=BasicMonster(),
    )
    e.loot_table = [(Scroll, 0.20), (Potion, 0.10)]
    return e


def create_troll(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="T", color=(80, 160, 80), name="Troll",
        blocks_movement=True,
        fighter=Fighter(hp=40, defense=3, power=6),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_axe, 0.10), (Potion, 0.20)]
    return e


def create_mimic(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="!", color=(255, 100, 100), name="Potion of Healing",
        blocks_movement=False,
        fighter=Fighter(hp=25, defense=4, power=5),
        ai=MimicAI(),
    )
    e.disguised = True
    e.real_name = "Mimic"
    e.disguised_name = "Potion of Healing"
    e.disguised_char = "!"
    e.disguised_color = (255, 100, 100)
    e.loot_table = [(create_sword, 0.30), (Potion, 0.30), (Scroll, 0.20)]
    return e


def create_chimera(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="C", color=(200, 100, 200), name="Chimera",
        blocks_movement=True,
        fighter=Fighter(hp=30, defense=2, power=7),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_sword, 0.20), (Potion, 0.25)]
    return e


# --- Very deep (9+) ---

def create_dark_knight(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="K", color=(80, 80, 100), name="Dark Knight",
        blocks_movement=True,
        fighter=Fighter(hp=28, defense=5, power=6),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_sword, 0.40), (Potion, 0.25)]
    return e


def create_dragon(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="D", color=(200, 50, 50), name="Dragon",
        blocks_movement=True,
        fighter=Fighter(hp=60, defense=4, power=10),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_axe, 0.50), (Potion, 0.30), (Scroll, 0.20)]
    return e


# --- Special / rare ---

def create_rat_king(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="R", color=(180, 60, 60), name="Rat King",
        blocks_movement=True,
        fighter=Fighter(hp=25, defense=2, power=4),
        ai=BasicMonster(),
    )
    e.loot_table = [(Potion, 1.00), (Scroll, 0.50)]
    return e


def create_goblin_shaman(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="g", color=(200, 100, 255), name="Goblin Shaman",
        blocks_movement=True,
        fighter=Fighter(hp=10, defense=1, power=2),
        ai=BasicMonster(),
    )
    e.loot_table = [(Scroll, 0.30), (Potion, 0.20)]
    return e


def create_rust_monster(x: int, y: int) -> Entity:
    e = Entity(
        x=x, y=y, char="x", color=(160, 120, 40), name="Rust Monster",
        blocks_movement=True,
        fighter=Fighter(hp=16, defense=3, power=2),
        ai=BasicMonster(),
    )
    e.loot_table = [(create_dagger, 0.10)]
    return e


# --- Existing: equipped goblin ---

def create_goblin(x: int, y: int, weapon: str | None = None) -> Entity:
    """Create a goblin. Optionally armed with a weapon that boosts power and drops on death."""
    power = 2
    loot = []

    if weapon == "dagger":
        power += 1
        loot.append(create_dagger())
    elif weapon == "sword":
        power += 2
        loot.append(create_sword())
    elif weapon == "axe":
        power += 3
        loot.append(create_axe())

    goblin = Entity(
        x=x, y=y, char="g", color=(80, 180, 80), name="Goblin",
        blocks_movement=True,
        fighter=Fighter(hp=7, defense=1, power=power),
        ai=BasicMonster(),
    )

    if loot:
        goblin.loot = loot

    return goblin
