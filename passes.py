# =============================================================================
#          File: passes.py
#        Author: Andre Brener
#       Created: 06 Sep 2016
# Last Modified: 21 Sep 2016
#   Description: description
# =============================================================================
from math import sqrt

import pandas as pd

from squawka.utils import SquawkaReport

match = 'data/premier_league/season_2012_2013/epl_157.xml'
# match = 'data/world_cup/brazil_2014/world-cup_7244.xml'
# match = 'data/world-cup_7251.xml'
# match = 'data/world-cup_7298.xml'
# match = 'data/world-cup_7254.xml'
# match = 'data/world-cup_7269.xml'
# match = 'data/world-cup_7250.xml'

report = SquawkaReport(match)

passes = pd.DataFrame(report.all_passes)
# takeons = pd.DataFrame(report.takeons)


def get_vertical_coord(coord):
    comma_index = coord.index(',')
    temp = coord[: comma_index]
    if len(temp) == 0:
        return None
    else:
        vert_coord = float(temp)
        return vert_coord


def get_horizontal_coord(coord):
    comma_index = coord.index(',')
    temp = coord[comma_index + 1:]
    if len(temp) == 0:
        return None
    else:
        hor_coord = float(temp)
        return hor_coord


def get_distance(df):
    vert_dist = (df['end_vert_coord'] - df['start_vert_coord']) ** 2
    hor_dist = (df['end_hor_coord'] - df['start_hor_coord']) ** 2
    dist = sqrt(vert_dist + hor_dist)
    return dist


def assist_type(df):
    if df['through_ball'] == 'true':
        return 'throughball'
    elif df['long_ball'] == 'true':
        return 'long_ball'
    elif df['headed'] == '1':
        return 'headed'
    elif df['throw_ins'] == '1':
        return 'throw_in'
    else:
        return 'pass'

lista = passes['end'].tolist()
for i in lista:
    test = get_vertical_coord(i)
passes['end_vert_coord'] = passes['end'].apply(get_vertical_coord)
passes['end_hor_coord'] = passes['end'].apply(get_horizontal_coord)
passes['start_vert_coord'] = passes['start'].apply(get_vertical_coord)
passes['start_hor_coord'] = passes['start'].apply(get_horizontal_coord)
passes['distance'] = passes.apply(get_distance, axis=1)
passes['pass_type'] = passes.apply(assist_type, axis=1)
passes['injurytime_play'] = passes['injurytime_play'].fillna(0).astype(int)

passes_assists = passes[passes['assists'] == 'true']
passes_assists = passes_assists[['start_hor_coord',
                                 'start_vert_coord',
                                 'end_hor_coord',
                                 'end_vert_coord',
                                 'distance',
                                 'minsec',
                                 'mins',
                                 'secs',
                                 'team_id',
                                 'pass_type']]
# print(passes_assists)

# takeons['vert_coord'] = takeons['loc'].apply(get_vertical_coord)
# takeons['hor_coord'] = takeons['loc'].apply(get_horizontal_coord)
# takeons['minsec_original'] = takeons['minsec'].astype(int)

# takeons = takeons[takeons['type'] == 'Success']

# takeons = takeons[['minsec',
# 'player_id',
# 'team_id']]

# # print(takeons)
# teams = takeons['team_id'].tolist()
# minutes = takeons['minsec'].tolist()


# def function(teams, i):
# if teams[i] != teams[i - 1]:
# return minutes[i - 1]
# else:
# return function(teams, i - 1)
# # takeons['test'] = lista
# lista_test = [0]
# for i in range(1, len(teams)):
# value = function(teams, i)
# lista_test.append(value)

# takeons['lista_test'] = lista_test
# print(takeons)
