#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup
import datetime
import os
import random
import re
import requests
import sys
import time
import urllib.parse


BASE_URL = "https://www.tjk.org/TR/YarisSever/Info/Data/GunlukYarisSonuclari?" \
    "QueryParameter_Tarih={}&Sort=&X-Requested-With=XMLHttpRequest"
ERROR_RE = re.compile(".*kayıt bulunamadı.*", re.I)


s = requests.session()
try:
    target_folder, days = sys.argv[1:]
except ValueError:
    print("Usage:", sys.argv[0], "[target folder]",
          "[number of days to scrape]")
    sys.exit(1)

if not os.path.exists(target_folder):
    os.makedirs(target_folder)


current_date = datetime.date.today() - datetime.timedelta(days=int(days))
print("Starting TJK race results scrape!")
while True:
    # Check if we reached today
    if current_date == datetime.date.today():
        print("Scrape completed.")
        break

    # Check if the folder for the day exists
    day = current_date.strftime("%Y-%m-%d")
    target = os.path.join(target_folder, day)
    if os.path.exists(target):
        print("  SKIPPING day {} because it's already downloaded.".format(day))
        current_date += datetime.timedelta(days=1)
        continue
    else:
        os.makedirs(target)

    # Start download for this day
    sys.stdout.write("  Downloading day {}... ".format(day))
    sys.stdout.flush()

    # Try to get the data
    data = s.get(BASE_URL.format(
        current_date.strftime("%d%%2F%m%%2F%Y"))).text
    if ERROR_RE.match(data):
        print("\n  Stopping at day {} due to error!".format(day))
        break

    # Parse the list of cities and download all their data as well
    soup = BeautifulSoup(data, 'html.parser')
    cities = []
    for city in soup.find_all("a"):
        link = "https://tjk.org" + city["href"]
        city_page = BeautifulSoup(s.get(link).text, 'html.parser')
        city_id = city["data-sehir-id"]

        csv_link = urllib.parse.urljoin(
            link,
            city_page.find("a", {"id": "CSVBulten"})["href"]
        )

        with open(os.path.join(
                        target, "{}.csv".format(city_id)
        ), "wb") as f:
            f.write(s.get(csv_link).content)

    # We're done
    sys.stdout.write("\033[1;32m✓\033[0m\n")

    # Wait a random amount of seconds to prevent server load
    secs = 0
    while secs:
        sys.stdout.write("\r  Downloaded! Sleeping {} seconds to prevent "
                         " overload on TJK servers.".format(secs))
        time.sleep(1)
        secs -= 1
    sys.stdout.write("\033[2K\r")  # Clear current line

    # Go to next day
    current_date += datetime.timedelta(days=1)
