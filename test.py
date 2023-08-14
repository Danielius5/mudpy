from objects import Armor

a = Armor()
print(a)
serialized = a.to_json()
print(serialized)
b = Armor.from_json(serialized)
print(b)
