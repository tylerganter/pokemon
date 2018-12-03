"""

GEN 1
Red & Blue
Yellow

GEN 2
Gold & Silver
Crystal

GEN 3
Ruby & Sapphire
FireRed & LeafGreen
Emerald

GEN 4
Diamond & Pearl
Platinum
HeartGold & SoulSilver

GEN 5
Black & White
Black 2 & White 2

GEN 6
X & Y
OmegaRuby & AlphaSapphire

GEN 7
Sun & Moon
Ultra Sun & Ultra Moon
Let's Go Pikachu & Let's Go Eevee


https://www.smogon.com/dex/rs/pokemon/ninetales/




"""

import os

gen_to_path = ['RB', 'GS', 'RS', 'DP', 'BW', 'XY', 'SM']

base_url = 'https://www.smogon.com/dex/{}'.format(gen_to_path[__gen__-1])

pokedex_url = os.path.join(base_url, 'pokemon')
attackdex_url = os.path.join(base_url, 'moves')

# TODO CONTINUE HERE
# shift get_data functions to here using SMOGON
# when getting pokedex: get url per pokemon


print(pokedex_url)

if __name__ == '__main__':
    __gen__ = 1


