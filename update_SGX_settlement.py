#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 17:20:47 2026

@author: Matthew Gotham
"""

import os, pandas as pd
from zipfile import ZipFile
from datetime import datetime
from miscellaneous import contracts_dict


# Change the following line to the path of your Downloads folder, as necessary.
downloads_folder = "../../../Downloads"
save_folder = "./SGX_settlement_files"
prices_folder =  "./SGX_settlement_prices"



#%% Get the settlement files from the Downloads folder.
# Save them into the save folder, after renaming.

futures_files = [f for f in os.listdir(downloads_folder)
                 if f.endswith("FUT.zip")]

for futures_zip in futures_files:
    new_file = futures_zip.split(".")[0]+"."+"csv"
    dt = datetime(2026,int(futures_zip[0:2]),int(futures_zip[2:4]))
    dt_str = str(dt.date())
    if f"{dt_str}.csv" not in os.listdir(save_folder):
        with ZipFile(os.path.join(downloads_folder,futures_zip)) as z:
            z.getinfo(new_file).filename = f"{dt_str}.csv"
            z.extract(new_file, path=save_folder)
            print(f"{new_file} extracted.")


#%% Get the for the desired securities from the files.

# Adapt the following line as necessary, for the contracts you're interested in.
to_add = ['FEF', 'CN', 'CY', 'TF', 'MF5F']

# Access the data we have.
dfs = {code: pd.read_parquet(os.path.join(prices_folder,
                                    f"SGX_{code}_settlement_prices.parquet"))
       if f"SGX_{code}_settlement_prices.parquet" in os.listdir(prices_folder)
       else pd.DataFrame() for code in contracts_dict.keys()}

# Read the futures files and save to the dict as temporary storage.
for futures_file in [f for f in os.listdir(save_folder) if f.endswith('csv')]:
    for code in to_add:
        df = dfs[code]
        if pd.Timestamp(futures_file[:10]) not in df.index:
            source_df = pd.read_csv(os.path.join(save_folder,futures_file))
            df_new = source_df[source_df['COM'].str.strip()==code].copy()
            df_new['Prompt'] = [datetime(int(yy),int(mm),1) for yy,mm
                                in zip(df_new['COM_YY'],df_new['COM_MM'])]
            df_new['Date'] = pd.to_datetime(df_new['DATE'], format='%Y%m%d')
            sers = df_new.set_index(['Date','Prompt'])['SETTLE']
            df = pd.concat([df, sers.unstack()], sort=True)
            dfs[code] = df
    print(f"{futures_file} added.")

# Save to disk.
for code,df in dfs.items():
    df.sort_index().to_parquet(os.path.join(prices_folder,
                                    f'SGX_{code}_settlement_prices.parquet'))
