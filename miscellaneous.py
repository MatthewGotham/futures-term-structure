#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
References and functions for general use.

@author: Matthew Gotham
"""

import pandas as pd
from datetime import datetime
from collections.abc import Iterable
from matplotlib import axes, pyplot as plt, dates as mdates


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
    Macro for formatting a datetime axis with control of day of the month
    labels.
    
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
    new_line:
        If True, sets the month on a new line after the day.
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
    
    Parameters
    ----------
    axis:
        The datetime axis to be formatted.
    include_year:
        If True, add the year to the first major tick as well.
    new_line:
        If True, set the month on a new line after the day.
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


def num_diff(sers:pd.Series, order:int=1) -> pd.Series:
    """
    A tool for very simple numerical differentiation. Importantly, it
    returns a series/list of the same length as the input
    series/iterables.
    """
    # Helper function #
    def sslopes(sers:pd.Series) -> pd.Series:
        """
        Numerical differentiaion of order 1.
        """
        xs = (mdates.date2num(sers.index) if type(sers.index)==pd.DatetimeIndex
              else sers.index)
        ys = sers.values
        out = []    
        for i,(x,y) in enumerate(zip(xs,ys)):
            if i<1:
                continue
            j = i-1
            datum = (y-ys[j])/(x-xs[j])
            # print(datum) #This was used for debugging.
            if len(out)<1:
                out.append(datum)
                stack = datum
            else:
                out.append((datum+stack)/2)
                stack = datum
                if len(out)==len(xs)-1: # We're up to the final entry.
                    out.append(datum)
        return pd.Series(index=sers.index, data=out, name=sers.name)
    # End of helper function #
    if (not type(order)==int) or order<1:
        errstr = "The order of the derivative must be an integer >= 1."
        raise ValueError(errstr)
    application_count = 0
    applicand = sers
    while application_count<order:
        applicand = sslopes(applicand)
        application_count += 1
    return applicand.rename(f"{applicand.name}.D{order}")
