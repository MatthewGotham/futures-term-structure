#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 22:10:55 2026

@author: matthew
"""

import os
import pandas as pd
from datetime import timedelta, datetime
from matplotlib import pyplot as plt, animation
from miscellaneous import month_locators, also_year, day_locators, \
    also_month, contracts_dict, priced_in_dict


#%% Definition

def animate_curve(curve:pd.DataFrame, title:str, priced_in:str|None=None,
                  quote_dates:int|tuple[datetime,datetime]|None=None,
                  prompt_dates:tuple[datetime,datetime]|None=None
                  speed:float=10) -> animation.ArtistAnimation:
    """
    A function to visualize the movement of a futures curve through time.
    
    Parameters
    ----------
    curve:
        A data frame of futures prices with price dates as the index, and
        prompt dates as the columns. Make sure the index is sorted.
    title:
        The (super)title for the charts.
    priced_in:
        The label for the y axis of the price curve chart. Default: no label.
    quote_dates:
        The dates for which to show the price curve. Default: all available
        dates (the whole index of curve).
    prompt_dates:
        The dates to include in the curve. Default: all available dates
        (all the columns of curve).
    speed:
        Animation speed in shifts/second. Default: 10.
    
    Returns
    -------
    A matplotlib animation object. Save to disk with the save method.
    """
    if prompt_dates is not None:
        curve = curve[[c for c in curve.columns
                       if prompt_dates[0]<=c<=prompt_dates[1]]]
    date_range = (curve.index.min()-timedelta(days=1),
                  curve.index.max()+timedelta(days=1))
    prompt_range = (curve.columns.min()-timedelta(weeks=2),
                    curve.columns.max()+timedelta(weeks=2))
    
    # Make plots and save to artists.
    fig, (ax,ax1) = plt.subplots(2, 1, height_ratios=(3,1),
                                 constrained_layout=True)
    fig.suptitle(title)
    month_locators(ax, [1,5,9] if len(curve.columns)>30
                   else [1,4,7,10] if len(curve.columns)>15 else range(1,13),
                   range(1,13))
    day_locators(ax1, [1,7,13,19,25], range(1,32), new_line=True)
    artists = []
    # Fill in gaps and get the period we're focussing on.
    if quote_dates is not None:
        if type(quote_dates)==int:
            curve = curve.tail(quote_dates)
        else:
            curve = curve.loc[quote_dates[0]:quote_dates[1]]
    curve = curve.replace(0, float('nan')).interpolate(method='time',
                                                       limit_area='inside')
    for i,sers in curve.iterrows():
        # Sometimes there are gaps in the middle.
        sers.dropna(inplace=True)
        # Curve
        ax.set(title="Price Curve", ylabel=priced_in, xlabel='Prompt')
        ax.set_ylim(curve.min().min()*0.95, curve.max().max()*1.05)
        ax.set_xlim(*prompt_range)
        #
        prev = curve.shift().loc[i,:].dropna()
        prev_prev = curve.shift(2).loc[i,:].dropna()
        # Plot previous curves, faded, to make the motion less jerky.
        p, = ax.plot(sers, color='C0')
        p1, = ax.plot(prev, color='C0', alpha=0.5)
        p2, = ax.plot(prev_prev, color='C0', alpha=0.3)
        also_year(ax)
        # Timer
        ax1.set(title="Date")
        ax1.set_xlim(*date_range)
        ax1.set_ylim(0, 1)
        ax1.set_yticks([])
        q = ax1.vlines(i, 0, 1, colors='C3')
        also_month(ax1)
        artists.append([p, p1, p2, q])
    
    # Save as video file.
    ani = animation.ArtistAnimation(fig=fig, artists=artists,
                                    interval=1/speed*1000)
    return ani


#%% Curves to save

# Adapt the following line as necessary, for the contracts you're interested in.
to_include = ['FEF', 'CN', 'CY', 'TF', 'MF5F']
for code in to_include:
    contract = contracts_dict[code]
    quote = priced_in_dict[code]
    curve = pd.read_parquet(os.path.join("SGX_settlement_prices",
                                    f'SGX_{code}_settlement_prices.parquet'))
    animate_curve(curve, contract, quote
                  ).save(os.path.join("animations",
                                      f'SGX_{code}_curve_animation.mp4'),
                                      writer=animation.FFMpegWriter())
    print(f"{code} curve animation complete.")
