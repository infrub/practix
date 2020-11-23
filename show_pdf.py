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
ashis = ["m01","m01","m15","h01","h04","d01"]

#pairname = "USDJPY" if len(sys.argv)<=1 else sys.argv[1]
#weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])
pairname = sys.argv[1]
weeki = int(sys.argv[2])

with open(f"raw_histories/{pairname}/style.json") as f:
    jsn1 = json.loads(f.read())
    ipv = jsn1["ipv"] # inverse of pips value (e.g. 100 in USDJPY)
    spread_pips = jsn1["spread_pips"] # spread_pips (単位はpips)

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
order_df["profitPipsPer5Min"] = order_df.profitPips / (order_df.exitX - order_df.entryX)
buy_order_df = order_df[order_df.entryStatus==1]
sell_order_df = order_df[order_df.entryStatus==-1]

mutter_df = pd.read_csv("logs/" + pairname + "/week_" + str(weeki).zfill(3) + ".mut", parse_dates=False)

#styles
priceLineWidth = 0.6
bgcolor = "#131313"


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}
gain_axs = {ashi:None for ashi in ashis}
mutter_axs = {ashi:None for ashi in ashis}

#(left,bottom,width,height)
acax_position = (0.05,0.33,0.9,0.64) # A面のcandle axの位置
amax_position = (0.05,0.20,0.9,0.13)
agax_position = (0.05,0.10,0.9,0.10)
atax_position = (0.05,0.03,0.9,0.07)

rexs = {}
lexs = {}




def create_ax(ashi):
    mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.7, alpha=1.0, colorup="#fa2200", colordown="#0077ff")
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_short, color="#f6ad48", s=1, label="SAR(5)") # 終値の単純移動平均(ピリオド5)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_mid, color="#aacf52", s=1, label="SAR(13)") # 終値の単純移動平均(ピリオド13)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_long, color="#00b1a9", s=1, label="SAR(25)") # 終値の単純移動平均(ピリオド25)
    candle_axs[ashi].set_xticks(np.arange(1,len(dfs[ashi]),trip)) # 1ずらしたほうが罫線のキリがよくなる
    candle_axs[ashi].set_xticklabels(dfs[ashi].openTime[1:len(dfs[ashi]):trip].dt.strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

    candle_axs[ashi].scatter(buy_order_df.entryX+0.25, buy_order_df.entryPrice,s=24,c='#ffbbbb',marker='>', label="INVIS_LABEL")
    candle_axs[ashi].scatter(buy_order_df.exitX-0.25, buy_order_df.exitPrice,s=24,c='#ffbbbb',marker='<', label="INVIS_LABEL")
    candle_axs[ashi].scatter(sell_order_df.entryX+0.25, sell_order_df.entryPrice,s=24,c='#bbbbff',marker='>', label="INVIS_LABEL")
    candle_axs[ashi].scatter(sell_order_df.exitX-0.25, sell_order_df.exitPrice,s=24,c='#bbbbff',marker='<', label="INVIS_LABEL")


    for orderi, order in buy_order_df.iterrows():
        mac_axs[ashi].axvspan(order.entryX, order.exitX, color="#552222")
    for orderi, order in sell_order_df.iterrows():
        mac_axs[ashi].axvspan(order.entryX, order.exitX, color="#222255")

    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_signal, color="lightslategrey", linewidth = 1.5, label="MACD(5,11,4) main") # MACD(5,11,4) sig
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_main, color="mediumvioletred", linewidth = 1.5, label="MACD(5,11,4) sig") # MACD(5,11,4) main
    mac_axs[ashi].grid(True,linestyle='dotted')
    mac_axs[ashi].tick_params(labelbottom=False)


    for orderi, order in buy_order_df.iterrows():
        gain_axs[ashi].axvspan(order.entryX, order.exitX, color="#552222")
    for orderi, order in sell_order_df.iterrows():
        gain_axs[ashi].axvspan(order.entryX, order.exitX, color="#222255")

    colors = []
    for orderi, order in order_df.iterrows():
        if order.profitPips < 0:
            colors.append("fuchsia") #"#b70868")
        else:
            colors.append("lime") #"#00a161")

    gain_axs[ashi].bar(order_df.entryX.values, order_df.profitPipsPer5Min, width=order_df.exitX-order_df.entryX, color=colors, align="edge")
    annoy = 999
    for orderi, order in order_df.iterrows():
        if order.profitPipsPer5Min < 0:
            annoy = 0.5
        else:
            annoy = -1.8
        gain_axs[ashi].annotate(f"{order.profitPips:+.1f}", ((order.entryX+order.exitX)/2-1, annoy), size=8, rotation=25)

    gain_axs[ashi].grid(True,linestyle='dotted')
    gain_axs[ashi].set_ylim(-3,3)
    gain_axs[ashi].set_ylabel("profit pips")
    gain_axs[ashi].set_yticks([0])
    gain_axs[ashi].set_yticklabels([""])
    gain_axs[ashi].tick_params(labelbottom=False)

    cnt = 1
    for mutteri, mutter in mutter_df.iterrows():
        if lexs["m01"] < mutter.nowX <= rexs["m01"]:
            mutter_axs[ashi].text(0.0, 1.0-cnt*0.3, f"{mutter.nowTime} {mutter.text}", size=12)
            cnt += 1


    candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
    miny = min(dfs[ashi].lowPrice[lexs[ashi]:rexs[ashi]])
    maxy = max(dfs[ashi].highPrice[lexs[ashi]:rexs[ashi]])
    buff = (maxy - miny)*0.05
    candle_axs[ashi].set_ylim(miny-buff,maxy+buff)

    yhani = dfs[ashi].closePrice[lexs[ashi]:rexs[ashi]]
    candle_axs[ashi].grid(True,linestyle='dotted')


    handlers1, labels1 = candle_axs[ashi].get_legend_handles_labels()
    handlers2, labels2 = mac_axs[ashi].get_legend_handles_labels()
    handlers3, labels3 = gain_axs[ashi].get_legend_handles_labels()
    handlers = []
    labels = []
    for handler,label in zip(handlers1 + handlers2 + handlers3, labels1 + labels2 + labels3):
        if label != "INVIS_LABEL":
            handlers.append(handler)
            labels.append(label)
    candle_axs[ashi].legend(handlers, labels, borderaxespad=0.)




def plot_top_page():
    all_len = len(order_df)
    all_score = np.sum(order_df.profitPips)

    won_order_df = order_df[order_df.profitPips>0]
    won_len = len(won_order_df)
    won_score = np.sum(won_order_df.profitPips)

    loss_order_df = order_df[order_df.profitPips<0]
    loss_len = len(loss_order_df)
    loss_score = np.sum(loss_order_df.profitPips)

    draw_order_df = order_df[order_df.profitPips==0]
    draw_len = len(draw_order_df)
    draw_score = np.sum(draw_order_df.profitPips)

    rowLabels = ["All","Won","Lost","Draw"]
    colLabels = ["Number", "Sum pips", "Mean pips"]
    cellTextss = [[f"{ all_len:>5}", f"{all_score:>9.2f}", f"{all_score/all_len:>8.3f}"],
                [f"{ won_len:>5}({int( won_len/all_len*100):>2}%)", f"{ won_score:>9.2f}", f"{ won_score/ won_len:>8.3f}"],
                [f"{loss_len:>5}({int(loss_len/all_len*100):>2}%)", f"{loss_score:>9.2f}", f"{loss_score/loss_len:>8.3f}"],
                [f"{draw_len:>5}({int(draw_len/all_len*100):>2}%)", f"{draw_score:>9.2f}", f"{draw_score/draw_len:>8.3f}"]]
    colWidths = [0.2,0.2,0.2]


    fig = plt.figure(figsize=(13,8))

    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)
    plt.tick_params(bottom=False, left=False, right=False, top=False)
    plt.text(0,0.8, pairname+" week_"+str(weeki).zfill(3), fontsize=30)
    table = plt.table(cellText=cellTextss, rowLabels=rowLabels, colLabels=colLabels, colWidths=colWidths, bbox=[0.1,0.0,0.8,0.7], loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(30)





def plot_and_save_all_page():
    pdf_filename = "logs/" + pairname + "/week_" + str(weeki).zfill(3) + ".pdf"
    pdf = PdfPages(pdf_filename)

    plt.style.use('default')
    plot_top_page()
    pdf.savefig()
    plt.close()

    ashi = "m01"

    for lex in trange(0, len(dfs[ashi]), flamesize):
        plt.style.use('dark_background')
        lexs[ashi] = lex
        rexs[ashi] = min(len(dfs[ashi]), lex+flamesize)
        fig = plt.figure(figsize=(13,8), num=pairname+" week_"+str(weeki).zfill(3), facecolor=bgcolor)
        mac_axs[ashi] = fig.add_axes(amax_position, facecolor=bgcolor)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi], facecolor=bgcolor)
        gain_axs[ashi] = fig.add_axes(agax_position, sharex=mac_axs[ashi], facecolor=bgcolor)
        mutter_axs[ashi] = fig.add_axes(atax_position, facecolor=bgcolor)
        mutter_axs[ashi].spines['top'].set_visible(False)
        mutter_axs[ashi].spines['bottom'].set_visible(False)
        mutter_axs[ashi].spines['left'].set_visible(False)
        mutter_axs[ashi].spines['right'].set_visible(False)
        mutter_axs[ashi].xaxis.set_visible(False)
        mutter_axs[ashi].yaxis.set_visible(False)
        create_ax(ashi)
        pdf.savefig()
        plt.close()

    pdf.close()


plot_and_save_all_page()