"""Translates raw keyboard events into Action objects.

Deliberately supports arrow keys, numpad, and vi-keys (hjkl + diagonals) from
day one, so that the player can choose their preferred movement style.
"""
from __future__ import annotations

from typing import Optional

import tcod.event
from tcod.event import KeySym

from roguelike.engine.actions import Action, EscapeAction, MovementAction

MOVE_KEYS = {
    # Arrow keys.
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    # Diagonals via numpad.
    KeySym.KP_1: (-1, 1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_3: (1, 1),
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_8: (0, -1),
    KeySym.KP_9: (1, -1),
    # Vi keys. (tcod's KeySym enum names letter keys with uppercase
    # attribute names -- these still refer to the plain, unshifted letter.)
    KeySym.H: (-1, 0),
    KeySym.J: (0, 1),
    KeySym.K: (0, -1),
    KeySym.L: (1, 0),
    KeySym.Y: (-1, -1),
    KeySym.U: (1, -1),
    KeySym.B: (-1, 1),
    KeySym.N: (1, 1),
}


def handle_event(event: tcod.event.Event) -> Optional[Action]:
    """Convert a single tcod event into an Action, or None if it maps to nothing."""
    match event:
        case tcod.event.Quit():
            return EscapeAction()

        case tcod.event.KeyDown(sym=sym):
            if sym in MOVE_KEYS:
                dx, dy = MOVE_KEYS[sym]
                return MovementAction(dx, dy)
            if sym == KeySym.ESCAPE:
                return EscapeAction()

    return None
