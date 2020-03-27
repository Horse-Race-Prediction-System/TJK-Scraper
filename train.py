#!/usr/bin/env python3

import csv
import pickle
import numpy as np
from sklearn.svm import SVR
import sys


def create_sets(filename: str) -> tuple:
    data = csv.reader(open(filename, "r"))
    # Skip first row
    next(data)

    y = []  # Target to train on
    X = []  # Features

    for i, row in enumerate(data):
        # Get the target
        y.append(float(row[3]))

        # Get the features
        data = np.array(
            [float(_ if len(str(_)) > 0 else 0) for _ in row[4:]]
        )
        X.append(data.reshape(1, -1))

    return X, y


def train(filename: str, model: str):
    clf = SVR(C=1.0, epsilon=0.1, cache_size=1000)
    X, y = create_sets(filename)

    # Fit the model
    clf.fit(X, y)

    # Pickle the model so we can save and reuse it
    s = pickle.dumps(clf)

    # Save the model to a file
    f = open(model, 'wb')
    f.write(s)


if __name__ == "__main__":
    try:
        dataset_file, target_model = sys.argv[1:]
    except ValueError:
        print("Usage:", sys.argv[0], "[dataset.csv]", "[output.model]")
        exit(1)

    print("Started training...")
    train(dataset_file, target_model)
