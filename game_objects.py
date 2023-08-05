from descriptors import Registry, State

class GameObject:
    registry = Registry()
    id = State(0, int)
    
