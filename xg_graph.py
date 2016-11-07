# =============================================================================
#          File: xg_graph.py
#        Author: Andre Brener
#       Created: 06 Nov 2016
# Last Modified: 06 Nov 2016
#   Description: description
# =============================================================================
import seaborn

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

path = 'season_2015-16_xg.csv'

data = pd.read_csv(path)

data = data[data['result'] > 5]

# print(data.sort_values('difference', ascending=False).head(70))

name_teams = [
    'R Madrid',
    'Barcelona',
    'PSG',
    'Roma',
    'Dortmund',
    'Arsenal',
    'Werder',
    "M'gladbach",
    'Villarreal',
    'Espanyol',
    'Sevilla']

name_teams_df = data[data['team_name'].isin(name_teams)]
# print(name_teams_df)
name_teams_goals = name_teams_df['result']
name_teams_xg = name_teams_df['xg']

other_teams_df = data[~data['team_name'].isin(name_teams)]
# print(other_teams_df.head(10))
other_teams_names = other_teams_df['team_name']
other_teams_goals = other_teams_df['result']
other_teams_xg = other_teams_df['xg']

fig, ax = plt.subplots()
plt.style.use('fivethirtyeight')
ax.text(3, 107, 'Goles vs Goles Esperados',
        color='0.1', fontsize=22, horizontalalignment='left', weight='bold')
ax.text(3, 102, 'Top 5 de Ligas europeas: Temporada 2015-2016',
        horizontalalignment='left', color='0.4', fontsize=16)
x = np.linspace(13, 90)
ax.scatter(name_teams_goals, name_teams_xg, s=90, color='deepskyblue',
           alpha=0.7)
ax.scatter(other_teams_goals, other_teams_xg, s=90, color='deepskyblue',
           alpha=0.7)
ax.plot(x, x, color='orangered', linewidth=2)
ax.tick_params(axis='both', labelsize=14, colors='0.4')
ax.spines['bottom'].set_visible(True)
ax.spines['bottom'].set_color('0.1')
for team in name_teams:
    va = 'top'
    ha = 'center'
    x_adjust = 0
    y_adjust = - 1.5
    if team in ['Werder', 'Sevilla', 'Arsenal']:
        va = 'bottom'
        y_adjust = 1.5
    elif team == 'Espanyol':
        va = 'bottom'
        y_adjust = 1.5
        x_adjust = - 3
    goals = name_teams_df[name_teams_df['team_name'] == team]['result'].iat[0]
    xg = name_teams_df[name_teams_df['team_name'] == team]['xg'].iat[0]
    ax.annotate(
        team,
        xy=(goals, xg),
        xytext=(goals + x_adjust, xg + y_adjust),
        va=va,
        ha=ha,
        size=14,
        color='0.4')


plt.xlabel('Goles a favor', fontsize=16, color='0.4')
plt.ylabel('Goles Esperados', fontsize=16, color='0.4')
plt.show()
