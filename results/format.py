#!/usr/bin/env python3

from bs4 import BeautifulSoup, NavigableString
import csv
import pathlib
import re
import sys

try:
    source, target = sys.argv[1:]
except ValueError:
    print("Usage:", sys.argv[0], "[source folder]", "[target file]")
    exit(1)

races = [
    # First row for column names
    [
        "RaceCity",
        "RaceDate",
        "RaceNumber",
        "Placement",
        "HorseName",
        "Age",
        "Mother",
        "Father",
        "Weight",
        "Jokey",
        "Owner",
        "Coach",
        "StartPos",
        "Degree",
        "Gny",
        "Difference"
    ]
]

# Start parsing
print("Starting parse of TJK data...")
for fname in sorted(pathlib.Path(source).glob("*")):
    print("  Parsing", fname)

    # Parse all races
    for fn in fname.glob("*.csv"):
        rd = csv.reader(open(str(fn.resolve())), delimiter=";")
        city, _, date = next(rd)
        while True:
            try:
                race_header = next(rd)
            except StopIteration:
                break

            race_number = race_header[0].split(".")[0]
            # Skip 3 rows
            next(rd); next(rd); next(rd)
            while True:
                horse = next(rd)
                # Need to check if the number can be coerced, if not
                # the horse placements are over.
                try:
                    int(horse[0])
                except ValueError:
                    break

                races.append([
                    city, date, race_number,
                    *horse[:10],
                    *horse[12:15]
                ])

            # Skip next line, if it doesn't exist we're done
            try:
                next(rd)
            except StopIteration:
                break


print("Writing results to", target + "!")
with open(target, "w", newline="") as f:
    w = csv.writer(f)
    w.writerows(races)
