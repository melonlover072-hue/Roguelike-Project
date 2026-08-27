# ADOM-Inspired Roguelike

A turn-based, full-ASCII roguelike, taking design inspiration from *ADOM*.

## Status: Phase 0 — Skeleton

- [x] Window + render loop via `python-tcod`
- [x] Map viewport / sidebar / message-log regions
- [x] Player entity rendered and movable (arrow keys, numpad, or vi-keys `hjklyubn`)
- [x] Wall + map-edge collision against a hardcoded test room
- [x] Test suite covering map bounds, walkability, and movement/collision logic

## Status: Phase 1 — Dungeon Generation and FOV

- [x] BSP dungeon generator (rooms + corridors)
- [x] Recursive shadowcasting FOV
- [x] Explored tile memory (dimmed when out of sight)
- [x] Items and item spawning (potions, scrolls, equipment)
- [x] Player spawns on a valid floor tile

## Status: Phase 2 — AI, Combat, and Inventory

- [x] Bump-to-attack melee combat
- [x] Basic enemy AI (chase within 8 tiles, attack if adjacent)
- [x] `Fighter` component with HP, defense, and power
- [x] Enemy death (corpse conversion, loot drops)
- [x] Inventory system (`g` pick up, `i` use, `d` drop, `e` equip/unequip)
- [x] Equipment that modifies stats (dagger +1, sword +2, axe +3)
- [x] Consumables (healing potions)
- [x] Sidebar shows HP, inventory count, equipped weapon

## Status: Phase 3 — Depths and Stairs

- [x] Multi-floor dungeon with persistent level cache
- [x] Down stairs (`>`) and up stairs (`<`)
- [x] `Shift+.` to descend, `Shift+,` to ascend
- [x] ADOM-style return stairs — previous floors are restored exactly as left
- [x] Depth counter in sidebar
- [x] Depth 1 blocks surface escape
- [x] Enemy/item spawn scaling per depth
- [x] Goblins spawn with equipment (dagger/sword/axe) that drops on death

## Status: Phase 4 — Enemy Expansion

- [x] 19 new enemies across all depths
- [x] Depth-appropriate spawn tables (rats on 1, dragons on 9+)
- [x] General loot tables — every enemy can drop items on death
- [x] Status effect framework (poison)
- [x] Giant Spider applies poison on hit (30% chance)
- [x] Cowardly AI — Kobold flees when hurt
- [x] Slow AI — Zombie acts every other turn
- [x] Mimic AI — disguised as a potion until bumped or approached
- [x] Rare spawns (Rat King, Goblin Shaman, Rust Monster)

## Controls

| Key | Action |
|-----|--------|
| Arrow / Numpad / `hjklyubn` | Move / Bump attack |
| `Numpad 5` | Wait one turn |
| `g` | Pick up item |
| `i` | Use item (inventory menu) |
| `d` | Drop item (inventory menu) |
| `e` | Equip / unequip item (inventory menu) |
| `Shift + .` (`>`) | Descend stairs |
| `Shift + ,` (`<`) | Ascend stairs |
| `a-z` | Select item from menu |
| `ESC` | Cancel / close menu |

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Testing

```bash
pytest tests/ -v
```

## Notes to Self

- Ranged enemies (later)
- Faction hostility (later)
- Overworld (MUCH later)
- Shops and quests (later)
- Proper special levels that can spawn. (VERY MUCH LATER)
