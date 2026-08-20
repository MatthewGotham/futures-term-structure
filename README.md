# Futures Term Structure

This repo contains tools for sourcing, analyzing and describing the term structure of futures contracts. The examples are all based on contracts traded on the [Taiwan Futures Exchange](https://www.taifex.com.tw/enl/eIndex); that's because the Republic of China government releases data from this exchange under the terms of a [licence](https://data.gov.tw/license) that allows me to share my visualizations and reports.


##  Quick start guide

1. Clone this repo to the location of your choice.
2. Run [download_TAIFEX_data.py](./download_TAIFEX_data.py). This downloads the most recent futures settlement prices from the ROC government API, and saves them into the folder [TAIFEX_settlement_files](/TAIFEX_settlement_files), in JSON or CSV format, depending on what's available.
    * This will usually only get you a couple of days' data. If you need more, you can download it manually [from the TAIFEX website](https://www.taifex.com.tw/enl/eng3/futDailyMarketView?menuid1=03). Save the CSV file in the [TAIFEX_settlement_files](/TAIFEX_settlement_files) folder in the same format as the other download(s).
2. Run [parse_TAIFEX_data.py](./parse_TAIFEX_data.py). This extracts price data for selected contracts from those JSON/CSV files, and saves them as data frames (with quotation dates as the rows and prompt dates as the columns) in parquet format in the folder [TAIFEX_prices](/TAIFEX_prices). By default, those contracts are:
        * Brent Crude Oil Futures (BRF)
        * TSMC Futures (CDF)
        * Gold Futures (GDF)
        * USD/CNH FX Futures (RHF)
        * TAIEX Index Futures (TXF)
2. Run [futures_curve_visualizations.py](/futures_curve_visualizations.py). For each of the selected contracts (default: same list as above), this produces:
    * an animation showing the movement of the futures curve over the period for which you have price data, saved to the folder [animations](/animations), and
    * charts showing the price, slope and curvature of the curve over the period, saved to the folder [graphs](/graphs).


## How to...

### ...change the contracts

1. The contract codes for the price data you want to extract must be included in the list assigned to `to_add` in the file [parse_TAIFEX_data.py](./parse_TAIFEX_data.py).
2. The contract codes for which you want to produce a curve movement animation and graphs must be included in the list assigned to `to_include` in the file [futures_curve_visualizations.py](/futures_curve_visualizations.py).


### ...change the dates to include in the animation

Change the `quote_dates` parameter in the call to `animate_curve` in [futures_curve_visualizations.py](/futures_curve_visualizations.py).


### ...change the prompt dates to include in the curve

Change the `prompt_dates` parameter in the call to `animate_curve` in [futures_curve_visualizations.py](/futures_curve_visualizations.py).


## To add

- Combination of animations and curves into an HTML report for each instrument.
- (Semi-)automated commentary on the curves for those reports.
