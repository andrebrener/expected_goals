
# =============================================================================
#          File: shots_analysis.py
#        Author: Andre Brener
#       Created: 11 Oct 2016
# Last Modified: 05 Nov 2016
#   Description: description
# =============================================================================
import pandas as pd

path = 'shots_database/shots_database.csv'

df = pd.read_csv(path)

print(df.shape)
# print(df.columns)
# df = df[(df['competition'] != 'world_cup') | (df['season_x'] == '2015-2016') |
# (df['is_own'] < 1)]


df = df[
    (df['competition'].isin(
        [
            'epl',
            'serie_a',
            'bundesliga',
            'la_liga',
            'ligue1'])) & (
                df['season_x'] == '2015-2016') & (
                    df['is_own'] < 1) & (
                        df['field_players_team'] > 8) &
    (df['field_players_rival'] > 8) &
    (df['goals_for'] < 6) & (df['goals_against'] < 6)]

print(df['competition'].value_counts())
print(df['season_x'].value_counts())
# Filter the columns to start
df = df[['team_name',
         'competition',
         'season_x',
         'hor_coord',
         'vert_coord',
         'injurytime_play',
         'is_own',
         'is_rebound',
         'minsec',
         'result',
         'team_shot_number',
         'consecutive_passes',
         'goals_for',
         'goals_against',
         'field_players_team',
         'field_players_rival',
         'home_away',
         'game_month_x',
         'age',
         'position',
         # 'height',
         # 'weight',
         'state',
         'pos_dribbled',
         'shot_type',
         'assist_type',
         'as_start_vert_coord',
         'as_start_hor_coord',
         'as_end_vert_coord',
         'as_end_hor_coord',
         'assister_position',
         'time_from_rival_last_inc',
         'disp_player_pos']]


# Define functions to process data

def shot_number_ranges(n):
    if n < 2:
        return 'very_few'
    elif n < 5:
        return 'few'
    elif n < 7:
        return 'many'
    else:
        return 'too_many'


def time_ranges(n):
    if n < 900:
        return 'first_fifteen'
    elif n < 1800:
        return 'second_fifteen'
    elif n < 2700:
        return 'third_fifteen'
    elif n < 3600:
        return 'fourth_fifteen'
    elif n < 4500:
        return 'fifth_fifteen'
    else:
        return 'last_fifteen'


def horizontal_split(n):
    if n < 20:
        return 'wide_right'
    elif n < 40:
        return 'right'
    elif n < 60:
        return 'center'
    elif n < 80:
        return 'left'
    else:
        return 'wide_left'


def vertical_split(n):
    if n > 95:
        return 'very_close'
    elif n > 90:
        return 'close'
    elif n > 80:
        return 'mid_range'
    else:
        return 'long_range'


def age_range(n):
    if n < 21:
        return 'under_21'
    elif n < 24:
        return 'young'
    elif n < 27:
        return 'peak'
    elif n < 30:
        return 'declining'
    elif n < 33:
        return 'semi_old'
    else:
        return 'old'


def height_range(n):
    if n < 170:
        return 'very_short'
    elif n < 180:
        return 'short'
    elif n < 190:
        return 'medium'
    elif n < 200:
        return 'tall'
    else:
        return 'very_tall'


def weight_range(n):
    if n < 80:
        return 'light'
    elif n < 90:
        return 'normal'
    elif n < 90:
        return 'heavy'
    else:
        return 'very_heavy'


def possession_time_range(n):
    if n < 10:
        return 'very_short'
    elif n < 20:
        return 'short'
    elif n < 30:
        return 'long'
    else:
        return 'very_long'


def get_rebound(n):
    if n > 0:
        return 'yes'
    else:
        return 'no'


def get_season_part(n):
    if n > 6:
        return 'first_half_season'
    else:
        return 'second_half_season'


def get_goal_or_not(n):
    if n != 'goal':
        return 0
    else:
        return 1
# print(df['height'].value_counts())
# df['height'] = df['height'].fillna(0).apply(correct_bool).astype(int)
# df['weight'] = df['weight'].fillna(0).apply(correct_bool).astype(float)

# Filter table, fill na, define column types and apply functions

print(df['consecutive_passes'].value_counts())
print(df['assist_type'].value_counts())
df['consecutive_passes'] = df['consecutive_passes'].fillna(0).astype(int)

changer_cols = [
    'as_start_hor_coord',
    'as_start_vert_coord',
    'as_end_hor_coord',
    'as_end_vert_coord',
    'age']

for col in changer_cols:
    df[col] = df[col].fillna(0).astype(int)
    df = df[df[col] > 0]

df = df[(df['age'] > 13) & (df['age'] < 37)]

df['injurytime_play'] = df['injurytime_play'].fillna(2).astype(int)
df = df[df['injurytime_play'] < 2]

df['pos_dribbled'] = df['pos_dribbled'].fillna('no_dribble')
df['disp_player_pos'] = df['disp_player_pos'].fillna('no_ball_won')
df['time_range'] = df['minsec'].apply(time_ranges)
df['hor_location'] = df['hor_coord'].astype(int).apply(horizontal_split)
df['ver_location'] = df['vert_coord'].astype(int).apply(vertical_split)
df['hor_start_assist_location'] = df[
    'as_start_hor_coord'].astype(int).apply(horizontal_split)
df['hor_end_assist_location'] = df[
    'as_end_hor_coord'].astype(int).apply(horizontal_split)
df['ver_start_assist_location'] = df[
    'as_start_vert_coord'].astype(int).apply(vertical_split)
df['ver_end_assist_location'] = df[
    'as_end_vert_coord'].astype(int).apply(vertical_split)
df['age_range'] = df['age'].astype(int).apply(age_range)
# df['height_range'] = df['height'].apply(height_range)
# df['weight_range'] = df['weight'].apply(weight_range)
df['is_rebound'] = df['is_rebound'].apply(get_rebound)
df['result'] = df['result'].apply(get_goal_or_not)
df['season_partition'] = df['game_month_x'].apply(get_season_part)
df['pos_time'] = df['time_from_rival_last_inc'].apply(possession_time_range)
df['shot_number_team'] = df['team_shot_number'].apply(shot_number_ranges)

assist_cols = [
    'assister_position',
    'assist_type',
    'as_start_hor_coord',
    'as_start_vert_coord',
    'as_end_hor_coord',
    'as_end_vert_coord']

for col in assist_cols:
    df[col] = df[col].fillna('no_assist').astype(str)


# Define columns
total_cols = ['competition',
              'season_x',
              'team_name',
              'hor_location',
              'ver_location',
              'injurytime_play',
              'is_rebound',
              'time_range',
              'shot_number_team',
              'consecutive_passes',
              'goals_for',
              'goals_against',
              'field_players_team',
              'field_players_rival',
              'home_away',
              'season_partition',
              'age_range',
              'position',
              'state',
              'pos_dribbled',
              'shot_type',
              'assist_type',
              'hor_start_assist_location',
              'hor_end_assist_location',
              'ver_start_assist_location',
              'ver_end_assist_location',
              'assister_position',
              'pos_time',
              'result']

df = df[total_cols]
print(df.shape)

df.to_csv('shots_database/test_table_processed.csv', index=False)
print(df.sample(20))
