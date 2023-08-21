import gc
import inspect
from typing import Callable, Self

from game.mechanics.flags import ObjectInspection, ObjectInteraction
from game.objects.base import BaseObject
from game.system import database
from game.system.utils import go_dataclass as ddc, hidden_field as hf, private_hidden_field as phf

Description = str | Callable[[Self], str] | Callable[[], str]


@ddc
class BasicObject(BaseObject):
    allowed_interactions: ObjectInteraction = phf(default = ObjectInteraction.INTERACT | ObjectInteraction.INSPECT,
                                                  metadata = {"to_type": ObjectInteraction})

    short_description: Description = hf(default = "Nothing much to see here")
    long_description: Description = hf(
            default = "Honestly, no matter how long you look, you won't find anything interesting"
    )
    detailed_description: Description = hf(
            default = "You look, and look and look, but you can't find anything interesting"
    )
    action_description: Description = hf(default = "Do you know what you can do with nothing? Nothing!")
    self_description: Description = hf(default = "Whats the best thing to describe nothing? Nothing!")
    db_category: str = phf(default = None)

    def inspect(self, lod: ObjectInspection | str = ObjectInspection.SHORT_DESCRIPTION) -> str:
        lod = ObjectInspection[lod.upper()] if isinstance(lod, str) else lod
        match lod:
            case _ if hasattr(self, lod.name.lower()):
                method = getattr(self, lod.name.lower(), lambda self: "Nothing to see here")
                if callable(method):
                    if "self" in inspect.signature(method).parameters:
                        return method(self)
                    return method()
                return method
            case ObjectInspection.NO_INSPECT | _:
                return "Nothing to see here"

    def interact(self, action: ObjectInteraction | str, *args, **kwargs) -> str:
        action = ObjectInteraction[action.upper()] if isinstance(action, str) else action
        if action & self.allowed_interactions:
            match action:
                case _ if hasattr(self, action.name.lower()):
                    method = getattr(self, action.name.lower(), lambda *args, **kwargs: "Nothing to do here")
                    return method(*args, **kwargs)
                case ObjectInteraction.NO_ACTION | _:
                    return "Nothing to do here"
        else:
            return "You can't do that!"

    def save(self):
        if self.db_category is None:
            raise ValueError("Cannot save an object without a database category")
        database.insert_game_object(self, cat = self.db_category)

    def update(self):
        if self.db_category is None:
            raise ValueError("Cannot update an object without a database category")
        database.update_game_object(self, cat = self.db_category)

    def delete(self):
        if self.db_category is None:
            raise ValueError("Cannot delete an object without a database category")
        database.delete_game_object(self, cat = self.db_category)

    @classmethod
    def from_db(cls, **kwargs):
        return database.retrieve_game_object(cls, **kwargs)

    # noinspection PyArgumentList
    @classmethod
    def from_db_all(cls, **kwargs):
        return database.retrieve_game_objects(cls, **kwargs)

    def is_garbage(self):
        """Override this method to determine if the object is garbage and should be collected. 
        You should include your own logic to determine if this particular
        instance is read for collection, such as being created at a certain time etc."""
        return False

    @classmethod
    def collect_garbage(cls):
        """Collects all garbage objects"""
        for obj in filter(lambda x: x.is_garbage(), cls.instances()):
            obj.delete()
            del obj

    @classmethod
    def instances(cls):
        # gets all instances of this class in the garbage collector
        return list(filter(lambda x: isinstance(x, cls), gc.get_objects()))


__all__ = [
        "Interactable",
]
