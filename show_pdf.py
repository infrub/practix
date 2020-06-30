#取引結果など表示　5分足+取引結果+MACD5分
#coding:utf-8
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import my_mpl_finance as mpf
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import trange
from datetime import datetime, timedelta
from math import floor
import json

pd.options.display.max_columns = 20
pd.options.display.width = 160
MAX_PDF_PAGE = 100









trip = 24
flamesize = 144
yoyuu = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDJPY" if len(sys.argv)<=1 else sys.argv[1]
weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])
with open(f"raw_histories/{pairname}/style.json") as f:
    jsn1 = json.loads(f.read())
    ipv = jsn1["ipv"] # inverse of pips value (e.g. 100 in USDJPY)
    spread = jsn1["spread"] # spread (単位はpips)

def textizerate(x):
    if ipv == 100: return f"{x:.3f}"
    elif ipv == 10000: return f"{x:.5f}"





dfs = {}
idxs = {}
for ashi in ashis:
    df = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)
    df["openTime"] = pd.to_datetime(df.openTime)
    df["closeTime"] = pd.to_datetime(df.closeTime)
    dfs[ashi] = df
    idxs[ashi] = np.arange(len(dfs[ashi].index))

order_df = pd.read_csv("logs/" + pairname + "/week_" + str(weeki).zfill(3) + ".csv", parse_dates=True)
buy_order_df = order_df[order_df.entryStatus==1]
sell_order_df = order_df[order_df.entryStatus==-1]

#styles
priceLineWidth = 0.6
bgcolor = "#131313"
plt.style.use('dark_background')


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}

#(left,bottom,width,height)
acax_position = (0.05,0.33,0.9,0.6) # A面のcandle axの位置
amax_position = (0.05,0.13,0.9,0.2)

rexs = {}
lexs = {}




def create_ax(ashi):
    mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.7, alpha=1.0, colorup="#fa2200", colordown="#0077ff")
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_short, color="#f6ad48", s=1) # 終値の単純移動平均(ピリオド5)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_mid, color="#aacf52", s=1) # 終値の単純移動平均(ピリオド13)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_long, color="#00b1a9", s=1) # 終値の単純移動平均(ピリオド25)
    candle_axs[ashi].set_xticks(np.arange(0,len(dfs[ashi]),trip))
    candle_axs[ashi].set_xticklabels(dfs[ashi].openTime[0:len(dfs[ashi]):trip].dt.strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

    candle_axs[ashi].scatter(buy_order_df.entryX+0.25, buy_order_df.entryPrice,s=24,c='#ffbbbb',marker='>',label="Buy Entry")
    candle_axs[ashi].scatter(buy_order_df.exitX-0.25, buy_order_df.exitPrice,s=24,c='#ffbbbb',marker='<', label="Buy Settle")
    candle_axs[ashi].scatter(sell_order_df.entryX+0.25, sell_order_df.entryPrice,s=24,c='#bbbbff',marker='>', label="Sell Entry")
    candle_axs[ashi].scatter(sell_order_df.exitX-0.25, sell_order_df.exitPrice,s=24,c='#bbbbff',marker='<', label="Sell Settle")


    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_main, color="mediumvioletred", linewidth = 1.5) # MACD(5,11,4) main
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_signal, color="lightslategrey", linewidth = 1.5) # MACD(5,11,4) sig
    mac_axs[ashi].grid(True,linestyle='dotted')
    mac_axs[ashi].tick_params(labelbottom=False)

    for i in range(len(buy_order_df)):
        mac_axs[ashi].axvspan(buy_order_df.iloc[i].entryX, buy_order_df.iloc[i].exitX, color="#552222")
    for i in range(len(sell_order_df)):
        mac_axs[ashi].axvspan(sell_order_df.iloc[i].entryX, sell_order_df.iloc[i].exitX, color="#222255")




    candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
    miny = min(dfs[ashi].lowPrice[lexs[ashi]:rexs[ashi]])
    maxy = max(dfs[ashi].highPrice[lexs[ashi]:rexs[ashi]])
    buff = (maxy - miny)*0.05
    candle_axs[ashi].set_ylim(miny-buff,maxy+buff)

    yhani = dfs[ashi].closePrice[lexs[ashi]:rexs[ashi]]
    candle_axs[ashi].grid(True,linestyle='dotted')



def plot_and_save_all_page():
    pdf_filename = "logs/" + pairname + "/week_" + str(weeki).zfill(3) + ".pdf"
    pdf = PdfPages(pdf_filename)

    """
    plot_top_page()
    pdf.savefig()
    plt.close()
    """

    ashi = "m05"

    for lex in trange(0, len(dfs[ashi]), flamesize):
        lexs[ashi] = lex
        rexs[ashi] = min(len(dfs[ashi]), lex+flamesize)
        fig = plt.figure(figsize=(12,7), num=f"{pairname} week_"+ str(weeki).zfill(3), facecolor=bgcolor)
        mac_axs[ashi] = fig.add_axes(amax_position, facecolor=bgcolor)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi], facecolor=bgcolor)
        create_ax(ashi)
        pdf.savefig()
        plt.close()

    pdf.close()


plot_and_save_all_page()