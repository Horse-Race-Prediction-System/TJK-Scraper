#!/usr/bin/env python3
"""This script takes a horse dataset and generates an SQLite3 database out of it."""

import csv
import sqlite3
import sys
import re

NUMBER_PREFIX = re.compile("\d+")

# Get the required arguments
try:
    horses_csv, target_db = sys.argv[1:]
except ValueError:
    print("Usage:", sys.argv[0], "[horses.csv]", "[database filename]")
    exit(1)

# Connect to the database and create the tables
conn = sqlite3.connect(target_db)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS horses")
cursor.execute(
    """
CREATE TABLE horses (
    name VARCHAR(75) NOT NULL,
    age VARCHAR(30) NOT NULL,
    country VARCHAR(50) NOT NULL,
    breed VARCHAR(30) NOT NULL,
    father VARCHAR(75) NOT NULL,
    mother VARCHAR(75) NOT NULL,
    races INT NOT NULL,
    first INT NOT NULL,
    second INT NOT NULL,
    third INT NOT NULL,
    fourth INT NOT NULL,
    first_percent INT NOT NULL,
    second_percent INT NOT NULL,
    third_percent INT NOT NULL,
    fourth_percent INT NOT NULL,
    earnings REAL,
    PRIMARY KEY (name, age)
)"""
)

# Read the horse dataset
hrd = csv.reader(open(horses_csv), delimiter=",")
next(hrd)  # skip header line
for line in hrd:
    # If the age value for the horse is invalid, skip it
    if NUMBER_PREFIX.match(line[1]) is None:
        print("WARNING: Skipping horse", line[0], "because the age value is invalid.")
        continue

    try:
        # Compensate for empty values
        if len(line) < 16:
            line += [0] * (16 - len(line))
        # Insert the horse
        cursor.execute("INSERT INTO horses VALUES (" + ("?, " * 15) + "?)", line)
    except sqlite3.IntegrityError:
        # If a duplicate horse is in the dataset, skip it
        print("WARNING: Skipping horse", line[0], "because it already exists.")
    except sqlite3.ProgrammingError:
        # If any other error occurs, exit
        print(line)
        raise

# Save all data and close the database
conn.commit()
conn.close()
