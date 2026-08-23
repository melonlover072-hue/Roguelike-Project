"""Actions decouple 'what key was pressed' from 'what happens in the game'.

The input handler only ever produces an Action; it never touches game state
directly. This is what lets Phase 2 add a BumpAction that turns into either
MovementAction or a MeleeAction depending on what's in the destination tile,
without the input-handling code needing to know anything about combat.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine


class Action:
    def perform(self, engine: "Engine") -> None:
        """Perform this action against the given engine's state.

        Must be overridden by subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: "Engine") -> None:
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def perform(self, engine: "Engine") -> None:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy

        if not engine.game_map.is_walkable(dest_x, dest_y):
            return  # Blocked by a wall or map edge -- do nothing (Phase 0 has no bump messages yet).

        engine.player.move(self.dx, self.dy)
