import re

from objects import *


# minimize code repetition
def validator(pattern_string):
    pattern = re.compile(pattern_string)
    return lambda value: pattern.match(value) is not None


# noinspection PyTypeChecker
class User(GameObject):

    username: str = State(validator(r"^[a-zA-Z0-9_]{3,16}$"))
    active: bool = State(default = True)
    
    def __repr__(self):
        return f"<User username={self.username!r} active={self.active!r}>"

if __name__ == "__main__":
    u = User("test")
    print(u)