from game.objects import MeleeWeapon

WeaponFactory = MeleeWeapon.factory()
SwordFactory = WeaponFactory.bind(
        name_infix = "Sword",
        damage = 10,
        damage_type = "SLASHING",
        max_stack_size = 1
)

LegendarySwordFactory = SwordFactory.bind(
        name_prefix = "Legendary",
        damage = 100
)

GodSwordFactory = LegendarySwordFactory.bind(
        name_prefix = "Godly",
        damage = 1000
)

sword = SwordFactory.create()
legendary_sword = LegendarySwordFactory.create()
god_sword = GodSwordFactory.create()
print(sword.to_json(
        "name_prefix",
        "name_infix",
        "name_suffix",
        "damage",
        "damage_type",
        "max_stack_size"
))
print(legendary_sword.to_json(
        "name_prefix",
        "name_infix",
        "name_suffix",
        "damage",
        "damage_type",
        "max_stack_size"
))
print(god_sword.to_json(
        "name_prefix",
        "name_infix",
        "name_suffix",
        "damage",
        "damage_type",
        "max_stack_size"
))

print(sword)
print(legendary_sword)
print(god_sword)

print(sword.detailed_description())
print(legendary_sword.detailed_description())
print(god_sword.detailed_description())
