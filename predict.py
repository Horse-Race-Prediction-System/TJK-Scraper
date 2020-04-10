#!/usr/bin/env python3

import numpy as np
import csv
import pickle
from sklearn.svm import SVR
import sys
import typing


def read_model(model_file: typing.IO) -> SVR:
    return pickle.loads(model_file.read())


def create_prediction_data(validation_file: typing.IO) -> dict:
    validation_data = csv.DictReader(validation_file)

    races = {}
    for row in validation_data:
        race_id = row["EntryID"]
        finish_pos = float(row["Placement"])

        if race_id not in races:
            races[race_id] = []

        # Skip horses that didn't run
        if finish_pos < 1:
            continue

        # Create validation array
        data = np.array([
            float(feat if len(str(feat)) > 0 else 0)
            for feat in list(row.values())[4:]
        ])
        data = data.reshape(1, -1)
        races[race_id].append({
            "data": data,
            "prediction": None,
            "finish_pos": finish_pos
        })

    return races


def predict(prediction_data: dict, model: SVR):
    race_count = 0
    correct_win = 0
    correct_first_three = 0

    for race_id, horses in prediction_data.items():
        # Predict each horse
        for horse in horses:
            horse["prediction"] = model.predict(horse["data"])

        # Sort by model placement
        horses.sort(key=lambda h: h["prediction"])

        race_count += 1

        # If the horse that won the race is in first place, then the
        # model is correct, add a point
        if horses[0]["finish_pos"] == 1:
            correct_win += 1

        # If the model predicted the horse in first three, then it's
        # also somewhat good
        if horses[0]["finish_pos"] <= 3:
            correct_first_three += 1

    print("Total count of predicted races:", race_count)
    print("Total count of correct win predictions:", correct_win)
    print("Total count of correct first three places predictions:", correct_first_three)


if __name__ == "__main__":
    try:
        model_file, prediction_csv = sys.argv[1:]
    except ValueError:
        print("Usage:", sys.argv[0], "[model file]", "[prediction.csv]")
        exit(1)

    with open(model_file, "rb") as f:
        model = read_model(f)

    with open(prediction_csv, "r") as f:
        races = create_prediction_data(f)

    predict(races, model)
