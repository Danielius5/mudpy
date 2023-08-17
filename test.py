from game.objects import MeleeWeapon

weapon_factory_base = MeleeWeapon.factory()
print(weapon_factory_base)
print(weapon_factory_base())
