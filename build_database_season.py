# =============================================================================
#          File: build_database_season.py
#        Author: Andre Brener
#       Created: 10 Oct 2016
# Last Modified: 22 Aug 2017
#   Description: description
# =============================================================================
import os

import pandas as pd


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if not file.startswith('.'):
                yield file


def concat_df(path, master_df):
    df_list = list(get_files(path))
    for df in df_list:
        print(df)
        full_path = '{0}/{1}'.format(path, df)
        if os.stat(full_path).st_size > 5:
            new_df = pd.read_csv(full_path)
        else:
            new_df = pd.DataFrame()
        master_df = pd.concat([master_df, new_df])
    return master_df


def build_database(dir_path, competition):
    dirs = [
        d for d in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, d))
    ]
    for season in dirs:
        total_games = pd.DataFrame()
        total_players = pd.DataFrame()
        print(season)
        os.makedirs('database/{0}/{1}'.format(competition, season))
        path_games = '{0}/{1}/processed_games/'.format(dir_path, season)
        path_players = '{0}/{1}/processed_players/'.format(dir_path, season)
        total_games = concat_df(path_games, total_games)
        total_players = concat_df(path_players, total_players)

        total_games.to_csv(
            'database/{0}/{1}/games_database.csv'.format(competition, season),
            index=False)
        total_players.to_csv(
            'database/{0}/{1}/players_database.csv'.format(competition,
                                                           season),
            index=False)


if __name__ == '__main__':

    os.makedirs('database', exist_ok=True)
    dir_path = 'data/'
    dirs = [
        d for d in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, d))
    ]
    for competition in dirs:
        print(competition)
        os.makedirs('database/{0}'.format(competition), exist_ok=True)
        path = 'data/{0}'.format(competition)
        build_database(path, competition)
