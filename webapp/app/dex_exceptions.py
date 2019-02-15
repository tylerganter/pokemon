#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

# TODO better solution for this?
# Skip pokemon that can't learn moves...or some other weird problem
attacking_pokemon_exceptions = [
    'Ditto',
    'Wobbuffet',
    'Smeargle',
    'Wynaut'
]

move_skip_list = [
    'Dream Eater',
    'Focus Punch',

    # User receives recoil damage. (1/4)
    # 'Head Charge', 'Submission', 'Take Down', 'Wild Charge',

    # User receives recoil damage. (1/3)
    # 'Brave Bird', 'Double-Edge', 'Flare Blitz', 'Volt Tackle', 'Wood Hammer',

    # User receives recoil damage. (1/2)
    'Head Smash', 'Light of Ruin', 'Mind Blown',

    # User attacks for 2-3 turns but then becomes confused.
    'Outrage', 'Thrash', 'Petal Dance',

    # sharply lowers attack
    'Psycho Boost', 'Overheat', 'Draco Meteor', 'Fleur Cannon', 'Leaf Storm',

    # Damage occurs 2 turns later.
    'Future Sight', 'Doom Desire',
]
