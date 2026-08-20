#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This program downloads settlement prices across the curve for TAIFEX
futures. Typically, one (or sometimes two, see below) day's data are
available, so that's what we download.

There seem to be two ways to download these data from the ROC government
website, both based on inspecting the web page for the resource found at
https://data.gov.tw/en/datasets/11319.
    1. Using the TAIFEX open API, as described in the "Note" on that page.
    Following the instructions leads to the URL assigned to the variable
    `url` below.
    2. Using the "Resources download link" on that page. This is the URL
    assigned to the variable `other_url` below.
    
Sometimes, the dates for which data are returned by these methods are out
of sync (by one day), so this program tries both and keeps what is needed.
The two methods also return the data in different formats; in this download
step we just retain the data in their original formats and think about
formatting later.

The legal basis for accessing the data in this way is the Open Government
Data License, version 1.0, found here:
    https://data.gov.tw/license

And preserved for posterity here:
    https://web.archive.org/web/20260812125051/https://data.gov.tw/license

@author: Matthew Gotham
"""

import os
import re
from requests import get
from datetime import datetime


# Method 1: TAIFEX open API (JSON format)

download_folder = "./TAIFEX_settlement_files"
url = "https://openapi.taifex.com.tw/v1/DailyMarketReportFut"
url_text = get(url).text
date_raw = re.search(r'Date":"[0-9]*"', url_text)[0][-9:-1]
datest = datetime.strptime(date_raw, "%Y%m%d")


# Method 2: ROC government download link (CSV format)

other_url = "https://www.taifex.com.tw/data_gov/taifex_open_data.asp?"
other_url += "data_name=DailyMarketReportFut"
other_url_text = get(other_url).text
other_date_raw = other_url_text.split("\n")[1].split(',')[0]
other_datest = datetime.strptime(other_date_raw, "%Y%m%d")


# Save the data we don't already have.

def check_add(data:str, dt_str:str, suffix:str, folder:str) -> None:
    if (f"{dt_str}.json" not in os.listdir(folder)
        and f"{dt_str}.csv" not in os.listdir(folder)):
        with open(os.path.join(folder,f"{dt_str}.{suffix}"), 'w'
                  ) as file:
            file.write(data)
            print(f"{dt_str}.{suffix} downloaded.")
    else:
        print(f"{dt_str}.{suffix} skipped.")


for data,dt_str,suffix in [(url_text,str(datest.date()),"json"),
                           (other_url_text,str(other_datest.date()),"csv")]:
    check_add(data, dt_str, suffix, download_folder)
