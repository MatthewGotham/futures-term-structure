#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 17:06:23 2026

@author: matthew
"""

import os
import re
# import pandas as pd
from requests import get
from datetime import datetime
# from io import StringIO


# Download the data using the API, and save as a JSON file.

download_folder = "./TAIFEX_settlement_files"
url = "https://openapi.taifex.com.tw/v1/DailyMarketReportFut"
url_text = get(url).text
date_raw = re.search(r'Date":"[0-9]*"', url_text)[0][-9:-1]
datest = datetime.strptime(date_raw, "%Y%m%d")


# Check to see if there are any more data to be had from the Taiwanese
# government website, and if so get them too.

other_url = "https://www.taifex.com.tw/data_gov/taifex_open_data.asp?"
other_url += "data_name=DailyMarketReportFut"
other_url_text = get(other_url).text
other_date_raw = other_url_text.split("\n")[1].split(',')[0]
other_datest = datetime.strptime(other_date_raw, "%Y%m%d")


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
    

# pseudofile.seek(0); df = pd.read_json(pseudofile).replace('-',float('nan')
#                                                           ).replace('NULL',
#                                                                   float('nan'))
# # Convert to numeric.
# df['%'] = df['%'].str.strip('%').astype(float)/100
# num_cols = df.columns[3:16]
# for col in num_cols:
#     df[col] = pd.to_numeric(df[col])
# # Convert to dates.
# df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
# exp_col = next(c for c in df.columns if c.lower().startswith('contractmonth')
#                or c.lower().startswith('contract month'))
# df[exp_col] = pd.to_datetime(df[exp_col], format='%Y%m')