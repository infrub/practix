import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
import my_mpl_finance as mpf
import determin_pair as dp
from datetime import datetime as dt
import os
import sys
import json



lw = 1.0
trip = 24
flamesize = 96
yoyuu = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDGBP" if len(sys.argv)<=1 else sys.argv[1]
weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])
with open(f"raw_histories/{pairname}/style.json") as f:
    jsn = json.loads(f.read())
    ipv = jsn["ipv"] # inverse of pips value (e.g. 100 in USDJPY)
    spread = jsn["spread"] # spread (単位はpips)


dfs = {}
idxs = {}
for ashi in ashis:
    df = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)
    df["openTime"] = pd.to_datetime(df.openTime)
    df["closeTime"] = pd.to_datetime(df.closeTime)
    dfs[ashi] = df
    idxs[ashi] = np.arange(len(dfs[ashi].index))


plt.style.use('dark_background')
fig = plt.figure(figsize=(12,7))


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}

#(left,bottom,width,height)
acax_position = (0.05,0.33,0.4,0.6) # A面のcandle axの位置
amax_position = (0.05,0.13,0.4,0.2)
bcax_position = (0.55,0.33,0.4,0.6)
bmax_position = (0.55,0.13,0.4,0.2)
tbox_position = (0.05,0.93,0.9,0.05)

for ashi in ashis:
    if ashi == "m05":
        mac_axs[ashi] = fig.add_axes(amax_position)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi])
    else:
        mac_axs[ashi] = fig.add_axes(bmax_position)
        candle_axs[ashi] = fig.add_axes(bcax_position,sharex=mac_axs[ashi])
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])

tbax = fig.add_axes(tbox_position)
tbax.spines['top'].set_visible(False)
tbax.spines['bottom'].set_visible(False)
tbax.spines['left'].set_visible(False)
tbax.spines['right'].set_visible(False)
tbax.xaxis.set_visible(False)
tbax.yaxis.set_visible(False)


rexs = {"m05":yoyuu}
lexs = {"m05":max(0,yoyuu-flamesize)}

for ashi in ashis:
    if ashi=="m05": continue
    rex = dfs["m05"]["matching_closeX_in_"+ashi][rexs["m05"]-1]
    rexs[ashi] = rex
    lexs[ashi] = max(0,rex-flamesize)

watching_ashi = "h01"
entryStatus = "NOENT"
entryTime = None
entryPrice = None
entryX = None
lastProfit = 0
sumProfit = 0


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

    update_text()


def move_tick_with_new_rex_in_m05(new_rex_in_m05):
    for ashi in ashis:
        rex = dfs["m05"]["matching_closeX_in_"+ashi][new_rex_in_m05-1]
        rexs[ashi] = rex
        lexs[ashi] = max(0,rex-flamesize)
        candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
    update_text()
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
        btns[watching_ashi].color = "black"
        watching_ashi = ashi
        fig.add_axes(mac_axs[watching_ashi])
        fig.add_axes(candle_axs[watching_ashi])
        btns[watching_ashi].color = "lightseagreen"
        plt.draw()
    return switch


def update_text():
    for ashi in ashis:
        while len(candle_axs[ashi].texts) > 0:
            del candle_axs[ashi].texts[-1]
    while len(tbax.texts) > 0:
        del tbax.texts[-1]

    nowPrice = dfs['m05'].closePrice[rexs['m05']-1]

    ctext = f"now: {nowPrice:.5f}"
    ttext = f"sum: {sumProfit:.1f} pips "
    if entryStatus == "NOENT":
        ttext += f"    last: {sumProfit:.1f} pips"
    elif entryStatus == "LONG":
        ctext += f"\nbought: {entryPrice:.5f}"
        ttext += f"    latent: {(nowPrice-entryPrice)*ipv - spread :.1f} pips"
    elif entryStatus == "SHORT":
        ctext += f"\nsold: {entryPrice:.5f}"
        ttext += f"    latent: {(entryPrice-nowPrice)*ipv - spread :.1f} pips"

    for ashi in ashis:
        candle_axs[ashi].text(0.05,0.95,ctext,verticalalignment='top',transform=candle_axs[ashi].transAxes)
    tbax.text(0,0.5,ttext,verticalalignment="center",horizontalalignment="left")



def buy(event):
    global entryStatus, entryPrice, entryTime
    if entryStatus != "NOENT": return

    entryStatus = "LONG"
    entryPrice = dfs["m05"].closePrice[rexs["m05"]-1]
    entryTime = dfs["m05"].closeTime[rexs["m05"]-1]

    update_text()

def sell(event):
    global entryStatus, entryPrice, entryTime
    if entryStatus != "NOENT": return

    entryStatus = "SHORT"
    entryPrice = dfs["m05"].closePrice[rexs["m05"]-1]
    entryTime = dfs["m05"].closeTime[rexs["m05"]-1]

    update_text()

def exit(event):
    global entryStatus, entryPrice, entryTime, lastProfit, sumProfit
    if entryStatus == "NOENT":
        return

    elif entryStatus == "LONG":
        exitPrice = dfs["m05"].closePrice[rexs["m05"]-1]
        exitTime = dfs["m05"].closeTime[rexs["m05"]-1]
        lastProfit = (exitPrice-entryPrice)*ipv - spread

    elif entryStatus == "SHORT":
        exitPrice = dfs["m05"].closePrice[rexs["m05"]-1]
        exitTime = dfs["m05"].closeTime[rexs["m05"]-1]
        lastProfit = (entryPrice-exitPrice)*ipv - spread

    entryStatus = "NOENT"
    sumProfit += lastProfit

    update_text()




btn_buy = Button(plt.axes([0.05, 0.03, 0.1, 0.075]), 'Buy',color = 'black')
btn_buy.on_clicked(buy)
btn_sell = Button(plt.axes([0.16, 0.03, 0.1, 0.075]), 'Sell',color = 'black')
btn_sell.on_clicked(sell)
btn_exit = Button(plt.axes([0.27, 0.03, 0.1, 0.075]), 'Exit',color = 'black')
btn_exit.on_clicked(exit)

btn_prev = Button(plt.axes([0.44, 0.03, 0.055, 0.075]), 'Prev',color = 'black')
btn_prev.on_clicked(prev_tick)
btn_next = Button(plt.axes([0.505, 0.03, 0.055, 0.075]), 'Next',color = 'black')
btn_next.on_clicked(next_tick)

btns = {}
btns["m01"] = Button(plt.axes([0.65, 0.03, 0.045, 0.075]), 'm01',color = 'black')
btns["m01"].on_clicked(get_func_of_switch_ashi("m01"))
btn_dummy1 = Button(plt.axes([0.70, 0.03, 0.045, 0.075]), '',color = 'black')
btn_dummy1.on_clicked(lambda x: x)
btns["m15"] = Button(plt.axes([0.75, 0.03, 0.045, 0.075]), 'm15',color = 'black')
btns["m15"].on_clicked(get_func_of_switch_ashi("m15"))
btns["h01"] = Button(plt.axes([0.80, 0.03, 0.045, 0.075]), 'h01',color = 'black')
btns["h01"].on_clicked(get_func_of_switch_ashi("h01"))
btns["h04"] = Button(plt.axes([0.85, 0.03, 0.045, 0.075]), 'h04',color = 'black')
btns["h04"].on_clicked(get_func_of_switch_ashi("h04"))
btns["d01"] = Button(plt.axes([0.90, 0.03, 0.045, 0.075]), 'd01',color = 'black')
btns["d01"].on_clicked(get_func_of_switch_ashi("d01"))





ashi = "m05"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

ashi = watching_ashi
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])
btns[watching_ashi].color = "lightseagreen"

for ashi in ashis:
    create_ax(ashi)



plt.show()