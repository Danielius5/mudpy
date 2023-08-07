from itertools import count

from objects import *
import re

# minimize code repetition
def validator(pattern_string):
    pattern = re.compile(pattern_string)
    return lambda value: pattern.match(value) is not None


class User(GameObject, freeze = True):
    username: str = State(validator(r"^[a-zA-Z0-9_.-]{3,}$"))
    email: str = State(validator(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"))
    password: str = State(
            validator(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"),
            min_length = 8,
            max_length = 64,
            )
    age: int = State(minimum = 13)
    active: bool = State(default = False)
    
    def __init__(self, username, email, password, age, active = False):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password
        self.age = age
        self.active = active
        
    def __repr__(self):
        return f"User(username = {self.username}, email = {self.email}, password = {self.password}, age = {self.age}, active = {self.active})"
    
    
if __name__ == "__main__":
    user = User("JohnDoe", "blah@blah.com", "Password123", 20)
    print(user)
    user.username = "JaneDoe"


    