
def search_subs(subs, name):
    for sub in subs:
        if sub.__name__ == name:
            return sub
        result = search_subs(sub.__subclasses__(), name)
        if result is not None:
            return result
    return None


class Meta(type):
    def __getitem__(self, item):
        if item is None:
            return State
        if isinstance(item, type):
            item = item.__name__
        name = f"{item.lower().title()}State"
        sub = search_subs(self.__subclasses__(), name)
        if sub is None:
            raise KeyError(f"Unsupported type {item}")
        return sub


class BaseState(metaclass = Meta):
    def __init__(self, *constraints, default = None, default_factory = None, _type = None):
        self.constraints = constraints
        self.default = default
        self.default_factory = default_factory
        self.type = _type or type(default) if default is not None else None

    def __set_name__(self, owner, name):
        self.name = name
        return self

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


# noinspection PyArgumentList
class NumberState(BaseState):
    def __init__(self, minimum = None, maximum = None, *args, **kwargs):
        constraint = None
        match minimum, maximum:
            case None, None:
                constraint = lambda x: True
            case None, int():
                constraint = lambda x: x <= maximum
            case int(), None:
                constraint = lambda x: minimum <= x
            case int(), int():
                constraint = lambda x: minimum <= x <= maximum
        super().__init__(constraint, *args, **kwargs)


# noinspection PyArgumentList
class IntState(NumberState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, _type = int, **kwargs)


# noinspection PyArgumentList
class FloatState(NumberState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, _type = float, **kwargs)


# noinspection PyArgumentList
class StrState(BaseState):
    def __init__(self, min_length = None, max_length = None, *args, **kwargs):
        constraint = None
        match min_length, max_length:
            case None, None:
                constraint = lambda x: True
            case None, int():
                constraint = lambda x: len(x) <= max_length
            case int(), None:
                constraint = lambda x: min_length <= len(x)
            case int(), int():
                constraint = lambda x: min_length <= len(x) <= max_length
        super().__init__(constraint, *args, **kwargs)


# noinspection PyArgumentList
class BoolState(BaseState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, _type = bool, **kwargs)


class State:
    """Facade for the State classes. Allows for type inference."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __set_name__(self, owner, name):
        t = owner.__annotations__.get(name, None)
        setattr(
                owner, 
                name,
                BaseState[
                    t
                ](
                        *self.args,
                        **self.kwargs).__set_name__(
                        owner, 
                        name)
        )


__all__ = ["BaseState", "NumberState", "IntState", "FloatState", "StrState", "BoolState", "State"]
