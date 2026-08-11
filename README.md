# Futures Term Structure

This repo contains tools for sourcing, analyzing and describing the term structure of futures contracts. The examples are all based on contracts traded on the SGX; that's because the SGX makes settlement prices for the last 60 trading days freely available for download [from its website](https://www.sgx.com/research-education/derivatives).


##  Quick start guide

1. Clone this repo to the location of your choice.
2. Download daily price data from the SGX link above (you want the downloads under &lsquo;Historical Settlement Data&rsquo;).
2. Change the line in [update_SGX_settlement.py](./update_SGX_settlement.py) where the variable `downloads_folder` folder is introduced, to point it at the folder you downloaded the SGX zip files to.
2. Run [update_SGX_settlement.py](./update_SGX_settlement.py).
    * The csv files contained in the downloaded zip files are extracted into the folder [SGX_settlement_files](/SGX_settlement_files).
    * Price data for selected contracts are extracted from those csv files, and saved as data frames (with quotation dates as the rows and prompt dates as the columns) in parquet format in the folder [SGX_settlement_prices](/SGX_settlement_prices). By default, those contracts are:
        * SGX IODEX Iron Ore Futures (FEF)
        * SGX FTSE China A50 Index Futures (CN)
        * SGX CNY/USD FX Futures (CY)
        * SGX SICOM TSR20 Futures (TF)
        * SGX Platts Marine Fuel 0.5% FOB Singapore Index Futures (MF5F)
2. Run [futures_curve_animation.py](/futures_curve_animation.py).
    * For each of the selected contracts (default: same list as above), an animation showing the movement of the futures curve over the period for which you have price data is saved to the folder [animations](/animations).


## How to...

### ...change the contracts

You need to do (up to) three things:

1. Make sure that the spreadsheet [SGX_codes.csv](./SGX_codes.csv) contains information for the contract that you want to include. I _think_ that the first column is a complete list of SGX contract codes (it's pulled from one of those downloads), but the other columns are quite sparse at the moment as I fill in the names of the contracts that those codes refer to. I haven't been able to find a master spreadsheet containing this information anywhere; do let me know if you have one.
2. The contract codes for the price data you want to extract must be included in the list assigned to `to_add` in the file [update_SGX_settlement.py](./update_SGX_settlement.py).
2. The contract codes for which you want to produce a curve movement animation must be included in the list assigned to `to_include` in the file [futures_curve_animation.py](/futures_curve_animation.py).


### ...change the dates to include in the animation

Change the `quote_dates` parameter in the call to `animate_curve` in [futures_curve_animation.py](/futures_curve_animation.py).


### ...change the prompt dates to include in the curve

Change the `prompt_dates` parameter in the call to `animate_curve` in [futures_curve_animation.py](/futures_curve_animation.py).


## To add

- More analysis and visualizations.
- Futures data from other sources.
