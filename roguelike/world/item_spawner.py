"""Item spawner for the game, responsible for generating random items in rooms based on dungeon depth and other factors.
"""
from __future__ import annotations

import random
from typing import List

from roguelike.entities.item import Item, Potion, Scroll, Weapon
from roguelike.world.game_map import GameMap


def spawn_items(game_map: GameMap, depth: int = 1) -> List[Item]:
    """Spawn random items in rooms based on dungeon depth."""
    items = []
    
    # Skip the first room (player starts there)
    rooms = game_map.rooms[1:] if len(game_map.rooms) > 1 else []
    
    # Number of items scales with depth
    num_items = min(len(rooms), 2 + depth // 2)
    
    for room in random.sample(rooms, min(num_items, len(rooms))):
        x, y, w, h = room
        
        # Random position within room (away from walls)
        item_x = x + random.randint(1, w - 2)
        item_y = y + random.randint(1, h - 2)
        
        # Random item type (weights can be adjusted)
        item_type = random.choice([
            "potion", "potion", "potion",  # 3x more likely
            "scroll",
            "weapon",
        ])
        
        if item_type == "potion":
            item = Potion(x=item_x, y=item_y)
        elif item_type == "scroll":
            item = Scroll(x=item_x, y=item_y, scroll_type="identify")
        else:
            item = Weapon(x=item_x, y=item_y)
        
        items.append(item)
    
    return items