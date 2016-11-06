# =============================================================================
#          File: dataset.py
#        Author: Andre Brener
#       Created: 11 Sep 2016
# Last Modified: 15 Oct 2016
#   Description: description
# =============================================================================
from math import sqrt
from datetime import datetime, timedelta

import pandas as pd

from bs4 import BeautifulSoup
from utils import SquawkaReport


def get_dataset(match):

    def get_competition(match):
        if 'premier_league' in match:
            return 'epl'
        elif 'serie_a' in match:
            return 'serie_a'
        elif 'bundesliga' in match:
            return 'bundesliga'
        elif 'la_liga' in match:
            return 'la_liga'
        elif 'ligue1' in match:
            return 'ligue1'
        elif 'mls' in match:
            return 'mls'
        elif 'eredivisie' in match:
            return 'eredivisie'
        elif 'brasileirao' in match:
            return 'brasileirao'
        elif 'world_cup' in match:
            return 'world_cup'

    competition = get_competition(match)

    report = SquawkaReport(match)

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

    if teams.empty:
        empty_match = pd.DataFrame()
        empty_players = pd.DataFrame()
        return empty_match, empty_players

    # Functions

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

    # Teams
    teams_id = list(teams['id'].get_values())
    team_a = 'team_{0}'.format(teams_id[0])
    team_b = 'team_{0}'.format(teams_id[1])
    team_list = [(teams_id[0], team_a), (teams_id[1], team_b)]
    teams = teams[['id', 'state']]
    teams = teams.rename(columns={'id': 'team_id'})

    # Clearences
    if 'mins' not in clearances.columns:
        empty_match = pd.DataFrame()
        empty_players = pd.DataFrame()
        return empty_match, empty_players

    if 'minsec' not in clearances.columns:
        clearances['mins'] = clearances['mins'].astype(int)
        clearances['secs'] = clearances['secs'].astype(int)
        clearances['minsec'] = 60 * clearances['mins'] + clearances['secs']

    clearances['action_type'] = ['clearance'] * clearances.shape[0]
    clearances['vert_coord'] = clearances['loc'].apply(get_vertical_coord)
    clearances['hor_coord'] = clearances['loc'].apply(get_horizontal_coord)
    clearances['minsec'] = clearances['minsec'].astype(int)

    clearances = clearances[['action_type',
                             'hor_coord',
                             'vert_coord',
                             'minsec',
                             'mins',
                             'secs',
                             'team_id',
                             'player_id']]
    # print(clearances)

    # Passes

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

    include_variable(passes, 'through_ball')
    include_variable(passes, 'long_ball')
    include_variable(passes, 'throw_ins')

    if 'assists' not in passes.columns:
        passes['assists'] = [0] * passes.shape[0]

    if 'minsec' not in passes.columns:
        passes['mins'] = passes['mins'].astype(int)
        passes['secs'] = passes['secs'].astype(int)
        passes['minsec'] = 60 * passes['mins'] + passes['secs']

    passes = passes.drop_duplicates(
        ['action_type', 'minsec', 'mins', 'secs', 'player_id', 'team_id',
            'type', 'start', 'end'])
    passes['end_vert_coord'] = passes['end'].apply(get_vertical_coord)
    passes['end_hor_coord'] = passes['end'].apply(get_horizontal_coord)
    passes['start_vert_coord'] = passes['start'].apply(get_vertical_coord)
    passes['start_hor_coord'] = passes['start'].apply(get_horizontal_coord)
    passes['distance'] = passes.apply(get_distance, axis=1)
    passes['temp_pass_type'] = passes.apply(assist_type, axis=1)
    passes['assists'] = passes['assists'].apply(transform_true)
    passes['minsec'] = passes['minsec'].astype(int)
    passes['action_type'] = ['pass'] * passes.shape[0]
    passes = passes.rename(
        columns={'type': 'result'})

    cons_passes_cols = []
    passes_col_names = []
    for team, col_name in team_list:
        temp_pass = [(passes['team_id'].values == team) &
                     (passes['result'] == 'completed')]
        name = 'is_pass_complete_{0}'.format(col_name)
        passes[name] = temp_pass[0].astype(int)
        passes_col_names.append(name)

        cons_passes_name = 'consec_passes_{0}'.format(col_name)
        cons_passes_cols.append(cons_passes_name)
    passes = passes[['action_type',
                     'start_hor_coord',
                     'start_vert_coord',
                     'end_hor_coord',
                     'end_vert_coord',
                     'distance',
                     'minsec',
                     'mins',
                     'secs',
                     'team_id',
                     'player_id',
                     'temp_pass_type',
                     'result',
                     'assists',
                     passes_col_names[0],
                     passes_col_names[1]]]

    # print(passes)
# print(passes[passes['assists'] == 1])

# print(passes['minsec'].value_counts())
# Crosses

    def if_corner(df):
        if df['start_vert_coord'] > 99 and df['start_hor_coord'] > 99:
            return 'left_corner'
        elif df['start_vert_coord'] > 99 and df['start_hor_coord'] < 1:
            return 'right_corner'
        else:
            return 'cross'

    def get_assist(string):
        if string == 'Assist':
            return 1
        else:
            return 0

    def cross_result(string):
        if string == 'Assist' or string == 'Completed':
            return 'completed'
        else:
            return 'failed'

    if 'minsec' not in crosses.columns:
        crosses['mins'] = crosses['mins'].astype(int)
        crosses['secs'] = crosses['secs'].astype(int)
        crosses['minsec'] = 60 * crosses['mins'] + crosses['secs']

    crosses = crosses.drop_duplicates(
        ['minsec', 'mins', 'secs', 'player_id', 'team',
         'type', 'start', 'end'])

    crosses['end_vert_coord'] = crosses['end'].apply(get_vertical_coord)
    crosses['end_hor_coord'] = crosses['end'].apply(get_horizontal_coord)
    crosses['start_vert_coord'] = crosses['start'].apply(get_vertical_coord)
    crosses['start_hor_coord'] = crosses['start'].apply(get_horizontal_coord)
    crosses['distance'] = crosses.apply(get_distance, axis=1)
    crosses['temp_pass_type'] = crosses.apply(if_corner, axis=1)
    crosses['result'] = crosses['type'].apply(cross_result)
    crosses['assists'] = crosses['type'].apply(get_assist)
    crosses['minsec'] = crosses['minsec'].astype(int)
    crosses['action_type'] = ['pass'] * crosses.shape[0]
    crosses = crosses.rename(columns={'team': 'team_id'})

    crosses_col_names = []
    for team, col_name in team_list:
        temp_cross = [(crosses['team_id'].values == team) &
                      (crosses['result'] == 'completed') &
                      (crosses['temp_pass_type'] == 'cross')]
        name = 'is_pass_complete_{0}'.format(col_name)
        crosses[name] = temp_cross[0].astype(int)
        crosses_col_names.append(name)

    crosses = crosses[['action_type',
                       'start_hor_coord',
                       'start_vert_coord',
                       'end_hor_coord',
                       'end_vert_coord',
                       'distance',
                       'minsec',
                       'mins',
                       'secs',
                       'team_id',
                       'player_id',
                       'temp_pass_type',
                       'result',
                       'assists',
                       crosses_col_names[0],
                       crosses_col_names[1]]]

    # print(crosses)

    # Shots

    if 'minsec' not in goals_attempts.columns:
        goals_attempts['mins'] = goals_attempts['mins'].astype(int)
        goals_attempts['secs'] = goals_attempts['secs'].astype(int)
        goals_attempts['minsec'] = 60 * \
            goals_attempts['mins'] + goals_attempts['secs']

    goals_attempts = goals_attempts.drop_duplicates(
        ['action_type', 'minsec', 'mins', 'secs', 'player_id', 'team_id',
            'type', 'start', 'end'])

    for team, col_name in team_list:
        temp_shots = [goals_attempts['team_id'].values == team]
        goals_attempts[col_name] = temp_shots[0].astype(int)
        cumsum_shots = goals_attempts[col_name].cumsum()
        col_name_shots = '{0}_shots'.format(col_name)
        goals_attempts[col_name_shots] = cumsum_shots

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

    goals_attempts['team_shot_number'] = goals_attempts.apply(
        team_shot_number, axis=1)
    if 'is_own' in goals_attempts.columns:
        goals_attempts['is_own'] = goals_attempts['is_own'].apply(is_own)
    else:
        goals_attempts['is_own'] = [0] * goals_attempts.shape[0]

    def temp_shot_type(df):
        if df['headed'] == 'true':
            return 'headed'
        else:
            return 'shot'

    def is_rebound(df):
        if df['minsec'] - df['minsec_last_shot'] < 6:
            return 1

    include_variable(goals_attempts, 'injurytime_play')
    if 'headed' not in goals_attempts.columns:
        goals_attempts['headed'] = [False] * goals_attempts.shape[0]
    goals_attempts['minsec'] = goals_attempts['minsec'].astype(int)
    goals_attempts = goals_attempts.sort_values('minsec', ascending=True)
    goals_attempts['vert_coord'] = goals_attempts[
        'end'].apply(get_vertical_coord)
    goals_attempts['hor_coord'] = goals_attempts[
        'end'].apply(get_horizontal_coord)
    goals_attempts['temp_shot_type'] = goals_attempts.apply(
        temp_shot_type, axis=1)
    goals_attempts['minsec_last_shot'] = goals_attempts['minsec'].shift()
    goals_attempts['is_rebound'] = goals_attempts.apply(is_rebound, axis=1)
    goals_attempts['injurytime_play'] = goals_attempts[
        'injurytime_play'].fillna(0).astype(int)
    goals_attempts['action_type'] = ['shot'] * goals_attempts.shape[0]
    goals_attempts = goals_attempts.rename(columns={'type': 'result'})

    shot_col_list = ['action_type',
                     'minsec',
                     'mins',
                     'secs',
                     'injurytime_play',
                     'player_id',
                     'team_id',
                     'team_shot_number',
                     'is_own',
                     'temp_shot_type',
                     'vert_coord',
                     'hor_coord',
                     'is_rebound',
                     'result']

    goals_attempts = goals_attempts[shot_col_list]
    # print(goals_attempts)

    # Takeons

    if 'minsec' not in takeons.columns:
        takeons['mins'] = takeons['mins'].astype(int)
        takeons['secs'] = takeons['secs'].astype(int)
        takeons['minsec'] = 60 * takeons['mins'] + takeons['secs']

    takeons['minsec'] = takeons['minsec'].astype(int)
    takeons = takeons.rename(
        columns={'type': 'result'})
    takeons['vert_coord'] = takeons['loc'].apply(get_vertical_coord)
    takeons['hor_coord'] = takeons['loc'].apply(get_horizontal_coord)
    takeons['action_type'] = ['dribble'] * takeons.shape[0]
    takeons = takeons[['action_type',
                       'minsec',
                       'mins',
                       'secs',
                       'vert_coord',
                       'hor_coord',
                       'player_id',
                       'team_id',
                       'other_player',
                       'other_team',
                       'result']]

    # print(takeons)

    # Goal Keeping

    if 'mins' not in goal_keeping.columns or 'secs' not in goal_keeping.columns:
        goal_keeping = pd.DataFrame()
    else:
        if 'minsec' not in goal_keeping.columns:
            goal_keeping['mins'] = goal_keeping['mins'].astype(int)
            goal_keeping['secs'] = goal_keeping['secs'].astype(int)
            goal_keeping['minsec'] = 60 * \
                goal_keeping['mins'] + goal_keeping['secs']

        goal_keeping['minsec'] = goal_keeping['minsec'].astype(int)
        goal_keeping['action_type'] = ['goal_keeping'] * goal_keeping.shape[0]
        goal_keeping = goal_keeping.rename(
            columns={'type': 'result'})

        goal_keeping = goal_keeping[['action_type',
                                     'minsec',
                                     'mins',
                                     'secs',
                                     'player_id',
                                     'team_id',
                                     'result']]
    # print(goal_keeping)

    # Tackles

    def result_change(string):
        if string == 'Success':
            return 'Successful'
        else:
            return 'Unsuccessful'

    # print(tackles.columns)
    tackles = tackles.drop_duplicates(
        ['action_type', 'mins', 'secs', 'player_id', 'team',
            'type', 'loc', 'tackler'])

    tackles['mins'] = tackles['mins'].astype(int)
    tackles['secs'] = tackles['secs'].astype(int)
    tackles['minsec'] = 60 * tackles['mins'] + tackles['secs']
    tackles['vert_coord'] = tackles['loc'].apply(get_vertical_coord)
    tackles['hor_coord'] = tackles['loc'].apply(get_horizontal_coord)
    tackles['action_type'] = ['tackle'] * tackles.shape[0]
    tackles['result'] = tackles['type'].apply(result_change)
    tackles = tackles.rename(
        columns={
            'player_id': 'other_player',
            'tackler': 'player_id',
            'tackler_team': 'team_id',
            'team': 'other_team'})

    tackles = tackles[['action_type',
                       'minsec',
                       'mins',
                       'secs',
                       'vert_coord',
                       'hor_coord',
                       'player_id',
                       'team_id',
                       'other_player',
                       'other_team',
                       'result']]

    # print(tackles)

    # Interceptions
    interceptions['mins'] = interceptions['mins'].astype(int)
    interceptions['secs'] = interceptions['secs'].astype(int)
    interceptions['minsec'] = 60 * \
        interceptions['mins'] + interceptions['secs']
    interceptions['vert_coord'] = interceptions[
        'loc'].apply(get_vertical_coord)
    interceptions['hor_coord'] = interceptions[
        'loc'].apply(get_horizontal_coord)
    interceptions['action_type'] = ['interception'] * interceptions.shape[0]

    interceptions = interceptions[['action_type',
                                   'minsec',
                                   'mins',
                                   'secs',
                                   'vert_coord',
                                   'hor_coord',
                                   'player_id',
                                   'team_id']]

    # print(interceptions)

    # Fouls
    include_variable(fouls, 'injurytime_play')
    fouls['mins'] = fouls['mins'].astype(int)
    fouls['secs'] = fouls['secs'].astype(int)
    fouls['minsec'] = 60 * fouls['mins'] + fouls['secs']

    fouls['minsec'] = fouls['minsec'].astype(int)
    fouls['vert_coord'] = fouls['loc'].apply(get_vertical_coord)
    fouls['hor_coord'] = fouls['loc'].apply(get_horizontal_coord)
    fouls = fouls.rename(
        columns={
            'type': 'action_type',
            'team': 'team_id'})

    fouls = fouls[['action_type',
                   'minsec',
                   'mins',
                   'secs',
                   'injurytime_play',
                   'vert_coord',
                   'hor_coord',
                   'player_id',
                   'team_id']]

    # print(fouls)
    # Cards
    if not cards.empty:
        cards['mins'] = cards['mins'].astype(int)
        cards['secs'] = cards['secs'].astype(int)
        cards['minsec'] = 60 * cards['mins'] + cards['secs']
        cards['minsec'] = cards['minsec'].astype(int)
        cards['vert_coord'] = cards['loc'].apply(get_vertical_coord)
        cards['hor_coord'] = cards['loc'].apply(get_horizontal_coord)
        cards['action_type'] = ['card'] * cards.shape[0]
        cards = cards.rename(
            columns={
                'card': 'result',
                'team': 'team_id'})

        cards = cards[['action_type',
                       'minsec',
                       'mins',
                       'secs',
                       'vert_coord',
                       'hor_coord',
                       'player_id',
                       'team_id',
                       'result']]

    # print(cards)
    # Concatenate all stats
    stats_list = [
        clearances,
        passes,
        crosses,
        goals_attempts,
        cards,
        takeons,
        goal_keeping,
        tackles,
        interceptions,
        fouls]
    match_stats = pd.concat(stats_list)
    match_stats = match_stats.sort_values('minsec', ascending=True)
    match_stats[crosses_col_names[0]].fillna(0)
    match_stats[crosses_col_names[1]].fillna(0)
    match_stats['assists'] = match_stats['assists'].fillna(0).astype(int)

    # print(match_stats['minsec'].value_counts())
    # Continuous Passes

    def assign_cons_passes(df):
        if df['team_id'] == teams_id[0]:
            team_cons_passes = cons_passes_cols[0]
        else:
            team_cons_passes = cons_passes_cols[1]
        return df[team_cons_passes]

    copy_df = match_stats[match_stats['action_type'] != 'dribble'].copy()

    y1 = copy_df[crosses_col_names[0]]
    y2 = copy_df[crosses_col_names[1]]
    copy_df[cons_passes_cols[0]] = y1 * \
        (y1.groupby((y1 != y1.shift()).cumsum()).cumcount() + 1)
    copy_df[cons_passes_cols[1]] = y2 * \
        (y2.groupby((y2 != y2.shift()).cumsum()).cumcount() + 1)

    copy_df['consecutive_passes'] = copy_df.apply(assign_cons_passes, axis=1)
    match_stats_cols = list(match_stats.columns)
    copy_df_cols = match_stats_cols + ['consecutive_passes']
    copy_df = copy_df[copy_df_cols]
    match_stats = pd.merge(
        match_stats,
        copy_df,
        how='left')

    for col in crosses_col_names:
        match_stats = match_stats.drop(col, 1)

    # print(match_stats.head(25))
    # print(match_stats[match_stats['action_type']
        # == 'pass']['consecutive_passes'])
    # Teams

    # print(match_stats['minsec'].value_counts())

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

    drop_cols = []
    for team, col_name in team_list:
        temp = [
            (match_stats['result'].values == 'goal') & (
                match_stats['team_id'].values ==
                team)]
        match_stats[col_name] = temp[0].astype(int)
        cumsum = match_stats[col_name].cumsum()
        col_name_state = '{0}_goals'.format(col_name)
        match_stats[col_name_state] = cumsum - match_stats[col_name]
        drop_cols.append(col_name)
        drop_cols.append(col_name_state)

    match_stats['goals_for'] = match_stats.apply(goals_for, axis=1)
    match_stats['goals_against'] = match_stats.apply(goals_against, axis=1)

    def field_players_team(df):
        if df['team_id'] == teams_id[0]:
            col_name_state = '{0}_red_cards'.format(team_a)
        else:
            col_name_state = '{0}_red_cards'.format(team_b)
        return df[col_name_state]

    def field_players_rival(df):
        if df['team_id'] == teams_id[0]:
            col_name_state = '{0}_red_cards'.format(team_b)
        else:
            col_name_state = '{0}_red_cards'.format(team_a)
        return df[col_name_state]

    for team, col_name in team_list:
        temp = [
            (match_stats['result'].values == 'red') & (
                match_stats['team_id'].values ==
                team)]
        col = 'card_{0}'.format(col_name)
        match_stats[col] = temp[0].astype(int)
        cumsum = match_stats[col].cumsum()
        col_name_state = '{0}_red_cards'.format(col_name)
        match_stats[col_name_state] = 11 - cumsum + match_stats[col]
        drop_cols.append(col)
        drop_cols.append(col_name_state)

    match_stats['field_players_team'] = match_stats.apply(
        field_players_team, axis=1)
    match_stats['field_players_rival'] = match_stats.apply(
        field_players_rival, axis=1)

    for col in drop_cols:
        match_stats = match_stats.drop(col, 1)
    teams = teams.rename(columns={'state': 'home_away'})
    match_stats = pd.merge(match_stats, teams, how='left', on='team_id')

    # print(match_stats[match_stats['action_type'] == 'shot'])['minsec']
    # print(match_stats['field_players_team'].value_counts())

    # Parse xml
    xml_file = match
    file = open(xml_file, 'r')
    soup = BeautifulSoup(file, 'xml')

    # Game Date
    kickoff = soup.find('kickoff').text[:25]
    game_date = datetime.strptime(kickoff, '%a, %d %b %Y %H:%M:%S').date()
    game_day = game_date.day
    game_month = game_date.month
    game_year = game_date.year

    next_year_date = game_date + timedelta(365)
    next_year = next_year_date.year
    last_year_date = game_date - timedelta(365)
    last_year = last_year_date.year

    last_season = '{0}-{1}'.format(last_year, game_year)
    next_season = '{0}-{1}'.format(game_year, next_year)

    if game_month < 6:
        current_season = last_season
    else:
        current_season = next_season

    match_stats['game_day'] = [game_day] * match_stats.shape[0]
    match_stats['game_month'] = [game_month] * match_stats.shape[0]
    match_stats['game_year'] = [game_year] * match_stats.shape[0]
    match_stats['season'] = [current_season] * match_stats.shape[0]

    # Time Played
    try:
        inj_time = soup.find('time_slice', {"name": "85 - 90"})['itp_mins']
    except (KeyError, TypeError):
        inj_time = 0

    game_time = int(inj_time) + 90

    # print(time_played)

    # Players
    # Subs

    def times(state):
        if state == 'playing':
            return game_time
        else:
            return 0

    if 'min' not in subs.columns:
        empty_match = pd.DataFrame()
        empty_players = pd.DataFrame()
        return empty_match, empty_players

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
        red_cards = cards[cards['result'] == 'red']
        if red_cards.empty:
            players['time_not_played_card'] = [0] * players.shape[0]
        else:
            red_cards['time_not_played_card'] = game_time - \
                red_cards['mins'].astype(int)
            red_cards = red_cards.rename(
                columns={'team': 'team_id', 'player_id': 'id'})
            players = pd.merge(
                players, red_cards, how='left', on=[
                    'team_id', 'id']).fillna(0)

    # Calculate time played
    players['time_played_temp'] = players['min'] - players['played_raw']
    players['time_played_temp'] = players['time_played_temp'].abs()
    players['time_played'] = players['time_played_temp'] - \
        players['time_not_played_card']

    include_variable(players, 'age')
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
                        'team_id',
                        'team_name',
                        'time_played']

    players = players[players_col_list]
    players['game_day'] = [game_day] * players.shape[0]
    players['game_month'] = [game_month] * players.shape[0]
    players['game_year'] = [game_year] * players.shape[0]
    players['season'] = [current_season] * players.shape[0]
    players['competition'] = [competition] * players.shape[0]

    # print(players)

    players_short = players[['player_id', 'surname', 'position', 'team_id']]
    players_short = players_short.rename(
        columns={
            'player_id': 'other_player',
            'team_id': 'other_team',
            'position': 'other_player_pos',
            'surname': 'other_player_sn'})

    # print(players_short)
    match_dataset = pd.merge(match_stats, players, how='left',
                             on=['player_id', 'team_id'])

    match_dataset = pd.merge(match_dataset, players_short, how='left',
                             on=['other_player', 'other_team'])

    # print(match_dataset[match_dataset['action_type'] == 'shot']['minsec'])
    match_dataset_cols = list(match_dataset.columns)
    # Get Freekicks

    def get_shot_fk(df):
        if df['action_type'] == 'shot' and df['last_incidence_type'] == 'Foul' and df[
                'team_id'] != df['last_incidence_team']:
            return 'free_kick'

    def get_pass_fk(df):
        if df['action_type'] == 'pass' and df['last_incidence_type'] == 'Foul' and df[
                'team_id'] != df['last_incidence_team']:
            return 'free_kick'

    def get_shot_dribble(df):
        if df['action_type'] == 'shot' and df['last_incidence_type'] == 'dribble' and df[
                'player_id'] == df['last_incidence_player']:
            return df['last_incidence_other_pl_pos']

    fk_df = match_dataset[~match_dataset[
        'action_type'].isin(['tackle', 'card'])].copy()
    fk_df = fk_df[fk_df['result'] != 'Failed']
    fk_df['last_incidence_type'] = fk_df['action_type'].shift()
    fk_df['last_incidence_player'] = fk_df['player_id'].shift()
    fk_df['last_incidence_team'] = fk_df['team_id'].shift()
    fk_df['last_incidence_other_pl_pos'] = fk_df['other_player_pos'].shift()
    fk_df['shot_fk'] = fk_df.apply(get_shot_fk, axis=1)
    fk_df['pass_fk'] = fk_df.apply(get_pass_fk, axis=1)
    fk_df['pos_dribbled'] = fk_df.apply(get_shot_dribble, axis=1)

    cols_list_fk = ['shot_fk', 'pass_fk', 'pos_dribbled']
    fk_df_cols = match_dataset_cols + cols_list_fk
    fk_df = fk_df[fk_df_cols]

    match_dataset = pd.merge(match_dataset, fk_df, how='left')

    def get_final_shot_type(df):
        if df['shot_fk'] == 'free_kick':
            if (df['vert_coord'] == 88.5) & (df['hor_coord']
                                             == 50.0) & (df['temp_shot_type'] == 'shot'):
                return 'penalty'
            else:
                return 'free_kick'
        else:
            return df['temp_shot_type']

    def get_final_pass_type(df):
        if df['pass_fk'] == 'free_kick':
            return 'free_kick'
        else:
            return df['temp_pass_type']

    match_dataset['shot_type'] = match_dataset.apply(
        get_final_shot_type, axis=1)
    match_dataset['pass_type'] = match_dataset.apply(
        get_final_pass_type, axis=1)
    match_dataset = match_dataset.drop(['shot_fk', 'temp_shot_type',
                                        'temp_pass_type', 'pass_fk'], 1)

    # print(match_dataset[match_dataset['action_type'] == 'pass'])
    # print(match_dataset[match_dataset['pass_type'] == 'right_corner'])

    # print(match_dataset[match_dataset['action_type'] == 'shot']['minsec'])
    # Get Tackle or Interception

    def get_shot_recovery(df):
        if df['shot_type'] == 'shot' and df['last_incidence_type'] in [
                'interception', 'tackle'] and df['player_id'] == df['last_incidence_player']:
            return df['last_incidence_other_pl_pos']

    def_df = match_dataset[~match_dataset[
        'action_type'].isin(['dribble'])].copy()
    def_df['last_incidence_type'] = def_df['action_type'].shift()
    def_df['last_incidence_player'] = def_df['player_id'].shift()
    def_df['last_incidence_team'] = def_df['team_id'].shift()
    def_df['last_incidence_other_pl_pos'] = def_df['other_player_pos'].shift()
    def_df['disp_player_pos'] = def_df.apply(get_shot_recovery, axis=1)

    match_dataset_cols = list(match_dataset.columns)
    def_df_cols = match_dataset_cols + ['disp_player_pos']
    def_df = def_df[def_df_cols]

    match_dataset = pd.merge(match_dataset, def_df, how='left')
    # print(def_df[def_df['action_type'] == 'shot'])
    # print(def_df[def_df['mins'] == '43'][['action_type', 'player_id', 'surname',
    # 'position']])

    # Link Assists

    def get_assister_id(df):
        if df['shot_type'] in ['shot', 'headed'] and df[
                'last_incidence_assist'] == 1 and df['team_id'] == df['last_incidence_team']:
            return df['last_incidence_player_id']

    def get_assist_type(df):
        if df['shot_type'] in ['shot', 'headed'] and df[
                'last_incidence_assist'] == 1 and df['team_id'] == df['last_incidence_team']:
            return df['last_inc_as_type']

    def get_assister_surname(df):
        if df['shot_type'] in ['shot', 'headed'] and df[
                'last_incidence_assist'] == 1 and df['team_id'] == df['last_incidence_team']:
            return df['last_incidence_player_surname']

    def get_assister_pos(df):
        if df['shot_type'] in ['shot', 'headed'] and df[
                'last_incidence_assist'] == 1 and df['team_id'] == df['last_incidence_team']:
            return df['last_incidence_player_pos']

    def get_as_cons_passes(df):
        if df['shot_type'] in ['shot', 'headed'] and df[
                'last_incidence_assist'] == 1 and df['team_id'] == df['last_incidence_team']:
            return df['last_inc_cons_passes']

    as_df = match_dataset[match_dataset[
        'action_type'].isin(['shot', 'pass'])].copy()
    as_df['last_incidence_assist'] = as_df['assists'].shift()
    as_df['last_incidence_player_id'] = as_df['player_id'].shift()
    as_df['last_incidence_player_surname'] = as_df['surname'].shift()
    as_df['last_incidence_player_pos'] = as_df['position'].shift()
    as_df['last_incidence_team'] = as_df['team_id'].shift()
    as_df['last_inc_as_type'] = as_df['pass_type'].shift()
    as_df['as_start_vert_coord'] = as_df['start_vert_coord'].shift()
    as_df['as_start_hor_coord'] = as_df['start_hor_coord'].shift()
    as_df['as_end_vert_coord'] = as_df['end_vert_coord'].shift()
    as_df['as_end_hor_coord'] = as_df['end_hor_coord'].shift()
    as_df['as_distance'] = as_df['distance'].shift()
    as_df['last_inc_cons_passes'] = as_df[
        'consecutive_passes'].shift()
    as_df['assister_id'] = as_df.apply(get_assister_id, axis=1)
    as_df['assister_surname'] = as_df.apply(get_assister_surname, axis=1)
    as_df['assister_position'] = as_df.apply(get_assister_pos, axis=1)
    as_df['as_consecutive_passes'] = as_df.apply(get_as_cons_passes, axis=1)
    as_df['assist_type'] = as_df.apply(get_assist_type, axis=1)

    match_dataset_cols = list(match_dataset.columns)
    as_df_cols = [
        'assist_type',
        'as_start_vert_coord',
        'as_start_hor_coord',
        'as_end_hor_coord',
        'as_end_vert_coord',
        'as_distance',
        'assister_id',
        'assister_surname',
        'assister_position',
        'as_consecutive_passes']

    def_as_cols = match_dataset_cols + as_df_cols
    as_df = as_df[def_as_cols]

    # print(as_df.head(60))

    # print(as_df[as_df['action_type'] == 'shot'])
    match_dataset = pd.merge(match_dataset, as_df, how='left')

    # print(match_dataset[match_dataset['action_type'] == 'shot'])
    # print(match_dataset[match_dataset['action_type'] ==
    # 'shot']['as_consecutive_passes'])
    time_df = match_dataset[(match_dataset['result'] != 'Unsuccessful') & (
        match_dataset['action_type'] != 'goal_keeping')].copy()

    time_teams = time_df['team_id'].tolist()
    time_minsec = time_df['minsec'].tolist()

    def function(teams, minutes, i):
        if teams[i] != teams[i - 1]:
            return minutes[i - 1]
        else:
            return function(teams, minutes, i - 1)

    def time_from_last_incidence(df):
        subtraction = df['minsec'] - df['time_before']
        if subtraction > 0:
            return subtraction
        else:
            return 0

    time_last_team_list = [0]
    try:
        for i in range(1, len(time_teams)):
            value = function(time_teams, time_minsec, i)
            time_last_team_list.append(value)
    except RuntimeError:
        empty_match = pd.DataFrame()
        empty_players = pd.DataFrame()
        return empty_match, empty_players

    time_df['time_before'] = time_last_team_list
    time_df['time_from_rival_last_inc'] = time_df.apply(
        time_from_last_incidence, axis=1)

    match_dataset_cols = list(match_dataset.columns)
    time_df_cols = match_dataset_cols + ['time_from_rival_last_inc']
    time_df = time_df[time_df_cols]

    match_dataset = pd.merge(match_dataset, time_df, how='left')

    return match_dataset, players

# match = 'data/ligue1/season_2012_2013/ligue1_687.xml'

# get_dataset(match)
