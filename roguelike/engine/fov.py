from __future__ import annotations

import numpy as np
from roguelike.world.game_map import GameMap


def compute_fov(game_map: GameMap, x: int, y: int, radius: int) -> None:
    """Calculate FOV using recursive shadowcasting."""
    
    # Reset visibility
    game_map.tiles["visible"] = False
    
    # Player's tile is always visible
    game_map.tiles[x, y]["visible"] = True
    game_map.tiles[x, y]["explored"] = True
    
    # Cast rays in all 8 octants
    for octant in range(8):
        cast_light(game_map, x, y, radius, 1, 1.0, 0.0, 
                   _get_octant_transform(octant))


def cast_light(game_map: GameMap, x: int, y: int, radius: int, 
               row: int, start_slope: float, end_slope: float, 
               transform: tuple) -> None:
    """Recursive light casting for one octant."""
    if start_slope < end_slope:
        return
    
    next_start_slope = start_slope
    
    for current_row in range(row, radius + 1):
        blocked = False
        
        for dx in range(-current_row, 1):
            dy = -current_row
            left_slope = (dx - 0.5) / (dy + 0.5)
            right_slope = (dx + 0.5) / (dy - 0.5)
            
            if start_slope < right_slope:
                continue
            elif end_slope > left_slope:
                continue
            
            # Transform to actual map coordinates
            map_x = x + dx * transform[0] + dy * transform[2]
            map_y = y + dx * transform[1] + dy * transform[3]
            
            # Check bounds
            if not game_map.in_bounds(map_x, map_y):
                continue
            
            # Check if within radius
            if dx * dx + dy * dy > radius * radius:
                continue
            
            # Mark as visible and explored
            game_map.tiles[map_x, map_y]["visible"] = True
            game_map.tiles[map_x, map_y]["explored"] = True
            
            if blocked:
                if not game_map.tiles[map_x, map_y]["transparent"]:
                    next_start_slope = left_slope
                    continue
                else:
                    blocked = False
                    start_slope = next_start_slope
            elif not game_map.tiles[map_x, map_y]["transparent"]:
                blocked = True
                next_start_slope = left_slope
        
        if blocked:
            break


def _get_octant_transform(octant: int) -> tuple:
    """Return transformation for each octant."""
    transforms = [
        (1, 0, 0, 1),    # 0: NNE
        (0, 1, 1, 0),    # 1: ENE
        (0, -1, 1, 0),   # 2: ESE
        (-1, 0, 0, 1),   # 3: SSE
        (-1, 0, 0, -1),  # 4: SSW
        (0, -1, -1, 0),  # 5: WSW
        (0, 1, -1, 0),   # 6: WNW
        (1, 0, 0, -1),   # 7: NNW
    ]
    return transforms[octant]