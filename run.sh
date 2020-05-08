#!/usr/bin/env bash

set -e

DATA_FOLDER=${DATA_FOLDER:-"data/"}

echo "----------------------------------"
echo "Welcome to the TJK-Scraper script."
echo "----------------------------------"
echo

if [ ! -d env ]; then
    echo "WARNING: You have not created a virtualenv! Do you want me to create one now?"
    printf "(Y/n) > "
    read -r yn
    if [ "x$yn" = "xy" ] || [ "x$yn" = "x" ]; then
        if ! virtualenv env; then
            echo "Failed to create virtualenv! Please create it manually."
            exit 1
        fi
        . env/bin/activate
        if ! pip install -r requirements.txt; then
            echo "Failed to install the required packages. Please install manually."
            exit 1
        fi
    else
        echo "Please create the virtualenv and then re-run the script."
        exit 0
    fi
else
    . env/bin/activate
fi


if [ ! -d "$DATA_FOLDER" ]; then
    echo "Creating data folder..."
    mkdir -p "$DATA_FOLDER"
fi

echo "Downloading horse data..."
mkdir -p "${DATA_FOLDER}horses/"
python3 horses/scrape.py "${DATA_FOLDER}horses/"
echo "Formatting horse data..."
python3 horses/format.py "${DATA_FOLDER}horses/" "${DATA_FOLDER}horses.csv"

echo "Downloading race data..."
printf "How many days to download?> "
read -r days
mkdir -p "${DATA_FOLDER}results/"
python3 results/scrape.py "${DATA_FOLDER}results/" "$days"
echo "Formatting race data..."
python3 results/format.py "${DATA_FOLDER}results/" "${DATA_FOLDER}results.csv"

echo "Generating horse database..."
python3 generate_db.py "${DATA_FOLDER}horses.csv" "${DATA_FOLDER}horses.db"

echo "Generating dataset for training..."
python3 dataset.py "${DATA_FOLDER}horses.db" "${DATA_FOLDER}results.csv" "${DATA_FOLDER}dataset.csv"

echo "Training model..."
python3 train.py "${DATA_FOLDER}dataset.csv" "${DATA_FOLDER}svr.model"

echo "Model generation complete\!"
