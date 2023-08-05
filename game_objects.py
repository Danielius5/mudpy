from descriptors.state import State
from descriptors.registry import Registry


class GameObject:
    registry = Registry()
    id = State(0, int)
    
