"""

#######################
###### GEN 1 ##########
#######################

Best Pokemon
      pokemon subname        move1         move2         move3       move4  a_score  d_score  ad_score    -A name     -A    -D name     -D
0      Mewtwo          Double-Edge   Thunderbolt      Ice Beam     Psychic    529.0    100.6       5.3    Snorlax  107.9   Beedrill  216.4
1     Snorlax          Double-Edge          Surf    Earthquake  Rock Slide    413.7     98.2       4.2    Snorlax  161.8  Hitmonlee  343.6
2         Mew          Thunderbolt  Seismic Toss    Earthquake     Psychic    382.9     96.3       4.0  Exeggutor   81.2   Beedrill  208.5
3     Slowbro                 Surf      Ice Beam  Seismic Toss     Psychic    356.4    125.5       2.8    Slowbro   76.2  Vileplume  444.0
4      Lapras          Double-Edge          Surf   Thunderbolt    Ice Beam    324.4    114.7       2.8    Snorlax   83.6  Hitmonlee  344.4
5     Machamp          Double-Edge  Seismic Toss    Earthquake  Rock Slide    434.3    159.5       2.7    Slowbro  127.5     Mewtwo  463.2
6  Kangaskhan          Double-Edge          Surf    Earthquake  Rock Slide    353.2    133.1       2.7    Snorlax  140.0  Hitmonlee  426.3
7   Exeggutor          Double-Edge    Solar Beam       Psychic                407.5    157.2       2.6    Snorlax   93.3   Beedrill  508.9
8      Zapdos          Double-Edge   Thunderbolt           Fly                328.9    132.8       2.5     Rhydon   39.8       Jynx  328.7
9    Vaporeon          Double-Edge          Surf      Ice Beam                292.5    119.8       2.4     Lapras   64.5  Vileplume  274.0

Best Starter
14  Blastoise          Double-Edge          Surf    Ice Beam  Seismic Toss    287.7    138.4       2.1  Slowbro  82.2  Vileplume  408.6
31  Charizard           Fire Blast  Seismic Toss  Earthquake           Fly    328.7    215.6       1.5  Slowbro  89.6     Rhydon  740.8
36   Venusaur          Double-Edge    Solar Beam                              235.3    186.8       1.3  Snorlax  80.7   Beedrill  617.7

#######################
###### GEN 3 ##########
#######################

Best Pokemon
    pokemon subname        move1         move2         move3       move4  a_score  d_score  ad_score   -A name     -A             -D name     -D
0    Kyogre          Water Spout   Thunderbolt      Ice Beam  Earthquake    631.0    107.1       5.9  Ludicolo  144.2           Vileplume  243.6
1   Groudon             Eruption  Seismic Toss    Earthquake  Rock Slide    536.1    127.3       4.2     Lugia  126.8              Kyogre  636.0
2    Mewtwo          Thunderbolt      Ice Beam    Earthquake     Psychic    465.2    110.2       4.2   Umbreon   96.4           Heracross  341.6
3     Lugia          Thunderbolt      Ice Beam    Earthquake   Aeroblast    327.3     81.5       4.0   Slaking   73.7  DeoxysAttack Forme  223.2
4   Snorlax          Double-Edge          Surf  Seismic Toss  Earthquake    379.9     96.8       3.9  Skarmory  111.1  DeoxysAttack Forme  351.4
5     Ho-oh          Sacred Fire    Giga Drain    Earthquake         Fly    428.3    130.2       3.3     Lugia  104.3              Rhydon  576.5
6  Rayquaza          Thunderbolt      Ice Beam    Earthquake         Fly    514.0    155.8       3.3   Slaking  117.6  DeoxysAttack Forme  583.6
7       Mew          Bullet Seed      Ice Beam    Earthquake     Psychic    332.8    105.5       3.2     Ho-oh   72.3           Heracross  326.4
8   Slaking          Double-Edge    Fire Blast  Seismic Toss  Earthquake    277.8     89.3       3.1  Regirock   89.0              Kyogre  292.8
9  Hariyama          Double-Edge  Seismic Toss    Earthquake  Rock Slide    391.0    134.5       2.9     Lugia  102.1  DeoxysAttack Forme  476.7

Best Starter

48    Venusaur       Double-Edge   Petal Dance  Sludge Bomb    Earthquake    349.9    173.1       2.0    Lugia  70.3  DeoxysAttack Forme  517.8
51   Blastoise       Double-Edge          Surf     Ice Beam  Seismic Toss    277.8    142.4       1.9  Suicune  74.8           Vileplume  408.6
104  Charizard        Fire Blast  Seismic Toss   Earthquake           Fly    315.3    231.8       1.4    Lugia  81.1              Rhydon  896.5

42  Feraligatr       Double-Edge           Surf  Seismic Toss     Earthquake    310.4    149.9       2.1     Lugia  78.7  Vileplume  478.6
64    Meganium       Double-Edge    Bullet Seed    Earthquake  Ancient Power    270.3    160.9       1.7  Skarmory  54.3   Camerupt  503.6
70  Typhlosion        Fire Blast  Thunder Punch  Seismic Toss     Earthquake    323.6    205.5       1.6  Rayquaza  74.6     Kyogre  862.9

16   Swampert          Ice Beam   Seismic Toss  Earthquake  Rock Slide    385.5    149.8       2.6    Lugia  93.9  Vileplume   751.2
62   Blaziken        Fire Blast   Seismic Toss  Earthquake  Rock Slide    439.7    256.2       1.7  Slowbro  98.6     Kyogre  1020.0
123  Sceptile       Double-Edge  Thunder Punch  Leaf Blade  Earthquake    310.2    252.5       1.2  Snorlax  83.6   Rayquaza   718.5

"""

# Standard library imports

# Third party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Local application imports
import settings

def get_pokemon(pokedex, name, subname=''):
    pokemons = pokedex[(pokedex['name'] == name)]
    return pokemons[(pokemons['subname'] == subname)].iloc[0]

def get_move(attackdex, name):
    return attackdex[attackdex['name'] == name].iloc[0]

def add_ad_score(results):
    # ad_score = results['a_score'] - results['d_score']
    ad_score = results['a_score'] / results['d_score']

    results['ad_score'] = pd.Series(ad_score, index=results.index)

    return results

def add_best_worst(results):
    full_pokemon_names = results['pokemon'] + results['subname']

    # temp = full_pokemon_names[np.argmax(vectors.values, axis=1)].values
    # results['+A name'] = pd.Series(temp, index=results.index)
    # temp = np.max(vectors.values, axis=1)
    # results['+A'] = pd.Series(temp, index=results.index).round(decimals=1)
    temp = full_pokemon_names[np.argmin(vectors.values, axis=1)].values
    results['-A name'] = pd.Series(temp, index=results.index)
    temp = np.min(vectors.values, axis=1)
    results['-A'] = pd.Series(temp, index=results.index).round(decimals=1)
    temp = full_pokemon_names[np.argmax(vectors.values, axis=0)].values
    results['-D name'] = pd.Series(temp, index=results.index)
    temp = np.max(vectors.values, axis=0)
    results['-D'] = pd.Series(temp, index=results.index).round(decimals=1)
    # temp = full_pokemon_names[np.argmin(vectors.values, axis=0)].values
    # results['+D name'] = pd.Series(temp, index=results.index)
    # temp = np.min(vectors.values, axis=0)
    # results['+D'] = pd.Series(temp, index=results.index).round(decimals=1)

    return results

def plot_matrix(results, vectors, N=10):
    full_pokemon_names = np.array(results['pokemon'] + results['subname'])

    z = vectors.values
    xticks = full_pokemon_names
    yticks = full_pokemon_names

    # attack_indices = (-np.array(results['a_score'])).argsort()
    # defense_indices = np.array(results['d_score']).argsort()

    attack_indices = defense_indices = \
            (-np.array(results['ad_score'])).argsort()

    z = z[attack_indices, :]
    z = z[:, defense_indices]
    yticks = yticks[attack_indices]
    xticks = xticks[defense_indices]

    z = z[:N, :N]
    z = np.log(z)

    plt.imshow(z, cmap=plt.get_cmap('RdYlGn'))

    plt.xticks(range(z.shape[1]), xticks[:z.shape[1]], rotation=45)
    plt.yticks(range(z.shape[1]), yticks[:z.shape[1]], rotation=45)

    plt.xlabel('Defending Pokemon')
    plt.ylabel('Attacking Pokemon')

def hist_a_pokemon(results, vectors, IDX=0, nbins=30):
    pokemon = results.iloc[IDX]
    attack_vector = vectors.values[IDX, :]
    defense_vector = vectors.values[:, IDX]

    full_name = pokemon['pokemon']
    if pokemon['subname'] != '':
        full_name += '-' + pokemon['subname']

    ratio_vector = attack_vector[defense_vector != 0] \
                   / defense_vector[defense_vector != 0]

    plt.subplot(3, 1, 1)
    bins = np.exp((np.linspace(np.log(30),
                               np.log(1000), num=nbins)))
    plt.xscale('log')
    plt.hist(attack_vector, bins=bins)
    plt.ylabel('damage dealt')
    plt.title(full_name)

    plt.subplot(3, 1, 2)
    bins = np.exp((np.linspace(np.log(30),
                               np.log(1000), num=nbins)))
    plt.xscale('log')
    plt.hist(defense_vector, bins=bins)
    plt.ylabel('damage taken')

    plt.subplot(3, 1, 3)
    bins = np.exp((np.linspace(np.log(0.01),
                               np.log(100), num=nbins)))
    plt.xscale('log')
    plt.hist(ratio_vector, bins=bins)
    plt.ylabel('ratio')


if __name__ == '__main__':
    """Settings"""

    # METHOD = 'mean'
    # METHOD = 'median'
    METHOD = 'harmonic_mean'
    # METHOD = 'min'

    settings.init(GEN=2, METHOD=METHOD)

    # number of top pokemon to show
    N = 10

    """Load Data"""

    with pd.HDFStore(settings.result_filepath, mode='r') as store:
        results = store['result']
        vectors = store['vectors']

    # with pd.HDFStore(settings.store_filepath, mode='r') as store:
    #     # poketypes = store['poketypes']
    #     # move_categories = store['move_categories']
    #     poketype_chart = store['poketype_chart']
    #     pokedex = store['pokedex']
    #     attackdex = store['attackdex']
    #     learnsets = store['learnsets']

    """find attack - defense score"""

    results = add_ad_score(results)

    """find best/worst attack and defense values (and pokemon)"""

    results = add_best_worst(results)

    """round"""

    results['a_score'] = results['a_score'].round(decimals=1)
    results['d_score'] = results['d_score'].round(decimals=1)
    results['ad_score'] = results['ad_score'].round(decimals=1)

    """Attack Result"""

    # attack_results = results.sort_values(by=['a_score'], ascending=False)
    # attack_results = attack_results.reset_index(drop=True)
    # print(attack_results.head(n=N))

    """Defense Result"""

    # defense_results = results.sort_values(by=['d_score'])
    # defense_results = defense_results.reset_index(drop=True)
    # print(defense_results.head(n=N))

    """Combined Result"""

    combined_results = results.sort_values(by=['ad_score'], ascending=False)
    combined_results = combined_results.reset_index(drop=True)
    print(combined_results.head(n=N))

    """Starters"""

    # starters = [
    #     'Venusaur', 'Charizard', 'Blastoise',
    #     'Meganium', 'Typhlosion', 'Feraligatr',
    #     'Sceptile', 'Blaziken', 'Swampert'
    # ]
    # indices = [i for i in range(combined_results.shape[0])
    #            if combined_results.iloc[i]['pokemon'] in starters]
    # print(combined_results.iloc[indices])

    """Grid Image"""

    plt.figure()
    plot_matrix(results, vectors, N=N)
    # plt.show()

    """Histograms"""

    sorted_idx = list(results.sort_values(by=['ad_score'],
                                          ascending=False).index)
    IDX = sorted_idx[0]

    plt.figure()
    hist_a_pokemon(results, vectors, IDX=IDX, nbins=30)
    plt.show()

    """Moves by sorted by occurrence"""
