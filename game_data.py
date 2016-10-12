# =============================================================================
#          File: game_data.py
#        Author: Andre Brener
#       Created: 25 Sep 2016
# Last Modified: 25 Sep 2016
#   Description: description
# =============================================================================
from math import sqrt
from datetime import datetime, timedelta

import pandas as pd

from bs4 import BeautifulSoup
from squawka.utils import SquawkaReport


def get_dataset(game):

    def get_competition(game):
        if 'premier_league' in game:
            return 'epl'
        elif 'serie_a' in game:
            return 'serie_a'
        elif 'bundesliga' in game:
            return 'bundesliga'
        elif 'la_liga' in game:
            return 'la_liga'
        elif 'ligue1' in game:
            return 'ligue1'
        elif 'mls' in game:
            return 'mls'
        elif 'eredivisie' in game:
            return 'eredivisie'
        elif 'brasileirao' in game:
            return 'brasileirao'
        elif 'world_cup' in game:
            return 'world_cup'

    competition = get_competition(game)

# Get Dfs

    report = SquawkaReport(game)

    passes = pd.DataFrame(report.all_passes)
    crosses = pd.DataFrame(report.crosses)
    goals_attempts = pd.DataFrame(report.goals_attempts)
    players = pd.DataFrame(report.players)
    teams = pd.DataFrame(report.teams)
    subs = pd.DataFrame(report.swap_players)
    cards = pd.DataFrame(report.cards)
    takeons = pd.DataFrame(report.takeons)
    goal_keeping = pd.DataFrame(report.goal_keeping)
    tackles = pd.DataFrame(report.tackles)
    interceptions = pd.DataFrame(report.interceptions)
    fouls = pd.DataFrame(report.fouls)
    clearances = pd.DataFrame(report.clearances)

# Teams

    def get_teams(teams_df):
        # Check if there is data for teams
        if teams_df.empty:
            return None
        else:
            teams_id = list(teams_df['id'].get_values())
            team_a = 'team_{0}'.format(teams_id[0])
            team_b = 'team_{0}'.format(teams_id[1])
            team_list = [(teams_id[0], team_a), (teams_id[1], team_b)]
            teams_trunc = teams_df[['id', 'state']]
            teams_final = teams_trunc.rename(columns={'id': 'team_id'})

        return teams_final

    teams = get_teams(teams)

    # print(teams)

    # If there are no Teams, discard the game
    if teams is None:
        empty_game = pd.DataFrame()
        empty_players = pd.DataFrame()
        return empty_game, empty_players


# Global Functions
    df_list = [passes, crosses, goals_attempts]

    def drop_duplicates_dfs(df_list):
        new_df_list = []
        for df in df_list:
            new_df = df.drop_duplicates()
            new_df_list.append(new_df)
        return new_df_list

    passes, crosses, goals_attempts = drop_duplicates_dfs(df_list)

    def include_variable(df, variable):
        if variable not in df.columns:
            df[variable] = [0] * df.shape[0]

    def transform_true(string):
        if string == 'true':
            return 1
        else:
            return 0

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

    def get_minsec(df):
        df['mins'] = df['mins'].astype(int)
        df['secs'] = df['secs'].astype(int)
        df['minsec'] = 60 * df['mins'] + df['secs']


get_dataset('data/premier_league/season_2012_2013/epl_100.xml')
