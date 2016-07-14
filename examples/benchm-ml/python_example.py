#!/usr/bin/python

import sys
import csv
from sklearn import metrics
sys.path.append('../../src/python')

import gbdt

def ComputeAUC(forest, data, targets):
    predictions = forest.predict(data)
    fpr, tpr, _ = metrics.roc_curve(targets, predictions, pos_label=1)
    return metrics.auc(fpr, tpr)

def GetTargets(tsv):
    labels = [row[8] for i, row in enumerate(csv.reader(open(tsv), delimiter='\t')) if i != 0 and len(row) > 0]
    return [1 if l == 'Y' else -1 for l in labels]

def main():
    loss_func = sys.argv[1]
    float_features = ["DepTime", "Distance"]
    cat_features = ["Month", "DayofMonth", "DayOfWeek", "UniqueCarrier", "Origin", "Dest"]
    config = {'loss_func': loss_func,
              'num_trees': 20,
              'num_leaves': 16,
              'example_sampling_rate': 0.5,
              'feature_sampling_rate': 0.8,
              'pair_sampling_rate': 0.00001,
              'shrinkage' : 0.1}

    training_data = gbdt.DataStore(tsvs=["train-0.1m.tsv"],
                                   binned_float_cols=float_features,
                                   string_cols=cat_features)
    training_targets = GetTargets('train-0.1m.tsv')
    forest = gbdt.train(training_data,
                   training_targets,
                   float_features=float_features,
                   cat_features=cat_features,
                   config=config)

    testing_data = gbdt.DataStore(tsvs=["test.tsv"],
                                  binned_float_cols=float_features,
                                  string_cols=cat_features)
    testing_targets = GetTargets('test.tsv')
    print "\nFeature Importance:"
    print '\n'.join(['{0}\t{1}'.format(feature, imp) for feature,imp in forest.feature_importance()])
    print

    print "Training AUC =", ComputeAUC(forest, training_data, training_targets)
    print "Testing AUC =", ComputeAUC(forest, testing_data, testing_targets)

if __name__ == '__main__':
    main()