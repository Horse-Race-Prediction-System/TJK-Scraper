TJK-Scraper
---

This repository contains two tools to scrape the TJK.org website to get a list
of horses in CSV format.

## Requirements

 - Python 3.6+

## Installation

 - Create a new virtualenv: `~$ virtualenv env`
 - Activate it: `~$ . env/bin/activate`
 - Install the packages: `~$ pip install -r requirements.txt`

## Usage

 - First, download all the TJK horse race data from tjk.org:
   `~$ mkdir pages && ./scrape.py pages/`
 - Then, generate a CSV file from the downloaded pages:
   `~$ ./format.py pages/ horses.csv`
