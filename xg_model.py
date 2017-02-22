# =============================================================================
#          File: xg_model.py
#        Author: Andre Brener
#       Created: 14 Oct 2016
# Last Modified: 17 Nov 2016
#   Description: description
# =============================================================================
import pickle

import numpy as np
import pandas as pd

from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.cross_validation import train_test_split

path = 'shots_database/train_table_processed.csv'

total_data = pd.read_csv(path)

# train_table = total_data.sample(frac=0.4)
train_table = total_data.copy()

# print(train_table.head())


def get_table(train_table):
    x_cols = []
    for col in train_table.columns:
        # print(data[col].value_counts())
        if col not in ['result', 'team_name', 'competition', 'season_x',
                       'surname']:
            train_table[col] = train_table[col].astype(str)
            x_cols.append(col)

    # print(x_cols)

    X = pd.get_dummies(train_table[x_cols])
    y = train_table['result']

    print(train_table.shape)
    print(X.shape)
    print(y.shape)

    return X, y

X, y = get_table(train_table)

# X.to_csv('/Users/andre/Desktop/x_train.csv')

multin_parameters = {'alpha': 10 **
                     (-1.00 * np.arange(-4, 4)), 'fit_prior': [True, False]}
forest_parameters = {'n_estimators': [150, 200, 250, 300],
                     'max_features': ["auto", 20, 25, 30],
                     "bootstrap": [True, False],
                     "min_samples_leaf": [1, 3, 5],
                     'max_depth': [5, 10, 15]}
SVR_parameters = {'C': [0.5, 0.6, 0.7, 1.0]}
grad_parameters = {'n_estimators': [100, 150, 200],
                   'max_depth': [3, 10],
                   'max_depth': [5, 10],
                   "max_features": [None, 1, 5],
                   "max_leaf_nodes": [None, 5],
                   "warm_start": [True, False]
                   }

models = {
    # 'MultinomialNB': (MultinomialNB(), multin_parameters),
    'RandomForestRegressor': (RandomForestRegressor(), forest_parameters),
    # 'GradientBoostingRegressor': (GradientBoostingRegressor(), grad_parameters),
    # 'SVR': (SVR(), SVR_parameters)
}


def pick_best_model_parameters(model, parameters, X_train, y_train):
    clf = GridSearchCV(model, parameters, cv=4, n_jobs=-1)
    clf.fit(X_train, y_train)
    print(clf.best_params_)
    return clf.best_estimator_

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0)

l = []

for model in models:
    print('\nTraining Model', model)
    (clf, parameters) = models[model]
    l.append(
        (model,
         pick_best_model_parameters(
             clf,
             parameters,
             X_train,
             y_train)))

for (model, clf) in l:
    y_pred = clf.predict(X_test)
    print('\n', model, mean_squared_error(y_test, y_pred))
    # for i in range (y_test.size):
    #    print (y_test.values[i], '-', int(y_pred[i]))


with open('random_forest.pkl', 'wb') as f:
    pickle.dump(l[0][1], f)
