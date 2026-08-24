"""Item classes for the game project, including base item definitions and classes.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine.engine import Engine
    from roguelike.entities.entity import Entity


class Item:
    
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        char: str = "!",
        color: tuple = (255, 255, 255),
        name: str = "Unknown Item",
        weight: float = 0.0,
        description: str = "A mysterious item.",
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.weight = weight  # In "stones" for that ADOM feel
        self.description = description
        
        # ADOM-style identification
        self.identified = False
        self.cursed = False
        self.blessed = False
    
    @property
    def display_name(self) -> str:
        """Return the name with identification status if known."""
        if not self.identified:
            return self.name
        
        status = []
        if self.blessed:
            status.append("blessed")
        elif self.cursed:
            status.append("cursed")
        
        if status:
            return f"{status[0]} {self.name}"
        return self.name
    
    def pick_up(self, engine: "Engine") -> bool:
        """Attempt to pick up this item."""
        if len(engine.inventory) >= engine.max_inventory_size:
            engine.add_message("Your backpack is full!")
            return False
        
        engine.inventory.append(self)
        engine.add_message(f"You pick up the {self.display_name}.")
        return True
    
    def drop(self, engine: "Engine") -> bool:
        """Drop this item at the player's feet."""
        self.x = engine.player.x
        self.y = engine.player.y
        engine.inventory.remove(self)
        engine.items_on_ground.append(self)
        engine.add_message(f"You drop the {self.display_name}.")
        return True
    
    def use(self, engine: "Engine") -> bool:
        """Use this item. Override in subclasses for specific effects."""
        engine.add_message(f"The {self.display_name} does nothing.")
        return False


class Consumable(Item):
    """Items that are used up when used (potions, scrolls, food)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uses = 1  # Most consumables are single-use
    
    def use(self, engine: "Engine") -> bool:
        """Use the consumable and apply its effect."""
        if self.uses <= 0:
            return False
        
        # Apply effect (override in subclasses)
        self.apply_effect(engine)
        
        # Consume
        self.uses -= 1
        if self.uses <= 0:
            engine.inventory.remove(self)
        
        return True
    
    def apply_effect(self, engine: "Engine") -> None:
        """Apply this consumable's effect. Override in subclasses."""
        pass


class Equipment(Item):
    """Items that can be worn/wielded (weapons, armor, rings)."""
    
    # Equipment slots
    SLOT_WEAPON = "weapon"
    SLOT_SHIELD = "shield"
    SLOT_HEAD = "head"
    SLOT_BODY = "body"
    SLOT_CLOAK = "cloak"
    SLOT_GLOVES = "gloves"
    SLOT_BOOTS = "boots"
    SLOT_NECK = "neck"
    SLOT_RING_LEFT = "ring_left"
    SLOT_RING_RIGHT = "ring_right"
    
    def __init__(self, slot: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot = slot
        self.equipped = False
        
        # Combat stats (add more as needed)
        self.attack_bonus = 0
        self.defense_bonus = 0
        self.damage_dice = None  # e.g., (2, 6) for 2d6
    
    def equip(self, engine: "Engine") -> bool:
        """Equip this item to its slot."""
        # Unequip existing item in this slot
        if self.slot in engine.equipment:
            old_item = engine.equipment[self.slot]
            old_item.unequip(engine)
        
        # Equip this item
        self.equipped = True
        engine.equipment[self.slot] = self
        engine.add_message(f"You equip the {self.display_name}.")
        return True
    
    def unequip(self, engine: "Engine") -> bool:
        """Unequip this item."""
        if not self.equipped:
            return False
        
        self.equipped = False
        if self.slot in engine.equipment:
            del engine.equipment[self.slot]
        engine.add_message(f"You unequip the {self.display_name}.")
        return True


class Potion(Consumable):
    """A healing potion."""
    
    def __init__(self, x: int = 0, y: int = 0, healing_amount: int = 10):
        super().__init__(
            x=x,
            y=y,
            char="!",
            color=(255, 100, 100),
            name="Potion of Healing",
            weight=0.5,
            description="A bubbling red liquid that smells faintly of herbs.",
        )
        self.healing_amount = healing_amount
    
    def apply_effect(self, engine: "Engine") -> None:
        """Heal the player."""
        fighter = engine.player.fighter
        if fighter is None:
            engine.add_message("Nothing happens.")
            return

        healed = fighter.heal(self.healing_amount)
        if healed > 0:
            engine.add_message(f"You feel better! (+{healed} HP)")
        else:
            engine.add_message("You are already at full health.")


class Scroll(Consumable):
    """A scroll with a magical effect."""
    
    def __init__(self, x: int = 0, y: int = 0, scroll_type: str = "unknown"):
        super().__init__(
            x=x,
            y=y,
            char="?",
            color=(200, 200, 255),
            name=f"Scroll of {scroll_type}",
            weight=0.1,
            description="A rolled parchment covered in arcane symbols.",
        )
        self.scroll_type = scroll_type
    
    def apply_effect(self, engine: "Engine") -> None:
        """Apply scroll effect based on type."""
        if self.scroll_type == "identify":
            engine.add_message("This scroll would identify an item.")
        elif self.scroll_type == "teleport":
            engine.add_message("This scroll would teleport you somewhere.")
        else:
            engine.add_message(f"The scroll crumbles to dust.")


class Weapon(Equipment):
    """A basic weapon."""
    
    def __init__(self, x: int = 0, y: int = 0, name: str = "Dagger"):
        super().__init__(
            slot=Equipment.SLOT_WEAPON,
            x=x,
            y=y,
            char=")",
            color=(180, 180, 180),
            name=name,
            weight=1.0,
            description=f"A simple {name.lower()}.",
        )
        self.attack_bonus = 1
        self.damage_dice = (1, 4)  # 1d4 damage