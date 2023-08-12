"""
Bounded State descriptors for use in the State pattern.
These are type checked and enforce constraints on the values they hold.
This is useful for managing data from the users to make sure its clean and expected.
"""

import os
import typing
import weakref

from ..utils import search_subs


class Meta(type):
    def __getitem__(self, item):
        if item is not None:
            if isinstance(item, type):
                item = item.__name__
            try:
                name = f"{item.lower().title()}State"
                sub = search_subs(self.__subclasses__(), name)
                if sub is None:
                    return type(name, (BaseState,), {})
                return sub
            except AttributeError:
                pass
        return type("GenericState", (BaseState,), {})


class BaseState(metaclass = Meta):
    """
    Represents a constraint on a value.
    
    """

    def __init__(self, *constraints, default = None, default_factory = None, _type = None, freeze = False, post_process = None, weak=False, **misc_data):
        
        if default is not None and default_factory is not None:
            raise ValueError("Cannot specify both default and default_factory")
        self.constraints = constraints
        self.default = default
        self.default_factory = default_factory
        self.post_process = post_process
        self.type = _type or type(default) if default is not None else None
        self.freeze = freeze
        self.frozen = False
        self.weak = weak
        self.misc_data = misc_data

    def __set_name__(self, owner, name):
        self.name = name
        return self

    def __get__(self, instance, owner):
        """
        Attempts to get the value from the instance, if it doesn't exist, it will create it and return it using the default or default_factory
        """
        if instance is None:
            return self
        v = instance.__dict__.get(self.name, None)
        if v is None:
            v = (self.default_factory() if self.default_factory is not None else self.default)
            if self.weak:
                v = weakref.proxy(v, lambda ref: instance.__dict__.__delitem__(self.name))
            instance.__dict__[self.name] = v
        return v

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Cannot set state on class")
        if self.frozen:
            raise AttributeError("Cannot set frozen state")
        if not self.skip_checking:
            if self.type is not None:
                if not isinstance(value, self.type):
                    raise TypeError(f"Expected {self.type}, got {type(value)} for {self.name}")
            if not all(constraint(value) for constraint in self.constraints):
                raise ValueError(f"Value {value} does not meet all constraints for {self.name}")
        v = (self.post_process(value) if self.post_process is not None else value)
        if self.weak:
            v = weakref.proxy(v, lambda ref: instance.__dict__.__delitem__(self.name))
        instance.__dict__[self.name] = v
        self.frozen = self.freeze

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def __init_subclass__(
            cls,
            skip_checking = os.getenv("SKIP_CHECKING", "false").lower() in ["true", "1", "t", "y", "yes", "on"],
            **kwargs):
        super().__init_subclass__(**kwargs)
        cls.skip_checking = skip_checking


# noinspection PyArgumentList
class NumberState(BaseState):
    def __init__(self, *args, minimum = None, maximum = None, **kwargs):
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
    def __init__(self, *args,  min_length = None, max_length = None, **kwargs):
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


# noinspection PyArgumentList, PyTypeChecker
class DictState(BaseState):
    def __init__(self, *args, expected = None, **kwargs):
        self.expected = expected or {}
        def check_value(value):
            if not isinstance(value, dict):
                return False
            for k, v in value.items():
                if k not in self.expected:
                    return False
                expected_value = self.expected[k]
                if isinstance(expected_value, typing._UnionGenericAlias) and type(None) in expected_value.__args__: 
                    if v is None:
                        continue
                    for t in expected_value.__args__:
                        if t is type(None):
                            continue
                        if isinstance(v, t):
                            break
                    else:
                        return False
                elif not isinstance(v, expected_value):
                    return False
            return True
        super().__init__(check_value, *args, **kwargs)
        

# noinspection PyArgumentList
class State:
    """
    Facade for the State classes. Allows for type inference.
    Looks up the appropriate state type based on the type annotation of the attribute.
    """

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
                        **self.kwargs)
                .__set_name__(
                        owner,
                        name
                )
        )


__all__ = ["BaseState", "NumberState", "IntState", "FloatState", "StrState", "BoolState", "DictState", "State"]
