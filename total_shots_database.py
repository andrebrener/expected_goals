# =============================================================================
#          File: build_database.py
#        Author: Andre Brener
#       Created: 10 Oct 2016
# Last Modified:
#   Description: description
# =============================================================================
import os

import pandas as pd


def concat_df(path, master_df):
    new_df = pd.read_csv(path)
    master_df = pd.concat([master_df, new_df])
    return master_df


def build_database(dir_path):
    total_games = pd.DataFrame()
    dirs = [
        d for d in os.listdir(dir_path) if os.path.isdir(
            os.path.join(
                dir_path,
                d))]
    for competition in dirs:
        print(competition)
        path_games = '{0}/{1}/shots_database.csv'.format(dir_path, competition)
        total_games = concat_df(path_games, total_games)
    total_games.to_csv('shots_database/shots_database.csv', index=False)

dir_path = 'shots_database'
build_database(dir_path)
