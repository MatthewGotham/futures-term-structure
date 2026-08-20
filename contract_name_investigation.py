#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I got the ticker symbols and contract names from here:
    https://www.taifex.com.tw/enl/eng4/contractName

...and here:
    https://www.taifex.com.tw/enl/eng2/stockLists

...and saved them to contractName.csv

...but then found they didn't always line up with the codes used in the
files I downloaded with the settlement prices. This is the code I used to
clean everything up.

@author: Matthew Gotham
"""

import pandas as pd
from json import dumps

web_df = pd.read_csv("contractName.csv", na_filter = False).replace('',pd.NA)
exchange_codes = web_df['Ticker Symbol'].values
settlement_codes = pd.read_csv("./TAIFEX_settlement_files/2026-08-14.csv"
                               )['契約代號'].values

reconciliation = {}
for code in settlement_codes:
    try:
        match = next(c for c in exchange_codes if code==c)
    except StopIteration:
        try:
            match = next(c for c in exchange_codes
                         if code.removesuffix("F")==c)
        except StopIteration:
            try:
                match = next(c for c in exchange_codes if code+"F"==c)
            except StopIteration:
                try:
                    match = next(c for c in exchange_codes
                                 if code.removesuffix("1")==c)
                except StopIteration:
                    match = ""
    reconciliation[code] = match

umatched = [code for code,c in reconciliation.items() if c==""]


# Manual fix up
reconciliation["TE"] = "EXF" # electronic sector index
reconciliation["TF"] = "FXF" # finance sector index
reconciliation["MTX"] = "MXF" # TAIEX futures!

# Check for duplicates
inverted = {}
for key,value in reconciliation.items():
    if value not in inverted.keys():
        inverted[value] = [key]
    else:
        inverted[value] = inverted[value]+[key]

colength = max(len(x) for x in inverted.values())
for key,value in inverted.items():
    if len(value)<colength:
        inverted[key] = inverted[key]+([pd.NA]*(colength-len(value)))


# Save updated version in a few places.
export = pd.DataFrame.from_dict(inverted, orient='index')
save_df = web_df.join(export, on='Ticker Symbol').rename(columns={0: 'AKA1',
                                                                  1:'AKA2'})
save_df.to_csv("TAIFEX_codes.csv", index=False)

save_dict = {}
for i,sers in save_df.iterrows():
    if not sers['Contract'].endswith("Futures"):
        save_df.loc[i,'Contract'] = f"{save_df.loc[i,'Contract']} Futures"
    for col in ['AKA1','AKA2']:
        if not pd.isna(sers.loc[col]):
            contract = sers.loc['Contract']
            if not contract.endswith("Futures"):
                contract += " Futures"
            save_dict[sers.loc[col]] = contract

dict_str = dumps(save_dict)
with open("contracts.json", "w") as file:
    file.write(dict_str)