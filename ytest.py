import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
from matplotlib.dates import date2num
import my_mpl_finance as mpf
import determin_pair as dp
from datetime import datetime as dt
import os
import sys


flamesize = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDGBP" if len(sys.argv)<=1 else sys.argv[1]
weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])


dfs = {}
for ashi in ashis:
    dfs[ashi] = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)


print(dfs)



plt.style.use('dark_background')
fig = plt.figure(figsize=(12,7))


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}

bcax_position = (0.55,0.35,0.4,0.6)
bmax_position = (0.55,0.15,0.4,0.2)

for ashi in ashis:
    mac_axs[ashi] = fig.add_axes(bmax_position)
    candle_axs[ashi] = fig.add_axes(bcax_position)
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])