from dataclasses import dataclass

from .base import default_dataclass_options, Living


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Human(Living):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Animal(Living):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class NPC(Living):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Trader(NPC):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class QuestGiver(NPC):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class QuestNPC(NPC):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class HostileNPC(NPC):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Player(Living):
    pass


__all__ = [
        "Human",
        "Animal",
        "NPC",
        "Trader",
        "QuestGiver",
        "QuestNPC",
        "HostileNPC",
        "Player",
]
