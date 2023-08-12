from ..descriptors import *
from .game_object import *
import typing


class DataMapping(typing.MutableMapping):
    def __getitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        return self.data[key]

    def __setitem__(self, key, value):
        if key not in self.data:
            raise KeyError(key)
        self.data[key] = value

    def __delitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        self.data[key] = None

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}={self.data}>"

class Inventory(GameObject, DataMapping):
    data: dict = State(
            default_factory=lambda: {i: None for i in range(1, 11)}, 
            freeze=True
    )


    

class Stats(GameObject, DataMapping):
    data: dict = State(
            default_factory=lambda: {
                "current_hp": 0,
                "max_hp": 0,
                "current_stamina": 0,
                "max_stamina": 0,
                "current_thirst": 0,
                "max_thirst": 0,
                "current_hunger": 0,
                "max_hunger": 0,
                "current_rested": 0,
                "max_rested": 0,
            },
            freeze=True
    )
    
class Equipment(GameObject, DataMapping):
    data: dict = State(
            default_factory=lambda: {
                "weapon": None,
                "armor": None,
                "accessory": None,
            },
            freeze=True
    )
    

class Skills(GameObject, DataMapping):
    data: dict = State(
            default_factory=lambda: {
            },
            freeze=True
    )
    


class Player(GameObject):
    name: str = State(freeze=True, default=None, required=True)
    inventory: typing.Mapping = State(default_factory=Inventory, freeze=True)
    stats: typing.Mapping = State(default_factory=Stats, freeze=True)
    equipment: typing.Mapping = State(default_factory=Equipment, freeze=True)
    skills: typing.Mapping = State(default_factory=Skills, freeze=True)
    
    def __repr__(self):
        return f"<Player name={self.name}, uuid={self.uuid}>"
            
    
    
__all__ = ["Player"]