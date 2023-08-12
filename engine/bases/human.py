import json

from .game_object import *
from ..descriptors import *
from ..mixins.mappings import DataMapping


class Inventory(GameObject, DataMapping):
    data: dict = State(
            default_factory = lambda: {i: None for i in range(1, 11)},
            freeze = True
    )


class Stats(GameObject, DataMapping):
    data: dict = State(
            default_factory = lambda: {
                    "current_hp"     : 0,
                    "max_hp"         : 0,
                    "current_stamina": 0,
                    "max_stamina"    : 0,
                    "current_thirst" : 0,
                    "max_thirst"     : 0,
                    "current_hunger" : 0,
                    "max_hunger"     : 0,
                    "current_rested" : 0,
                    "max_rested"     : 0,
                    "current_energy" : 0,
                    "max_energy"     : 0,
                    "current_charge" : 0,
                    "max_charge"     : 0,
            },
            freeze = True
    )


class Equipment(GameObject, DataMapping):
    data: dict = State(
            default_factory = lambda: {
                    "head"                : None,
                    "eyes"                : None,
                    "ears"                : None,
                    "face"                : None,
                    "neck"                : None,
                    "shoulders"           : None,
                    "arms"                : None,
                    "hands"               : None,
                    "chest"               : None,
                    "back"                : None,
                    "waist"               : None,
                    "legs"                : None,
                    "feet"                : None,
                    "left_hand"           : None,
                    "right_hand"          : None,
                    "left_ring"           : None,
                    "right_ring"          : None,
                    "left_wrist"          : None,
                    "right_wrist"         : None,
                    "left_ankle"          : None,
                    "right_ankle"         : None,
                    "left_finger"         : None,
                    "right_finger"        : None,
                    "left_ear"            : None,
                    "right_ear"           : None,
                    "left_eye"            : None,
                    "right_eye"           : None,
                    "left_arm"            : None,
                    "right_arm"           : None,
                    "left_leg"            : None,
                    "right_leg"           : None,
                    "left_foot"           : None,
                    "right_foot"          : None,
                    # implants
                    "head_implant"        : None,
                    "eyes_implant"        : None,
                    "ears_implant"        : None,
                    "face_implant"        : None,
                    "neck_implant"        : None,
                    "shoulders_implant"   : None,
                    "chest_implant"       : None,
                    "back_implant"        : None,
                    "waist_implant"       : None,
                    "left_hand_implant"   : None,
                    "right_hand_implant"  : None,
                    "left_ring_implant"   : None,
                    "right_ring_implant"  : None,
                    "left_wrist_implant"  : None,
                    "right_wrist_implant" : None,
                    "left_ankle_implant"  : None,
                    "right_ankle_implant" : None,
                    "left_finger_implant" : None,
                    "right_finger_implant": None,
                    "left_ear_implant"    : None,
                    "right_ear_implant"   : None,
                    "left_eye_implant"    : None,
                    "right_eye_implant"   : None,
                    "left_arm_implant"    : None,
                    "right_arm_implant"   : None,
                    "left_leg_implant"    : None,
                    "right_leg_implant"   : None,
                    "left_foot_implant"   : None,
                    "right_foot_implant"  : None,
            },
            freeze = True
    )


class Skills(GameObject, DataMapping):
    data: dict = State(
            default_factory = lambda: {
                    # todo: add skills
            },
            freeze = True
    )


class Human(GameObject):
    name: str = State(default = None, required = True)
    short_description: str = State(default = None, required = True)
    long_description: str = State(default = None, required = True)
    detailed_description: str = State(default = None, required = True)

    inventory: Inventory = State(default_factory = Inventory, freeze = True)
    stats: Stats = State(default_factory = Stats, freeze = True)
    equipment: Equipment = State(default_factory = Equipment, freeze = True)
    skills: Skills = State(default_factory = Skills, freeze = True)

    def to_dict(self):
        return {
                "name"                : self.name,
                "short_description"   : self.short_description,
                "long_description"    : self.long_description,
                "detailed_description": self.detailed_description,
                "inventory"           : self.inventory.data,
                "stats"               : self.stats.data,
                "equipment"           : self.equipment.data,
                "skills"              : self.skills.data,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
                name = data['name'],
                short_description = data['short_description'],
                long_description = data["long_description"],
                detailed_description = data["detailed_description"],
                inventory = Inventory(data["inventory"]),
                stats = Stats(data["stats"]),
                equipment = Equipment(data["equipment"]),
                skills = Skills(data["skills"])
        )
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data_string):
        return cls.from_dict(json.loads(data_string))

    def __repr__(self):
        return f"<Human name={self.name}, uuid={self.uuid}>"


class Player(Human):
    owner_id: int = State(required = True)
    op_level: int = State(default = 0)
    op_enabled: bool = State(default = False)
    
    def to_dict(self):
        super_dict = super().to_dict()
        super_dict.update({
                "owner_id"  : self.owner_id,
                "op_level"  : self.op_level,
                "op_enabled": self.op_enabled,
        })
        return super_dict
    
    @classmethod
    def from_dict(cls, data):
        return cls(
                name = data['name'],
                short_description = data['short_description'],
                long_description = data["long_description"],
                detailed_description = data["detailed_description"],
                inventory = Inventory(data["inventory"]),
                stats = Stats(data["stats"]),
                equipment = Equipment(data["equipment"]),
                skills = Skills(data["skills"]),
                owner_id = data["owner_id"],
                op_level = data["op_level"],
                op_enabled = data["op_enabled"],
        )


__all__ = ["Human", "Player"]
