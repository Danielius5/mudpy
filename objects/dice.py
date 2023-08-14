import random

def __getattr__(name):
    if name.startswith("d"):
        sides = name[1:]
        if not sides.isdigit():
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        return lambda: random.randint(1, int(sides))
    elif name == "roll_many":
        return lambda n, sides: [random.randint(1, int(sides[1:])) for _ in range(int(n))]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
