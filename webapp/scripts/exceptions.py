#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

# TODO better solution for this?
attacking_pokemon_exceptions = [
    'Ditto',
    'Wobbuffet',
    'Smeargle',
    'Wynaut'
]
best_combo_exception = {
    'a_score': 0,
    'move_poketypes': [''] * 4,
    'move_names': [''] * 4
}


move_skip_list = [
    'Future Sight',
    'Dream Eater',
    'Focus Punch',

    # moves that lock the user in for multiple moves
    'Outrage', 'Thrash',

    # self harming moves
    # 'Double-Edge'

    # sharply lowers attack
    'Psycho Boost',
    'Overheat'
]
