
# =============================================================================
#          File: shots.py
#        Author: Andre Brener
#       Created: 08 Sep 2016
# Last Modified: 11 Sep 2016
#   Description: description
# =============================================================================
import pandas as pd

from bs4 import BeautifulSoup
from squawka.utils import SquawkaReport

match = 'data/world-cup_7244.xml'
# match = 'data/world-cup_7251.xml'
# match = 'data/world-cup_7298.xml'
# match = 'data/world-cup_7254.xml'
# match = 'data/world-cup_7269.xml'
# match = 'data/world-cup_7250.xml'

report = SquawkaReport(match)

goals_attempts = pd.DataFrame(report.goals_attempts)
players = pd.DataFrame(report.players)
teams = pd.DataFrame(report.teams)
setpieces = pd.DataFrame(report.setpieces)
subs = pd.DataFrame(report.swap_players)
cards = pd.DataFrame(report.cards)
takeons = pd.DataFrame(report.takeons)

# Teams
teams_id = list(teams['id'].get_values())
team_a = 'team_{0}'.format(teams_id[0])
team_b = 'team_{0}'.format(teams_id[1])
team_list = [(teams_id[0], team_a), (teams_id[1], team_b)]
teams = teams[['id', 'state']]
teams = teams.rename(columns={'id': 'team_id'})

for team, col_name in team_list:
    temp = [
        (goals_attempts['type'].values == 'goal') & (
            goals_attempts['team_id'].values ==
            team)]
    goals_attempts[col_name] = temp[0].astype(int)
    cumsum = goals_attempts[col_name].cumsum()
    col_name_state = '{0}_goals'.format(col_name)
    goals_attempts[col_name_state] = cumsum
    temp_shots = [goals_attempts['team_id'].values == team]
    goals_attempts[col_name] = temp_shots[0].astype(int)
    cumsum_shots = goals_attempts[col_name].cumsum()
    col_name_shots = '{0}_shots'.format(col_name)
    goals_attempts[col_name_shots] = cumsum_shots


def goals_for(df):
    if df['team_id'] == teams_id[0]:
        col_name_state = '{0}_goals'.format(team_a)
    else:
        col_name_state = '{0}_goals'.format(team_b)
    return df[col_name_state]


def goals_against(df):
    if df['team_id'] == teams_id[0]:
        col_name_state = '{0}_goals'.format(team_b)
    else:
        col_name_state = '{0}_goals'.format(team_a)
    return df[col_name_state]


def team_shot_number(df):
    if df['team_id'] == teams_id[0]:
        col_name_shots = '{0}_shots'.format(team_a)
    else:
        col_name_shots = '{0}_shots'.format(team_b)
    return df[col_name_shots]


def is_own(string):
    if string == 'yes':
        return 1
    else:
        return 0
goals_attempts['goals_for'] = goals_attempts.apply(goals_for, axis=1)
goals_attempts['goals_against'] = goals_attempts.apply(goals_against, axis=1)
goals_attempts['team_shot_number'] = goals_attempts.apply(
    team_shot_number, axis=1)
if 'is_own' in goals_attempts.columns:
    goals_attempts['is_own'] = goals_attempts['is_own'].apply(is_own)
else:
    goals_attempts['is_own'] = [0] * goals_attempts.shape[0]

if setpieces.empty:
    goals_attempts['sp_type'] = [0] * goals_attempts.shape[0]
else:
    setpieces = setpieces[['minsec', 'player_id', 'type']]
    setpieces = setpieces.rename(columns={'type': 'sp_type'})
    goals_attempts = pd.merge(
        goals_attempts, setpieces, how='left', on=[
            'minsec', 'player_id']).fillna(0)


def shot_type(df):
    if df['sp_type'] == 'penalty':
        return 'penalty'
    # elif df['sp_type'] == 'direct':
        # return 'free_kick'
    else:
        if df['headed'] == 'true':
            return 'headed'
        else:
            return 'shot'


def get_vertical_coord(coord):
    comma_index = coord.index(',')
    vert_coord = float(coord[: comma_index])
    return vert_coord


def get_horizontal_coord(coord):
    comma_index = coord.index(',')
    hor_coord = float(coord[comma_index + 1:])
    return hor_coord

goals_attempts['minsec'] = goals_attempts['minsec'].astype(int)
goals_attempts['vert_coord'] = goals_attempts['end'].apply(get_vertical_coord)
goals_attempts['hor_coord'] = goals_attempts['end'].apply(get_horizontal_coord)
goals_attempts['shot_type'] = goals_attempts.apply(shot_type, axis=1)
goals_attempts['injurytime_play'] = goals_attempts[
    'injurytime_play'].fillna(0).astype(int)

shot_col_list = ['assist_1',
                 'minsec',
                 'injurytime_play',
                 'player_id',
                 'team_id',
                 'goals_for',
                 'goals_against',
                 'team_shot_number',
                 'is_own',
                 'shot_type',
                 'vert_coord',
                 'hor_coord']

goals_attempts = goals_attempts[shot_col_list]
# Get time played
xml_file = match
file = open(xml_file, 'r')
soup = BeautifulSoup(file, 'xml')
inj_time = soup.find('time_slice', {"name": "85 - 90"})['itp_mins']
game_time = int(inj_time) + 90
# print(time_played)

# Subs


def times(state):
    if state == 'playing':
        return game_time
    else:
        return 0

players['played_raw'] = players['state'].apply(times)
subs['min'] = subs['min'].astype(int)
subs_in = subs[['min', 'sub_to_player', 'team_id']]
subs_in = subs_in.rename(
    columns={'sub_to_player': 'last_name'})
# print(subs_in)
subs_out = subs[['min', 'player_to_sub', 'team_id']]
subs_out = subs_out.rename(
    columns={'player_to_sub': 'last_name'})
# print(subs_out)
subs_list = [subs_in, subs_out]
subs = pd.concat(subs_list, join='outer')
subs['min'] = game_time - subs['min']
players = pd.merge(players, subs, how='left', on=['team_id',
                                                  'last_name']).fillna(0)
# Red Cards
if cards.empty:
    players['time_not_played_card'] = [0] * players.shape[0]
else:
    cards = cards[cards['card'] == 'red']
    if cards.empty:
        players['time_not_played_card'] = [0] * players.shape[0]
    else:
        cards['mins'] = cards['mins'].astype(int)
        cards['time_not_played_card'] = game_time - cards['mins']
        cards = cards.rename(
            columns={'team': 'team_id', 'player_id': 'id'})
        players = pd.merge(players, cards, how='left', on=['team_id',
                                                           'id']).fillna(0)

# Calculate time played
players['time_played_temp'] = players['min'] - players['played_raw']
players['time_played_temp'] = players['time_played_temp'].abs()
players['time_played'] = players['time_played_temp'] - \
    players['time_not_played_card']

players = players.rename(columns={'id': 'player_id'})
players_col_list = ['player_id',
                    'age',
                    'country',
                    'first_name',
                    'last_name',
                    'surname',
                    'position',
                    'height',
                    'weight',
                    'state',
                    'team_name',
                    'time_played']

players = players[players_col_list]

shots = pd.merge(goals_attempts, players, how='left', on='player_id')

# Takeons
takeons['minsec_takeon'] = takeons['minsec'].astype(int)

# takeons = takeons[takeons['type'] == 'Success']
takeons = takeons[['minsec_takeon',
                   'player_id',
                   'team_id']]

# for i in range(1, 6):
# col_name = 'minsec_minus_{0}'.format(i)
# takeons[col_name] = takeons['minsec_original'] - i

# shots = pd.merge(shots, takeons, how='left', on=['player_id',
# 'team_id']).fillna(0)


# def allocate_takeons(df):
# if (df['minsec_takeon'] >= df['minsec'] - 5) & (df['minsec_takeon'] <=
# df['minsec']):
# return 1
# else:
# return 0
# shots['takeon'] = shots.apply(allocate_takeons, axis=1)
# col_list = list(set(players_col_list + shot_col_list))
# shots = shots.groupby([col_list]).sum()
# print(shots.columns)
# print(shots[['minsec', 'player_id']])
print(shots[shots['minsec'] == 5430])
