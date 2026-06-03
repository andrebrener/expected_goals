# =============================================================================
#          File: match_processsing.py
#        Author: Andre Brener
#       Created: 18 Sep 2016
# Last Modified: 22 Aug 2017
#   Description: description
# =============================================================================
import os

from dataset import get_dataset


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if not file.startswith('.'):
                yield file


def process_game(dir_path):
    dirs = [
        d for d in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, d))
    ]
    for directory in dirs:
        print(directory)
        new_path_games = '{0}/{1}/processed_games'.format(dir_path, directory)
        new_path_players = '{0}/{1}/processed_players'.format(dir_path,
                                                              directory)
        season_path = '{0}/{1}'.format(dir_path, directory)
        print(season_path)
        os.makedirs(new_path_players, exist_ok=True)
        os.makedirs(new_path_games, exist_ok=True)
        games_list = list(get_files(season_path))
        for game in games_list:
            print(game)
            full_path = '{0}/{1}'.format(season_path, game)
            game_dataset, players = get_dataset(full_path)
            game_name = game[:-4]
            new_name_game = '{0}/processed_games/{1}.csv'.format(season_path,
                                                                 game_name)
            new_name_players = '{0}/processed_players/{1}.csv'.format(
                season_path, game_name)
            game_dataset.to_csv(new_name_game, index=False, encoding='utf-8')
            players.to_csv(new_name_players, index=False, encoding='utf-8')


if __name__ == '__main__':

    path = 'data/ligue1'
    process_game(path)
