import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
import my_mpl_finance as mpf
import determin_pair as dp
from datetime import datetime as dt
import os
import sys

print(pd.__path__)

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


#print(dfs)



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


rexs = {"m05":yoyuu}
lexs = {"m05":max(0,yoyuu-flamesize)}

for ashi in ashis:
    if ashi=="m05": continue
    rex = dfs["m05"]["matching_closeX_in_"+ashi][rexs["m05"]-1]
    rexs[ashi] = rex
    lexs[ashi] = max(0,rex-flamesize)

watching_ashi = "h01"


def create_ax(ashi):
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_main, linewidth = lw) #close時点で値がでるのでこうして1シフトしておくのが正しい(だよね？確認してない) #TODO
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_signal, linewidth = lw)
    mac_axs[ashi].grid(True,linestyle='dotted')
    mac_axs[ashi].tick_params(labelbottom=False)

    mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_mid, s=1) #close時点で値がでるのでこうして1シフトしておくのが正しい(だよね？確認してない) #TODO
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_short, s=1)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_long, s=1)
    candle_axs[ashi].set_xticks(np.arange(0,len(dfs[ashi]),trip))
    candle_axs[ashi].set_xticklabels(dfs[ashi].openTime[0:len(dfs[ashi]):trip].dt.strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

    candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])

    yhani = dfs[ashi].closePrice[lexs[ashi]:rexs[ashi]]
    candle_axs[ashi].grid(True,linestyle='dotted')

def move_tick_with_new_rex_in_m05(new_rex_in_m05):
    for ashi in ashis:
        rex = dfs["m05"]["matching_closeX_in_"+ashi][new_rex_in_m05-1]
        rexs[ashi] = rex
        lexs[ashi] = max(0,rex-flamesize)
        candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
    plt.draw()

def next_tick(event):
    move_tick_with_new_rex_in_m05(rexs["m05"]+1)

def prev_tick(event):
    move_tick_with_new_rex_in_m05(rexs["m05"]-1)


def get_func_of_switch_ashi(ashi):
    global watching_ashi
    def switch(event):
        global watching_ashi
        fig.delaxes(mac_axs[watching_ashi])
        fig.delaxes(candle_axs[watching_ashi])
        watching_ashi = ashi
        fig.add_axes(mac_axs[watching_ashi])
        fig.add_axes(candle_axs[watching_ashi])
        plt.draw()
    return switch





btn_m01 = Button(plt.axes([0.33, 0.04, 0.1, 0.035]), 'm01',color = 'black')
btn_m01.on_clicked(get_func_of_switch_ashi("m01"))
#btn_m05 = Button(plt.axes([0.44, 0.04, 0.1, 0.035]), 'm05',color = 'black')
#btn_m05.on_clicked(callback.get_func_of_switch_ashi("m05"))
btn_m15 = Button(plt.axes([0.55, 0.04, 0.1, 0.035]), 'm15',color = 'black')
btn_m15.on_clicked(get_func_of_switch_ashi("m15"))

btn_h01 = Button(plt.axes([0.33, 0.00, 0.1, 0.035]), 'h01',color = 'black')
btn_h01.on_clicked(get_func_of_switch_ashi("h01"))
btn_h04 = Button(plt.axes([0.44, 0.00, 0.1, 0.035]), 'h04',color = 'black')
btn_h04.on_clicked(get_func_of_switch_ashi("h04"))
btn_d01 = Button(plt.axes([0.55, 0.00, 0.1, 0.035]), 'd01',color = 'black')
btn_d01.on_clicked(get_func_of_switch_ashi("d01"))




btn_prev = Button(plt.axes([0.7, 0.0, 0.1, 0.075]), 'Prev',color = 'black')
btn_prev.on_clicked(prev_tick)
btn_next = Button(plt.axes([0.81, 0.0, 0.1, 0.075]), 'Next',color = 'black')
btn_next.on_clicked(next_tick)




ashi = "m05"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

ashi = watching_ashi
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

for ashi in ashis:
    create_ax(ashi)



plt.show()