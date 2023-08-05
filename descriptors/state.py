class State:
    def __init__(self, *constraints, default = None, default_factory = None, _type = None):
        self.constraints = constraints
        self.default = default
        self.default_factory = default_factory
        self.type = _type or type(default) if default is not None else None
        

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default_factory() if self.default_factory else self.default)

    def __set__(self, instance, value):
        if self.type is not None:
            if not isinstance(value, self.type):
                raise TypeError(f"Expected {self.type}, got {type(value)}")
        if not all(constraint(value) for constraint in self.constraints):
            raise ValueError(f"Value {value} does not meet all constraints")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]

class IntState(State):
    def __init__(self, min, max, *args, **kwargs):
        super().__init__(lambda x: min <= x <= max, *args, _type = int, **kwargs)
        
        
class FloatState(State):
    def __init__(self, min, max, *args, **kwargs):
        super().__init__(lambda x: min <= x <= max, *args, _type = float, **kwargs)
        
        
class StringState(State):
    def __init__(self, min_length, max_length, *args, **kwargs):
        super().__init__(lambda x: min_length <= len(x) <= max_length, *args, _type = str, **kwargs)
        

class BoolState(State):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, _type = bool, **kwargs)