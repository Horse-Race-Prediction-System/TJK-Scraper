#!/usr/bin/env python3

from bs4 import BeautifulSoup, NavigableString
import csv
import pathlib
import sys

try:
    source, target = sys.argv[1:]
except ValueError:
    print("Usage:", sys.argv[0], "<source folder>", "<target file>")
    exit(1)

horses = [
    # First row for column names
    [
        "Name",
        "Age",
        "Country",
        "Breed",
        "Father",
        "Mother",
        "Races",
        "First",
        "Second",
        "Third",
        "Fourth",
        "FirstPercent",
        "SecondPercent",
        "ThirdPercent",
        "FourthPercent",
        "Earnings"
    ]
]

# Start parsing
print("Starting parse of TJK data...")
sort_key = lambda k: int(k.name.split(".")[0][5:])
for fname in sorted(pathlib.Path(source).glob("page_*.html"), key=sort_key):
    print("  Parsing", fname)

    soup = BeautifulSoup(fname.read_text(), 'html.parser')
    for row in soup.find_all("tr"):
        # Skip 'load more' row
        if "class" in row.attrs and "hidable" in row["class"]:
            continue

        # Collect fields
        fields = []
        for field in row.children:
            if isinstance(field, NavigableString):
                fields.append(field)
            else:
                fields.append(field.get_text().strip())

        # Clean empty fields and insert
        horses.append(list(filter(str.strip, fields)))

print("Writing results to", target + "!")
with open(target, "w", newline="") as f:
    w = csv.writer(f)
    w.writerows(horses)
