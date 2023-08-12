import random

def __getattr__(name):
    if name.startswith("d") and  (num := name[1:]).isdigit():
        roll = lambda *mods: random.randint(1, int(num)) + sum(mods)
        roll.x = lambda times, *mods: [random.randint(1, int(num)) + sum(mods) for _ in range(times)]
        return roll
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
