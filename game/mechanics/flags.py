from enum import auto, IntFlag

from game.system.utils import search_subs


class GameFlags(IntFlag):
    @classmethod
    def get_flags(cls, value):
        return tuple(flag for flag in cls if flag & value)

    def __str__(self):
        return self.name.replace("_", " ").title()

    def __contains__(self, item):
        return item in self.get_flags(self)

    @classmethod
    def search_game_flags(cls, name, member = None):
        sub = search_subs(cls, name)
        return sub[member] if member is not None else sub


class ObjectInteraction(GameFlags):
    NO_ACTION = auto()
    INTERACT = auto()
    INSPECT = auto()

    def __format__(self, format_spec):
        if format_spec == "s":
            return self.name.replace("_", " ").title()
        elif format_spec == "r":
            return self.name
        elif format_spec == "i":
            return str(self.value)
        else:
            return super().__format__(format_spec)


class ObjectInspection(GameFlags):
    NO_INSPECT = auto()
    SHORT_DESCRIPTION = auto()
    LONG_DESCRIPTION = auto()
    DETAILED_DESCRIPTION = auto()
    ACTION_DESCRIPTION = auto()
    SELF_DESCRIPTION = auto()


__all__ = [
        "GameFlags",
        "ObjectInteraction",
        "ObjectInspection",
]
