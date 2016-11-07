# =============================================================================
#          File: xg_validation.py
#        Author: Andre Brener
#       Created: 27 Oct 2016
# Last Modified: 06 Nov 2016
#   Description: description
# =============================================================================
import pickle

import pandas as pd

from sklearn.metrics import mean_squared_error

path = 'shots_database/test_table_processed.csv'

total_data = pd.read_csv(path)

# train_table = total_data.sample(frac=0.2)

test_table = total_data.copy()

# print(test_table.head())

x_cols = []
for col in test_table.columns:
    # print(data[col].value_counts())
    if col not in ['result', 'team_name', 'season_x', 'competition']:
        test_table[col] = test_table[col].astype(str)
        x_cols.append(col)

# print(x_cols)

X = pd.get_dummies(test_table[x_cols])
y = test_table['result']

# X.to_csv('/Users/andre/Desktop/x_test.csv')
print(test_table.shape)
print(X.shape)
print(y.shape)


with open('random_forest.pkl', 'rb') as f:
    clf = pickle.load(f)

# print(clf)
y_pred = clf.predict(X)
print('\n', clf, mean_squared_error(y, y_pred))

# print(y_pred)
test_table['xg'] = y_pred

# print(test_table.head())

diff_table = test_table[['team_name', 'result', 'xg']]
diff_table = diff_table.groupby('team_name').sum()
diff_table['xg'] = diff_table['xg'].round(2)

diff_table['difference'] = (diff_table['xg'] - diff_table['result']).round(2)
diff_table.reset_index(inplace=True)

# test = diff_table.sort_values('result', ascending=True)
# print(test.head(10))
# print(diff_table.sample(20))

diff_table.to_csv('season_2015-16_xg.csv', index=False)
