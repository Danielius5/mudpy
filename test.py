import re

from objects import *


# minimize code repetition
def validator(pattern_string):
    pattern = re.compile(pattern_string)
    return lambda value: pattern.match(value) is not None


# noinspection PyTypeChecker
class User(GameObject):
    username: str = State(validator(r"^[a-zA-Z0-9_.-]{3,}$"))
    email: str = State(validator(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"), freeze = True)
    password: str = State(
            validator(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"),
            min_length = 8,
            max_length = 64,
    )
    dob: str = State(validator(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/((19|20)\d\d)$"), freeze = True)
    active: bool = State(default = True)


    def __repr__(self):
        return f"User(username = {self.username!r}, email = {self.email!r}, password = {self.password!r}, dob = {self.dob!r}, active = {self.active!r})"


if __name__ == "__main__":
    u = User(username = "test", email = "blah@blah.com", password = "Password1", dob = "01/01/2000")
    print(u.uuid)
    print(u)
