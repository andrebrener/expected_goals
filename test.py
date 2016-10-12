import pandas as pd

from squawka.utils import SquawkaReport

report = SquawkaReport('data/world-cup_7247.xml')
# report = SquawkaReport('data/world-cup_7251.xml')
# report = SquawkaReport('data/world-cup_7254.xml')
# report = SquawkaReport('data/world-cup_7269.xml')
goals_attempts = pd.DataFrame(report.goals_attempts)
players = pd.DataFrame(report.players)
teams = pd.DataFrame(report.teams)
setpieces = pd.DataFrame(report.setpieces)

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
    elif df['sp_type'] == 'direct':
        return 'free_kick'
    else:
        if df['headed'] == 'true':
            return 'headed'
        else:
            return 'shot'


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


def get_vertical_coord(coord):
    comma_index = coord.index(',')
    vert_coord = float(coord[: comma_index])
    return vert_coord


def get_horizontal_coord(coord):
    comma_index = coord.index(',')
    hor_coord = float(coord[comma_index + 1:])
    return hor_coord


goals_attempts['vert_coord'] = goals_attempts['end'].apply(get_vertical_coord)
goals_attempts['hor_coord'] = goals_attempts['end'].apply(get_horizontal_coord)
goals_attempts['hor_pos'] = goals_attempts['hor_coord'].apply(horizontal_split)
goals_attempts['ver_pos'] = goals_attempts['vert_coord'].apply(vertical_split)
goals_attempts['time_range'] = goals_attempts[
    'minsec'].astype(int).apply(time_ranges)
goals_attempts['shot_type'] = goals_attempts.apply(shot_type, axis=1)


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

players = players[['id', 'age', 'country',
                   'first_name', 'last_name', 'surname', 'position', 'height',
                   'weight', 'state', 'team_name']]
players = players.rename(columns={'id': 'player_id'})
players_info = pd.DataFrame()
players_info['age'] = players['age'].astype(int).apply(age_range)
players_info['height'] = players['height'].astype(int).apply(height_range)
players_info['player_status'] = players['state']
players_info['weight'] = players['weight'].astype(int).apply(weight_range)
players_info['position'] = players['position']
players_info['player_id'] = players['player_id']

data = pd.merge(goals_attempts, players, how='left', on='player_id')
# data = pd.merge(data, teams, how='left', on='team_id')
print(data.columns)
print(data.head())
