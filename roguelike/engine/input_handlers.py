"""Translates raw keyboard events into Action objects."""
from __future__ import annotations

from typing import Optional

import tcod.event
from tcod.event import KeySym

from roguelike.engine.actions import (
    Action,
    AscendAction,
    CancelMenuAction,
    DescendAction,
    EscapeAction,
    InventoryDropAction,
    InventoryEquipAction,
    InventoryUseAction,
    MovementAction,
    PickupAction,
    SelectItemAction,
    WaitAction,
)

MOVE_KEYS = {
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.KP_1: (-1, 1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_3: (1, 1),
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_8: (0, -1),
    KeySym.KP_9: (1, -1),
    KeySym.H: (-1, 0),
    KeySym.J: (0, 1),
    KeySym.K: (0, -1),
    KeySym.L: (1, 0),
    KeySym.Y: (-1, -1),
    KeySym.U: (1, -1),
    KeySym.B: (-1, 1),
    KeySym.N: (1, 1),
}

INVENTORY_KEYS = {
    KeySym.A: 0, KeySym.B: 1, KeySym.C: 2, KeySym.D: 3, KeySym.E: 4,
    KeySym.F: 5, KeySym.G: 6, KeySym.H: 7, KeySym.I: 8, KeySym.J: 9,
    KeySym.K: 10, KeySym.L: 11, KeySym.M: 12, KeySym.N: 13, KeySym.O: 14,
    KeySym.P: 15, KeySym.Q: 16, KeySym.R: 17, KeySym.S: 18, KeySym.T: 19,
    KeySym.U: 20, KeySym.V: 21, KeySym.W: 22, KeySym.X: 23, KeySym.Y: 24,
    KeySym.Z: 25,
}


def handle_event(event: tcod.event.Event, game_state: str = "playing") -> Optional[Action]:
    if game_state == "playing":
        return _handle_playing(event)
    elif game_state.startswith("inventory"):
        return _handle_inventory(event, game_state)
    return None


def _handle_playing(event: tcod.event.Event) -> Optional[Action]:
    match event:
        case tcod.event.Quit():
            return EscapeAction()

        case tcod.event.KeyDown(sym=sym, mod=mod):
            if sym in MOVE_KEYS:
                return MovementAction(*MOVE_KEYS[sym])
            if sym == KeySym.ESCAPE:
                return EscapeAction()
            if sym == KeySym.G:
                return PickupAction()
            if sym == KeySym.I:
                return InventoryUseAction()
            if sym == KeySym.D:
                return InventoryDropAction()
            if sym == KeySym.E:
                return InventoryEquipAction()
            if sym == KeySym.KP_5:
                return WaitAction()
            if sym == KeySym.PERIOD and mod & tcod.event.KMOD_SHIFT:
                return DescendAction()
            if sym == KeySym.COMMA and mod & tcod.event.KMOD_SHIFT:
                return AscendAction()

    return None


def _handle_inventory(event: tcod.event.Event, game_state: str) -> Optional[Action]:
    match event:
        case tcod.event.KeyDown(sym=sym):
            if sym == KeySym.ESCAPE:
                return CancelMenuAction()
            if sym in INVENTORY_KEYS:
                mode = game_state.replace("inventory_", "")
                return SelectItemAction(INVENTORY_KEYS[sym], mode)

    return None
