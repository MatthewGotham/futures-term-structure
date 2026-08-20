#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code takes the raw downloaded data in the `save_folder` folder, which
has one file per date with all instruments, and uses it to produce/update
the ticker-specific files in the `prices_folder` folder. The incoming data
are in different formats (json and csv), and columns aren't in English in
the csv files, so all of that has to be taken care of.

@author: Matthew Gotham
"""

import os, pandas as pd


# Preliminaries
save_folder = "./TAIFEX_settlement_files"
prices_folder =  "./TAIFEX_prices"
EN_cols = ['Date', 'Contract', 'ContractMonth(Week)', 'Open', 'High', 'Low',
           'Last', 'Change', '%', 'Volume', 'SettlementPrice', 'OpenInterest',
           'BestBid', 'BestAsk', 'HistoricalHigh', 'HistoricalLow',
           'TradingHalt', 'TradingSession',
           'Volume(ExecutionsAmongSpreadOrderAndSingleOrderOnly)']
CN_cols = ['日期', '契約代號', '到期月份(週別)', '開盤價', '最高價', '最低價',
           '最後成交價', '漲跌價', '漲跌%', '合計成交量', '結算價', '未沖銷契約數',
           '最後最佳買價', '最後最佳賣價', '歷史最高價', '歷史最低價',
           '是否因訊息面暫停交易', '交易時段', '價差對單式委託成交量']
translation = {cn:en for cn,en in zip(CN_cols,EN_cols)}
translation.update({"一般": "Regular", "盤後": "After-Hours"})


#%% Get data for the desired tickers from the files.

# Adapt the following line as necessary, for the contracts you're interested in.
to_add = ["TX", "GDF", "BRF", "CDF", "RHF"]

# Access the data we have.
dfs = {code: pd.read_parquet(os.path.join(prices_folder,
                                    f"TAIFEX_{code}_prices.parquet"))
       if f"TAIFEX_{code}_prices.parquet" in os.listdir(prices_folder)
       else pd.DataFrame() for code in to_add}

# Read the futures files and save to the dict as temporary storage.
for futures_file in [f for f in os.listdir(save_folder) if f.endswith('json')
                     or f.endswith('csv')]:
    for code in to_add:
        df = dfs[code]
        if pd.Timestamp(futures_file[:10]) not in df.index:
            # Update with data we don't have yet.
            if futures_file.endswith("json"):
                # JSON
                source_df = pd.read_json(os.path.join(save_folder,
                                                      futures_file))
            else:
                # CSV
                source_df = pd.read_csv(os.path.join(save_folder,futures_file)
                                        ).rename(columns=translation)
            source_df = source_df.replace('-',pd.NA).replace("NULL",pd.NA)
            df_new = source_df[source_df['Contract']==code
                               ].dropna(subset='SettlementPrice').copy()
            df_new['Prompt'] = pd.to_datetime(df_new['ContractMonth(Week)'],
                                              format="%Y%m", errors='coerce')
            try:
                df_new['Date'] = pd.to_datetime(df_new['Date'],
                                                format='%Y%m%d')
            except ValueError:
                df_new['Date'] = pd.to_datetime(df_new['Date'],
                                                format='%Y/%m/%d')
            sers = df_new.set_index(['Date','Prompt'])['SettlementPrice']
            sers = pd.to_numeric(sers).replace(0,pd.NA)
            df = pd.concat([df, sers.unstack()], sort=True)
            dfs[code] = df
            print(f"{code} data from {futures_file} added.")

# Save to disk.
for code,df in dfs.items():
    df.sort_index().to_parquet(os.path.join(prices_folder,
                                    f'TAIFEX_{code}_prices.parquet'))
