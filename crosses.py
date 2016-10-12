# =============================================================================
#          File: crosses.py
#        Author: Andre Brener
#       Created: 06 Sep 2016
# Last Modified: 06 Sep 2016
#   Description: description
# =============================================================================
from math import sqrt

import pandas as pd

from squawka.utils import SquawkaReport

report = SquawkaReport('data/world-cup_7247.xml')
# report = SquawkaReport('data/world-cup_7251.xml')
# report = SquawkaReport('data/world-cup_7254.xml')
# report = SquawkaReport('data/world-cup_7269.xml')
crosses = pd.DataFrame(report.crosses)
crosses = crosses.rename(columns={'team': 'team_id'})


def get_vertical_coord(coord):
    comma_index = coord.index(',')
    vert_coord = float(coord[: comma_index])
    return vert_coord


def get_horizontal_coord(coord):
    comma_index = coord.index(',')
    hor_coord = float(coord[comma_index + 1:])
    return hor_coord


def get_distance(df):
    vert_dist = (df['end_vert_coord'] -
                 df['start_vert_coord']) ** 2
    hor_dist = (df['end_hor_coord'] -
                df['start_hor_coord']) ** 2
    dist = sqrt(vert_dist + hor_dist)
    return dist


def if_corner(df):
    if df['start_vert_coord'] > 99 and df['start_hor_coord'] > 99:
        return 'left_corner'
    elif df['start_vert_coord'] > 99 and df['start_hor_coord'] < 1:
        return 'right_corner'
    else:
        return 'cross'


crosses['end_vert_coord'] = crosses['end'].apply(get_vertical_coord)
crosses['end_hor_coord'] = crosses['end'].apply(get_horizontal_coord)
crosses['start_vert_coord'] = crosses['start'].apply(get_vertical_coord)
crosses['start_hor_coord'] = crosses['start'].apply(get_horizontal_coord)
crosses['distance'] = crosses.apply(get_distance, axis=1)
crosses['injurytime_play'] = crosses['injurytime_play'].fillna(0).astype(int)
crosses['pass_type'] = crosses.apply(if_corner, axis=1)

crosses_assists = crosses[(crosses['type'] == 'Assist') | (crosses['type'] ==
                                                           'Completed')]
crosses_assists = crosses_assists[['start_hor_coord',
                                   'start_vert_coord',
                                   'end_hor_coord',
                                   'end_vert_coord',
                                   'distance',
                                   'minsec',
                                   'mins',
                                   'secs',
                                   'team_id',
                                   'pass_type']]

print(crosses_assists)
