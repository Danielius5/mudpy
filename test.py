import sys

from objects import *

class TestGO(GameObject):
    name: str = State(min_length = 1, max_length = 10)
    age: int = State(minimum = 0, maximum = 100)
    is_alive: bool = State(default = True)
    items: dict = State(default_factory = dict)

        
        
if __name__ == "__main__":
    for attr_name in [
        "name",
        "age",
        "is_alive",
        "items",
    ]:
        print(f"{attr_name}: {getattr(TestGO, attr_name)}")
    print()
    
    go = TestGO("Test")
    for attr_name in [
        "name",
        "age",
        "is_alive",
        "items",
    ]:
        print(f"{attr_name}: {getattr(go, attr_name)}")
    print()
    
    # count references to TestGO
    print(sys.getrefcount(go))