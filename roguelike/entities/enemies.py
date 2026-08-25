from roguelike.entities.ai import BasicMonster
from roguelike.entities.entity import Entity
from roguelike.entities.fighter import Fighter


def create_rat(x: int, y: int) -> Entity:
    return Entity(
        x=x,
        y=y,
        char="r",
        color=(139, 69, 19),
        name="Rat",
        blocks_movement=True,
        fighter=Fighter(hp=5, defense=0, power=2),
        ai=BasicMonster(),
    )


def create_wolf(x: int, y: int) -> Entity:
    return Entity(
        x=x,
        y=y,
        char="W",
        color=(180, 180, 180),
        name="Wolf",
        blocks_movement=True,
        fighter=Fighter(hp=10, defense=1, power=3),
        ai=BasicMonster(),
    )


def create_skeleton(x: int, y: int) -> Entity:
    return Entity(
        x=x,
        y=y,
        char="S",
        color=(220, 220, 200),
        name="Skeleton",
        blocks_movement=True,
        fighter=Fighter(hp=16, defense=2, power=5),
        ai=BasicMonster(),
    )


def create_goblin(x: int, y: int) -> Entity:
    return Entity(
        x=x,
        y=y,
        char="g",
        color=(80, 180, 80),
        name="Goblin",
        blocks_movement=True,
        fighter=Fighter(hp=7, defense=1, power=2),
        ai=BasicMonster(),
    )
