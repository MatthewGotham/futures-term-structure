#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 22:10:55 2026

@author: matthew
"""

import os, pandas as pd
from json import loads
from datetime import timedelta, datetime
from matplotlib import pyplot as plt, animation
from matplotlib.lines import Line2D
from miscellaneous import month_locators, also_year, day_locators, \
    also_month


with open("contracts.json", "r") as file:
    contracts_dict = loads(file.read())
priced_in_dict = {"TX":"NT$",
                  "GDF":"US$/toz",
                  "BRF":"NT$/barrel",
                  "CDF":"NT$/share",
                  "RHF":"CN¥/US$"}
for code in [c for c in contracts_dict.keys()
             if c not in priced_in_dict.keys()]:
    # Placeholder
    priced_in_dict[code] = ""


#%% Definitions

def animate_curve(curve:pd.DataFrame, title:str, priced_in:str|None=None,
                  quote_dates:int|tuple[datetime,datetime]|None=None,
                  prompt_dates:tuple[datetime,datetime]|None=None,
                  speed:float=4) -> animation.ArtistAnimation:
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
        dates (the whole index of curve). This can be narrowed either by
        entering a date range in the form of (starting date, closing date)
        (both will be included), or by entering an integer n, in which case
        the final n available dates will be included.
    prompt_dates:
        The dates to include in the curve. Default: all available dates
        (all the columns of curve). This can be narrowed by entering a date
        range in the for of (starting date, closing date) (both will be)
        included.
    speed:
        Animation speed in shifts/second. Default: 4.
    
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


def triple_plot(curve:pd.DataFrame, title:str, priced_in:str|None=None
                ) -> plt.Figure:
    """
    
    """
    # Level
    level = curve.copy()
    level['Month1'] = [next(i for i,bl in pd.notna(level.loc[dt]).items() if bl
                            ) for dt in level.index]
    level['Month2'] = [next(m for m in level.columns if m>c)
                       for c in level['Month1']]
    # Start the plot.
    fig, (ax,ax1,ax2) = plt.subplots(1, 3, figsize=(3*6.4,1.3*4.8))
    fig.suptitle(title)
    for i,col in enumerate([c for c in curve.columns]):
        clr = f"C{i}"
        solid = level[(level['Month1']!=col)&(level['Month2']!=col)][col]
        dashed = level[level['Month1']!=col][col]
        dotted = level[col]
        ax.plot(solid, color=clr, label=col.strftime("%b %y"))
        ax.plot(dashed, color=clr, linestyle='--')
        ax.plot(dotted, color=clr, linestyle=':')
    ax.set(title='Level', ylabel=priced_in)
    ax_handles, ax_labels = ax.get_legend_handles_labels()
    m1_line = Line2D([0],[0], label='Front Month', color='k', linestyle=':')
    m2_line = Line2D([0],[0], label='Second Month', color='k', linestyle='--')
    ax_handles = [*ax_handles, m1_line, m2_line]
    ax_leg_cols = 3 if len(ax_handles)>8 else 2 if len(ax_handles)>3 else 1
    ax.legend(handles=ax_handles, title='Price', ncols=ax_leg_cols,
              loc="upper center", bbox_to_anchor=(0.5,-0.1))
    # Slope
    slope = curve.diff(-1, axis=1).dropna(axis=1, how='all')
    missing = next(c for c in curve.columns if c not in slope.columns)
    slope_clrs = []
    # We have to separate positive and negative values for the stackplot.
    for i,col in enumerate(slope.columns):
        slope_clrs.append(f"C{i}")
        if (len(slope[slope[col]<0].index)>0
            and len(slope[slope[col]>=0].index)>0):
            # new_col = f"+{col}"
            new_col = col+timedelta(days=1)
            slope[new_col] = slope[slope[col]>=0][col]
            slope[col] = slope[slope[col]<0][col]
            slope_clrs.append(f"C{i}")
    slope = slope.reindex(sorted(slope.columns), axis=1)
    slope.plot(ax=ax1, kind='area', linewidth=0, color=slope_clrs)#, label=slope_labels)
    ax1.set(title="Slope", ylabel=priced_in, xlabel=None)
    ax1.tick_params(rotation=0)
    # Get rid of the duplicate labels.
    input_handles, input_labels = ax1.get_legend_handles_labels()
    ax1_handles, interim_labels = [],[]
    for handle,label in zip(input_handles, input_labels):
        dt = pd.Timestamp(label)
        if dt.day==1:
            ax1_handles.append(handle)
            interim_labels.append(dt.strftime('%b %y'))
    # Format labels.
    ax1_labels = []
    for i,label in enumerate(interim_labels):
        try:
            new_label = f"{label}-{interim_labels[i+1]}"
        except IndexError:
            new_label = f"{label}-{pd.Timestamp(missing).strftime('%b %y')}"
        ax1_labels.append(new_label)
    ax1_leg_cols = 3 if len(ax1_handles)>8 else 2 if len(ax1_handles)>3 else 1
    ax1.legend(handles=ax1_handles, labels=ax1_labels, title='Spread',
               ncols=ax1_leg_cols, loc="upper center",
               bbox_to_anchor=(0.5,-0.1))
    # Curvature
    curvature = pd.DataFrame(index=curve.index)
    for i,col in enumerate(curve.columns[1:-1], 1):
        prev = curve.columns[i-1]
        nex = curve.columns[i+1]
        prev_gap = col-prev
        nex_gap = nex-col
        if prev_gap*1.1 > nex_gap > prev_gap*0.9:
            new_col = f"{prev.strftime('%b %y')}:{col.strftime('%b %y')}:"
            new_col += f"{nex.strftime('%b %y')}"
            curvature[new_col] = curve[prev]+curve[nex]-2*curve[col]
    if any(curvature>0):
        ax2.axhline(0, color='C7', linewidth=0.5, alpha=0.5)
    curvature.plot(ax=ax2)
    ax2.set(title='Curvature', ylabel=priced_in, xlabel=None)
    ax2.tick_params(rotation=0)
    ax2_leg_cols = (3 if len(curvature.columns)>8
                    else 2 if len(curvature.columns)>3 else 1)
    ax2.legend(title='Butterfly', ncols=ax2_leg_cols,
              loc="upper center", bbox_to_anchor=(0.5,-0.1))
    # Finishing up
    for axis in [ax,ax1,ax2]:
        day_locators(axis, [1,7,13,19,25], range(1,32), new_line=True)
    return fig


#%% Curves to save

# Adapt the following line as necessary, for the contracts you're interested in.
to_include = ["TX", "GDF", "BRF", "CDF", "RHF"]
for code in to_include:
    contract = contracts_dict[code]
    quote = priced_in_dict[code]
    curve = pd.read_parquet(os.path.join("TAIFEX_prices",
                                    f'TAIFEX_{code}_prices.parquet'))
    # Animation
    animate_curve(curve, contract, quote
                  ).save(os.path.join("animations",
                                      f'TAIFEX_{code}_curve_animation.mp4'),
                                      writer=animation.FFMpegWriter())
    print(f"{code} curve animation complete.")
    # Charts
    triple_plot(curve, contract, quote
                ).savefig(os.path.join("graphs",f"TAIFEX_{code}_charts.png"),
                          bbox_inches='tight')
    print(f"{code} curve charts complete.")
