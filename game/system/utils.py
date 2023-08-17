# levenshtein distance, based on percentage similarity
import functools
from dataclasses import dataclass


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if not s1:
        return len(s2)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return 1 - (previous_row[-1] / max(len(s1), len(s2)))


@functools.cache
def search_subs(cls, name):
    if cls.__name__.lower() == name.lower():
        return cls
    for sub in cls.__subclasses__():
        if (result := search_subs(sub, name)):
            return result
    raise ValueError(f"Invalid type or name {name}")


def go_dataclass(*args, **kwargs):
    defaults = {
            "init"       : True,
            "repr"       : True,
            "eq"         : True,
            "order"      : False,
            "unsafe_hash": False,
            "frozen"     : False,
            "kw_only"    : True,
    }
    return dataclass(*args, **{**defaults, **kwargs})
