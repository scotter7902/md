import pandas as pd
import numpy as np
import sklearn
import sklearn.ensemble
import sklearn.feature_selection
import sklearn.model_selection
import pickle
import joblib

if __name__ == '__main__':
    # read data.csv
    data = pd.read_csv('data.csv', sep=',')

    # dataset
    X = data.drop(['legitimate'], axis=1).values
    y = data['legitimate'].values
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, random_state=1, test_size=.2)

    # feature selection
    fsel = sklearn.ensemble.ExtraTreesClassifier().fit(X, y)
    model = sklearn.feature_selection.SelectFromModel(fsel, prefit=True)
    X_new = model.transform(X)
    nb_features = X_new.shape[1]
    indices = np.argsort(fsel.feature_importances_)[::-1][:nb_features]
    for f in range(nb_features):
        print("%d. feature %s (%f)" % (f + 1, data.columns[indices[f]], fsel.feature_importances_[indices[f]]))

    # training
    algorithms = {
        "DecisionTree": sklearn.tree.DecisionTreeClassifier(max_depth=10),
        "RandomForest": sklearn.ensemble.RandomForestClassifier(n_estimators=50),
        "GradientBoosting": sklearn.ensemble.GradientBoostingClassifier(n_estimators=50),
        "AdaBoost": sklearn.ensemble.AdaBoostClassifier(n_estimators=100),
        }

    # testing
    results = {}

    # result
    print("\nNow testing algorithms")
    for algo in algorithms:
        clf = algorithms[algo]
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
        print("%s : %f %%" % (algo, score*100))
        results[algo] = score
    winner = max(results, key=results.get)
    print('\nWinner algorithm is %s with a %f %% success' % (winner, results[winner]*100))

    features = []
    for f in sorted(np.argsort(fsel.feature_importances_)[::-1][:nb_features]):
        features.append(data.columns[f])
    # Save the algorithm and the feature list for later predictions
    print('Saving algorithm and feature list in classifier directory...')
    joblib.dump(algorithms[winner], 'classifier.pkl')
    open('features.pkl', 'wb+').write(pickle.dumps(features))
    print('Saved')