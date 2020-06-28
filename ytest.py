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

lw = 1.0
trip = 24
flamesize = 96
yoyuu = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDGBP" if len(sys.argv)<=1 else sys.argv[1]
weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])


dfs = {}
idxs = {}
for ashi in ashis:
    df = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)
    df["openTime"] = pd.to_datetime(df.openTime)
    df["closeTime"] = pd.to_datetime(df.closeTime)
    dfs[ashi] = df
    idxs[ashi] = np.arange(len(dfs[ashi].index))



candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}


print(dfs)



plt.style.use('dark_background')
fig = plt.figure(figsize=(12,7))


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}

acax_position = (0.05,0.35,0.4,0.6) # A面のcandle axの位置
amax_position = (0.05,0.15,0.4,0.2)
bcax_position = (0.55,0.35,0.4,0.6)
bmax_position = (0.55,0.15,0.4,0.2)

for ashi in ashis:
    if ashi == "m05":
        mac_axs[ashi] = fig.add_axes(amax_position)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi])
    else:
        mac_axs[ashi] = fig.add_axes(bmax_position)
        candle_axs[ashi] = fig.add_axes(bcax_position,sharex=mac_axs[ashi])
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])





rex_in_m05 = yoyuu
lex_in_m05 = max(0, rex_in_m05 - flamesize)
watching_ashi = "h01"


def create_aax(ashi):
    #nowpricetext = str(round(dfs[ashi].closePrice[self.rex_in_m05-1],5))
    #entrypricetext = str(self.entryprice)
    #pricetext = 'entryprice:' + entrypricetext + "\n" +'nowprice:' + nowpricetext
    #candle_axs[ashi].text(0.05,0.85,pricetext,transform=candle_axs[ashi].transAxes)

    mac_main = dfs[ashi].macd_main
    mac_signal = dfs[ashi].macd_signal
    mac_axs[ashi].plot(idxs[ashi]+1, mac_main, linewidth = lw) #close時点で値がでるのでこうして1シフトしておくのが正しい(だよね？確認してない) #TODO
    mac_axs[ashi].plot(idxs[ashi]+1, mac_signal, linewidth = lw)
    mac_axs[ashi].grid(True,linestyle='dotted')
    mac_axs[ashi].tick_params(labelbottom=False)

    mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_mid, s=1) #close時点で値がでるのでこうして1シフトしておくのが正しい(だよね？確認してない) #TODO
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_short, s=1)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_long, s=1)

    candle_axs[ashi].set_xlim(lex_in_m05,rex_in_m05)
    candle_axs[ashi].set_xticks(idxs[ashi][lex_in_m05:rex_in_m05+1:trip])
    candle_axs[ashi].set_xticklabels(dfs[ashi].openTime[lex_in_m05:rex_in_m05+1:trip].dt.strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small") #TODO

    yhani = dfs[ashi].closePrice[lex_in_m05:rex_in_m05]
    #candle_axs[ashi].set_ylim(min(yhani)-buff,max(yhani)+buff)
    candle_axs[ashi].grid(True,linestyle='dotted')



ashi = "m05"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])
create_aax(ashi)



plt.show()