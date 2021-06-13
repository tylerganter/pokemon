"""Hardcoded exceptions"""

# Skip pokemon that can't learn moves...or some other weird problem
ATTACKING_POKEMON_EXCEPTIONS = ["Ditto", "Wobbuffet", "Smeargle", "Wynaut"]

MOVE_SKIP_LIST = [
    "Dream Eater",
    "Focus Punch",
    # User receives recoil damage. (1/4)
    # 'Head Charge', 'Submission', 'Take Down', 'Wild Charge',
    # User receives recoil damage. (1/3)
    # 'Brave Bird', 'Double-Edge', 'Flare Blitz', 'Volt Tackle', 'Wood Hammer',
    # User receives recoil damage. (1/2)
    "Head Smash",
    "Light of Ruin",
    "Mind Blown",
    # User attacks for 2-3 turns but then becomes confused.
    "Outrage",
    "Thrash",
    "Petal Dance",
    # sharply lowers attack
    "Psycho Boost",
    "Overheat",
    "Draco Meteor",
    "Fleur Cannon",
    "Leaf Storm",
    # Damage occurs 2 turns later.
    "Future Sight",
    "Doom Desire",
]
