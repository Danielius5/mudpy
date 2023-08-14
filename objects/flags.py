from enum import auto, IntFlag


class GameFlags(IntFlag):
    @classmethod
    def get_flags(cls, value):
        return [flag for flag in cls if flag & value]

    def __str__(self):
        return self.name.replace("_", " ").title()


class Effect(GameFlags):
    NO_EFFECT = auto()
    RESTORE_HEALTH = auto()
    RESTORE_HUNGER = auto()
    RESTORE_THIRST = auto()
    RESTORE_STAMINA = auto()


class ItemSlot(GameFlags):
    NO_SLOT = auto()
    WALLET = auto()
    HEAD = auto()
    NECK = auto()
    SHOULDERS = auto()
    CHEST = auto()
    BACK = auto()
    WRISTS = auto()
    HANDS = auto()
    FINGERS = auto()
    WAIST = auto()
    LEGS = auto()
    FEET = auto()
    MAIN_HAND = auto()
    OFF_HAND = auto()
    TWO_HAND = auto()
    RANGED = auto()
    AMMO = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    JUNK = auto()


class DamageType(GameFlags):
    NO_DAMAGE_TYPE = auto()
    BALLISTIC = auto()
    BLUNT = auto()
    PIERCING = auto()
    SLASHING = auto()
    FIRE = auto()
    COLD = auto()
    ELECTRIC = auto()
    POISON = auto()
    RADIATION = auto()
    SONIC = auto()


class AmmoType(GameFlags):
    NO_AMMO_TYPE = auto()
    BULLET = auto()


class Targets(GameFlags):
    NO_TARGET = auto()
    SELF = auto()
    OTHER = auto()
    ALL = auto()
    IN_RANGE = auto()


class WeaponModSlot(GameFlags):
    NO_SLOT = auto()
    BARREL = auto()
    STOCK = auto()
    GRIP = auto()
    SIGHT = auto()
    MAGAZINE = auto()
    MUZZLE = auto()
    UNDERBARREL = auto()
    BLADE = auto()


class ObjectAction(GameFlags):
    NO_ACTION = auto()
    PICK_UP = auto()
    DROP = auto()
    USE = auto()
    EQUIP = auto()
    UNEQUIP = auto()
    STACK = auto()
    UNSTACK = auto()
    INSPECT = auto()
    ATTACK = auto()
    DEFEND = auto()
    MOVE = auto()
    SELL = auto()
    BUY = auto()
    TRADE = auto()


class InspectionDetails(GameFlags):
    NO_INSPECT = auto()
    SHORT_INSPECT = auto()
    LONG_INSPECT = auto()
    DETAILED_INSPECT = auto()
    ACTION_INSPECT = auto()
