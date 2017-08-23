# =============================================================================
#          File: build_shots_database.py
#        Author: Andre Brener
#       Created: 10 Oct 2016
# Last Modified: 22 Aug 2017
#   Description: description
# =============================================================================
import os

import pandas as pd


def concat_df(path, master_df):
    df = pd.read_csv(path)
    shots_df = df[df['action_type'] == 'shot']
    master_df = pd.concat([master_df, shots_df])
    return master_df


def build_database(comp_path, competition):
    total_shots = pd.DataFrame()
    dirs = [
        d for d in os.listdir(comp_path)
        if os.path.isdir(os.path.join(comp_path, d))
    ]
    for season in dirs:
        print(season)
        shots_path = '{0}/{1}/games_database.csv'.format(comp_path, season)
        total_shots = concat_df(shots_path, total_shots)
    total_shots.to_csv(
        'shots_database/{0}/shots_database.csv'.format(competition),
        index=False)


if __name__ == '__main__':

    os.makedirs('shots_database', exist_ok=True)
    dir_path = 'database/'
    dirs = [
        d for d in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, d))
    ]
    for competition in dirs:
        print(competition)
        os.makedirs('shots_database/{0}'.format(competition), exist_ok=True)
        path = 'database/{0}'.format(competition)
        build_database(path, competition)
