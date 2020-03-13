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
        "RaceID",
        "RaceCity",
        "HorseName",
        "Age",
        "Origin",
        "Weight",
        "Jokey",
        "Owner",
        "Coach",
        "Degree",
        "GNY",
        "AGF",
        "StartPos",
        "Difference",
        "LateExit",
        "HandicapPoints"
    ]
]

# Start parsing
print("Starting parse of TJK data...")
for fname in sorted(pathlib.Path(source).glob("*")):
    print("  Parsing", fname)

    # Parse all races
    for fn in fname.glob("*.html"):
        soup = BeautifulSoup(fn.read_text(), 'html.parser')
        for race in soup.find("div", attrs={"class": "races-panes"}).children:
            if isinstance(race, NavigableString):
                continue

            race_id = race["id"]
            race_city = race["sehir"]

            for row in race.find_all("tr"):
                # Skip header rows
                if not "class" in row.attrs:
                    continue

                # Collect fields
                fields = []
                for i, field in enumerate(row.children):
                    if isinstance(field, NavigableString):
                        fields.append(field)
                    else:
                        fields.append(field.get_text().strip())

                # Delete the order field, which is inconsistent
                fields = list(filter(str.strip, fields))
                try:
                    int(fields[0])
                except ValueError:
                    fields = [
                        race_id, race_city,
                    ] + fields
                else:
                    fields = [
                        race_id, race_city,
                    ] + fields[1:]

                # Clean up the origin field
                fields[4] = re.sub("\s+", " ", re.sub("\n", "", fields[4]))

                # Clean empty fields and insert
                races.append(fields)

print("Writing results to", target + "!")
with open(target, "w", newline="") as f:
    w = csv.writer(f)
    w.writerows(races)
