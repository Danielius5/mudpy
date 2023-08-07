from objects import *

class TestGO(GameObject):
    name: str = State(min_length = 1, max_length = 10)
    age: int = State(minimum = 0, maximum = 100)
    is_alive: bool = State(default = True)
    
    def __init__(self, name):
        self.name = name
        
        
if __name__ == "__main__":
    for attr_name in [
        "name",
        "age",
        "is_alive",
    ]:
        print(f"{attr_name}: {getattr(TestGO, attr_name)}")
    print()
    
    go = TestGO("Test")
    for attr_name in [
        "name",
        "age",
        "is_alive",
    ]:
        print(f"{attr_name}: {getattr(go, attr_name)}")
    print()
    
    # count references to TestGO
    print(sys.getrefcount(TestGO))