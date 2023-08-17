from .simple import Living
from ..system.utils import go_dataclass


# todo: Flesh out the living classes
#  - Add a way to track the living's inventory
#  - Add a way to track the living's equipment
#  - Add a way to track the living's stats
#  - Add a way to track the living's skills
#  - Add a way to track the living's spells
#  - Add a way to track the living's quests
#  - Add a way to track the living's factions
#  - Add a way to track the living's relationships
#  - Add a way to track the living's AI
#  - Add a way to track the living's combat
#  - Add a way to track the living's death
#  - Add a way to track the living's respawn
#  - Add a way to track the living's loot
#  - Add a way to track the living's trading
#  - Add a way to track the living's dialogue
#  - Add a way to track the living's quests
#  - Add a way to track the living's quest rewards
#  - Add a way to track the living's quest dialogue
#  - Add a way to track the living's quest items
#  - Add a way to track the living's quest objectives
#  - Add a way to track the living's quest rewards
#  - Add a way to track the living's quest rewards

# noinspection PyArgumentList
@go_dataclass
class Human(Living):
    pass


# noinspection PyArgumentList
@go_dataclass
class Animal(Living):
    pass


# noinspection PyArgumentList
@go_dataclass
class NPC(Living):
    pass


# noinspection PyArgumentList
@go_dataclass
class Trader(NPC):
    pass


# noinspection PyArgumentList
@go_dataclass
class QuestGiver(NPC):
    pass


# noinspection PyArgumentList
@go_dataclass
class QuestNPC(NPC):
    pass


# noinspection PyArgumentList
@go_dataclass
class HostileNPC(NPC):
    pass


# noinspection PyArgumentList
@go_dataclass
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
