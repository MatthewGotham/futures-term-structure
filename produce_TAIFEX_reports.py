#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 01:41:53 2026

@author: matthew
"""

import pandas as pd
from json import loads
with open("contracts.json", "r") as file:
    contracts_dict = loads(file.read())


def generate_html(code:str, updated:str="") -> str:
    contract = contracts_dict[code]
    output = f"""
<html lang="en-GB">

<head>
    <title>TAIFEX {contract} Report</title>
</head>

<body>
    <h1 style="margin-left:auto; margin-right:auto; width:1600px">TAIFEX {contract}</h1>
    <h2 style="margin-left:auto; margin-right:auto; width:1600px">Last updated {updated}</h1>
<div style="margin-left:auto; margin-right:auto; width:1200px">
    <p>
        <video controls autoplay width="800px" style="padding-left: 100px;padding-right: 100px;">
            <source src="../animations/TAIFEX_{code}_curve_animation.mp4" type="video/mp4">
        </video>
    </p>
    <p>
        <img src="../graphs/TAIFEX_{code}_charts.png" width="1000px">
    </p>
</body>
</div>
    """
    return output

to_report = ["TX", "GDF", "BRF", "CDF", "RHF"]
for code in to_report:
    curve = pd.read_parquet(f"./TAIFEX_prices/TAIFEX_{code}_prices.parquet")
    updated = max(curve.index).strftime("%d %b %Y").lstrip("0")
    html = generate_html(code, updated)
    with open(f"./reports/TAIFEX_{code}_report.html", "w") as file:
        file.write(html)
