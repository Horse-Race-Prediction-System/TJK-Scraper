#!/usr/bin/env python3
# coding: utf-8

import os.path
import random
import re
import requests
import sys
import time


BASE_URL = "https://www.tjk.org/TR/YarisSever/Query/DataRows/AtIstatistikleri?" \
    "PageNumber={}&Sort=AtAdi+ASC&X-Requested-With=XMLHttpRequest"
ERROR_RE = re.compile(".*hata/tjkLogo.*", re.I)


s = requests.session()
page = 0 # First page is rendered server-side
target_folder = sys.argv[1]

print("Starting TJK scrape!")
while True:
    target = os.path.join(
        target_folder, "page_{}.html".format(page))
    if os.path.exists(target):
        print("  SKIPPING page {} because it's already downloaded.".format(page))
        page += 1
        continue

    sys.stdout.write("  Downloading page {}... ".format(page))
    sys.stdout.flush()

    data = s.get(BASE_URL.format(page)).text
    if ERROR_RE.match(data):
        print("\n  Stopping at page {} due to error!".format(page))
        break

    with open(target, "w") as f:
        f.write(data)

    sys.stdout.write("\033[1;32m✓\033[0m\n")

    secs = random.randint(5, 10)
    while secs:
        sys.stdout.write("\r  Downloaded! Sleeping {} seconds to prevent "
                         " overload on TJK servers.".format(secs))
        time.sleep(1)
        secs -= 1
    sys.stdout.write("\033[2K\r")  # Clear current line
    page += 1
