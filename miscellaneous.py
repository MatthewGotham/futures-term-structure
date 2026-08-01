#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
References and functions for general use.

@author: Matthew Gotham
"""

from datetime import datetime
from collections.abc import Iterable
from matplotlib import axes, pyplot as plt, dates as mdates


# These are the contracts I'm interested in. Adapt as needed for your interests.
cwf_str = 'SGX Baltic Capesize Time Charter Average (5 Routes) 180 Futures'
sora_str = "SGX Three-Month Singapore Overnight Rate Average (SORA) Futures"
mf5f_str = "SGX Platts Marine Fuel 0.5% FOB Singapore Index Futures"
contracts_dict = {'FEF': 'SGX Iron Ore (61%) Futures',
                  'CN': "SGX FTSE China A50 Index Futures",
                  "CY": "SGX CNY/USD FX Futures",
                  "TF": "SGX SICOM TSR20 Futures",
                  "SORA": sora_str, 'CWF': cwf_str, "MF5F": mf5f_str}
priced_in_dict = {"CWF": "$/day", 'SORA': 'S$', 'CY': '$/¥10', "CN": "$",
                  "TF": "¢/kg", "FEF": "$/t", "MF5F": "$/t"}
for key in [k for k in contracts_dict.keys()
            if k not in priced_in_dict.keys()]:
    priced_in_dict[key] = ""
# If you prefer, you can remove the empty string default statement above and
# include something like the statement below to check you haven't forgotten
# anything.

# if set(contracts_dict.keys())!=set(priced_in_dict.keys()):
#     print("EITHER contracts_dict OR priced_in_dict NEEDS UPDATING.")


def month_locators(axis:axes.Axes, majors:Iterable[int]=[1],
                   minors:Iterable[int]|None=None,
                   include_jan:bool=True, include_year:bool=True,
                   also_year:datetime|Iterable[datetime]|None=None
                   ) -> None:
    """
    Macro for formatting a datetime axis with control of month and/or
    year labels.
    
    Parameters
    ----------
    axis:
        The datetime axis to be formatted.
    majors:
        Iterable of ints corresponding to months that will have a tick
        and a tick label. Default: 1 (January) only.
    minors:
        Iterable of ints corresponding to months that will have a tick
        only. Default: None.
    include_jan:
        If True (default), the tick label for January includes 'Jan'.
    include_year:
        If True (default), the tick label for January includes the
        year. At least one of include_jan and include_year must be True.
    also_year:
        Add year to specified dates among the major ticks.
    """
    if 1 not in majors:
        raise ValueError("Majors must include January (1).")
    if not (include_jan or include_year):
        err_str = "At least one of include_jan and include_year must be True."
        raise ValueError(err_str)
    axis.xaxis.set_major_locator(mdates.MonthLocator(majors))
    def my_formatter(x,_):
        "Custom function"
        dt = mdates.num2date(x)
        if dt.month==1:
            return (dt.strftime('%b\n%Y') if include_jan and include_year
                    else dt.strftime('%b') if include_jan else dt.year)
        # \This/ has to do with how num2date works.
        if also_year is not None:
            add_year = (also_year if isinstance(also_year, Iterable)
                        else [also_year])
            tz_aware = [d.replace(tzinfo=dt.tzinfo) for d in add_year]
            if dt in tz_aware:
                return dt.strftime('%b\n%Y')
        return mdates.num2date(x).strftime('%b')
    axis.xaxis.set_major_formatter(plt.FuncFormatter(my_formatter))
    if minors is not None:
        axis.xaxis.set_minor_locator(mdates.MonthLocator(minors))


def also_year(axis:axes.Axes) -> None:
    """
    Supplement to month_locators for adding a year to the first major
    tick.
    """
    mticks = axis.get_xticklabels()
    date1 = mdates.num2date(mticks[0].get_position()[0])
    if date1.month!=1:# Not January so no year yet.
        new_label = date1.strftime('%b\n%Y')
        new_ticks = axis.get_xticks()
        new_labels = [new_label, *[t.get_text()
                                   for t in axis.get_xticklabels()[1:]]]
        axis.set_xticks(new_ticks, new_labels)


def day_locators(axis:axes.Axes, majors:Iterable[int]=[1],
                 minors:Iterable[int]|None=None,
                 new_line:bool=False) -> None:
    """
    Macro for formatting a datetime axis with control of month and/or
    year labels.
    
    Parameters
    ----------
    axis:
        The datetime axis to be formatted.
    majors:
        Iterable of ints corresponding to days that will have a tick
        and a tick label. Default: 1 only.
    minors:
        Iterable of ints corresponding to days that will have a tick
        only. Default: None.
    """
    axis.xaxis.set_major_locator(mdates.DayLocator(majors))
    def my_formatter(x,_):
        "Custom function"
        dt = mdates.num2date(x)
        if dt.month==1:
            if dt.day==1:
                return (dt.strftime('%d\n%b\n%Y').lstrip("0") if new_line
                        else dt.strftime('%d %b\n%Y').lstrip("0"))
            return (dt.strftime('%d\n%b').lstrip("0") if new_line
                    else dt.strftime('%d %b').lstrip("0"))
        if dt.day==1:
            return (dt.strftime('%d\n%b').lstrip("0") if new_line
                    else dt.strftime('%d %b').lstrip("0"))
        return mdates.num2date(x).strftime('%d').lstrip("0")
    axis.xaxis.set_major_formatter(plt.FuncFormatter(my_formatter))
    if minors is not None:
        axis.xaxis.set_minor_locator(mdates.DayLocator(minors))


def also_month(axis:axes.Axes, include_year:bool=True,
               new_line:bool=False) -> None:
    """
    Supplement to day_locators for adding a month to the first major
    tick.
    """
    mticks = axis.get_xticklabels()
    date1 = mdates.num2date(mticks[0].get_position()[0])
    if date1.day!=1:# Not the 1st so so month yet.
        if date1.month==1 or include_year:
            new_label = (date1.strftime('%d\n%b\n%Y').lstrip("0") if new_line
                         else date1.strftime('%d %b\n%Y').lstrip("0"))
        else:
            new_label = (date1.strftime('%d\n%b').lstrip("0") if new_line
                         else date1.strftime('%d %b').lstrip("0"))
        new_ticks = axis.get_xticks()
        new_labels = [new_label, *[t.get_text()
                                   for t in axis.get_xticklabels()[1:]]]
        axis.set_xticks(new_ticks, new_labels)
