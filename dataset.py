#!/usr/bin/env python3
# coding: utf-8

import datetime
import csv
import re
import sqlite3
import sys


def update_age(age: str, race_date: str) -> int:
    match = re.match(r"\d+", age)
    if match is None:
        raise ValueError("Age doesn't start with number.")
    else:
        age_int = int(match.group(0))
        race_year = int(race_date.split("/")[2])
        this_year = datetime.date.today().year

        return age_int + (this_year - race_year)


def like_first_word(s: str) -> str:
    return re.split(r"\s+", s)[0] + "%"


def make_rowid(city: str, date: str, num: str, name: str) -> str:
    return "{}_{}_{}_{}".format(
        city, date.replace("/", ""), num, name.replace(" ", "")
    )


def make_entryid(city: str, date: str, num: str) -> str:
    return make_rowid(city, date, num, "!!").replace("_!!", "")


try:
    horse_db, result_csv, target_csv = sys.argv[1:]
except ValueError:
    print("Usage:", sys.argv[0], "[horse database]",
          "[result.csv]", "[target.csv]")
    exit(1)

conn = sqlite3.connect(horse_db)
cursor = conn.cursor()

result_rd = csv.DictReader(open(result_csv), delimiter=",")
next(result_rd)  # Skip header

dataset = [
    # Header row
    [
        "RowID",  # The unique ID for this race entry.
        "EntryID",  # The unique ID for the race.
        "Gny",  # Amount of ganyots purchased for this horse
        "Placement",  # The finish position of the horse
        # Model features
        "Finish",  # If the horse is in finish position 1-3 1, else 0
        "Start",  # If the horse is start position 1-3 1, else 0
        "Weight",  # If horse weight more than race average 1, else -1
        "Successful",  # If horse 1-3 percent is >50% 1, else 0
        "Experienced",  # If horse has had at least 5 races 1, else 0
        "SameDriver",  # If horse's driver is same as last race 1, else 0
        "WonLast",  # If this horse finished its last race first 1, else 0
        "WonLastThree",  # If this horse finished one of last 3 races first 1,
                         # else 0
    ]
]

state = {
    # Holding the following data for the horses:
    # - Last driver (Jokey) of horse
    # - Last 3 placements
    "horses": {},
    "race_num": None,
    # Setting weight averages and such
    "tracked_rows": []
}

print("Starting final dataset generation.")
for horse in result_rd:
    print("  Processing",
          horse["RaceDate"], "-",
          horse["RaceCity"], "- Race",
          horse["RaceNumber"], "-",
          horse["HorseName"] + "...")
    # Skip horses that didn't run
    if "(Koşmaz)" in horse["HorseName"]:
        print("    Skipping because the horse didn't run.")
        continue

    if state["race_num"] and state["race_num"] != horse["RaceNumber"] and \
       len(state["tracked_rows"]):
        # Average all weights of horses and update the Weight feature.
        aver = 0
        horse_count = len(state["tracked_rows"])
        weights = []

        for row in state["tracked_rows"]:
            weight = float(horse["Weight"].split(" ")[0].replace(",", "."))
            aver += weight
            weights.append(weight)

        aver /= horse_count
        for w, row in zip(weights, state["tracked_rows"]):
            if w >= aver:
                row[6] = 1
            else:
                row[6] = -1

        state["tracked_rows"].clear()

    state["race_num"] = horse["RaceNumber"]

    cursor.execute(
        "SELECT * FROM horses WHERE name LIKE ? AND age LIKE ?",
        [
            like_first_word(horse["HorseName"]),
            like_first_word(str(update_age(horse["Age"], horse["RaceDate"])))
        ]
    )
    row = cursor.fetchone()

    if not row:
        print("    Skipping because the horse wasn't found.")
        continue
    else:
        # Skip dead horses
        if "(Öldü)" in row[0]:
            print("    Skipping because the horse is dead.")
            continue

        dataset_row = [
            make_rowid(horse["RaceCity"], horse["RaceDate"],
                       horse["RaceNumber"], row[0]),
            make_entryid(horse["RaceCity"], horse["RaceDate"],
                         horse["RaceNumber"]),
            horse["Gny"],
            horse["Placement"],

            # Model features
            1 if 1 <= int(horse["Placement"]) <= 3 else 0,  # Finish

            1 if 1 <= int(horse["StartPos"].split(" ")[0]) <= 3 else 0,  # Start

            0,  # Weight Updated above, when race is complete

            1 if sum(map(int, row[11:14])) > 50 else 0,  # Successful

            1 if int(row[6]) > 5 else 0,  # Experienced

            1 if row[0] in state["horses"] and
            state["horses"][row[0]]["jokey"] == horse["Jokey"] else 0,  # SameDriver

            1 if row[0] in state["horses"] and
            state["horses"][row[0]]["last_races"][-1] == 1 else 0,  # WonLast

            1 if row[0] in state["horses"] and
            1 in state["horses"][row[0]]["last_races"] else 0,  # WonLastThree
        ]
        dataset.append(dataset_row)
        state["tracked_rows"].append(dataset_row)

    if row[0] in state["horses"]:
        state["horses"][row[0]]["jokey"] = horse["Jokey"]
        state["horses"][row[0]][
            "last_races"
        ] = state["horses"][row[0]]["last_races"][:-2] + [int(horse["Placement"])]
    else:
        state["horses"][row[0]] = {
            "jokey": horse["Jokey"],
            "last_races": [int(horse["Placement"])]
        }

print("Writing results to", target_csv + "!")
with open(target_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerows(dataset)
