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

lw = 1.0
trip = 20
ashis = ["5m","15m","60m","4h","1d","1m"]
times = 6

dt_now = '\n\n' + str(dt.now())
dp.writelog(dt_now)

pair = dp.pair()
nomalize,spread = dp.spnm(pair)
year = 2018
month = 9

initial_time_text = open("logs/nikki.txt").readlines()[-1]
flamesize = 144

dfs = {}
idxs = {}
for ashi in ashis:
    dfs[ashi] = pd.read_csv("raw_histories/" + pair + '/' + str(year) + '_' + str(month).zfill(2) + '/market_'+ashi+'.csv', index_col=0, parse_dates=True)
    idxs[ashi] = np.arange(len(dfs[ashi].index))

candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}





acax_position = (0.05,0.35,0.4,0.6) # A面のcandle axの位置
amax_position = (0.05,0.15,0.4,0.2)
bcax_position = (0.55,0.35,0.4,0.6)
bmax_position = (0.55,0.15,0.4,0.2)


plt.style.use('dark_background')


fig = plt.figure(figsize=(12,7))

for ashi in ashis:
    if ashi == "5m":
        mac_axs[ashi] = fig.add_axes(amax_position)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi])
    else:
        mac_axs[ashi] = fig.add_axes(bmax_position)
        candle_axs[ashi] = fig.add_axes(bcax_position,sharex=mac_axs[ashi])
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])



ashi = "5m"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

nowpricetext = str(round(dfs[ashi].closePrice[flamesize-1],5))
entrypricetext = ''
pricetext = 'entryprice:' + entrypricetext + "\n" +'nowprice:' + nowpricetext
candle_axs[ashi].text(0.05,0.85,pricetext,transform=candle_axs[ashi].transAxes)

mac_main = dfs[ashi].macd_main.shift()
mac_signal = dfs[ashi].macd_signal.shift()
mac_axs[ashi].plot(idxs[ashi], mac_main, linewidth = lw)
mac_axs[ashi].plot(idxs[ashi], mac_signal, linewidth = lw)
mainhani = dfs[ashi].macd_main[0:flamesize]
signalhani = dfs[ashi].macd_signal[0:flamesize]
y1hani = mainhani+signalhani

buff = 5.0e-04*dfs["5m"].closePrice[0]
mac_axs[ashi].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
mac_axs[ashi].grid(True,linestyle='dotted')
mac_axs[ashi].tick_params(labelbottom=False)

mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
MAmid = dfs[ashi].MA_mid.shift()
MAshort = dfs[ashi].MA_short.shift()
MAlong = dfs[ashi].MA_long.shift()
candle_axs[ashi].scatter(idxs[ashi], MAmid, s=1)
candle_axs[ashi].scatter(idxs[ashi], MAshort, s=1)
candle_axs[ashi].scatter(idxs[ashi], MAlong, s=1)

candle_axs[ashi].set_xlim(0,flamesize)
candle_axs[ashi].set_xticks(idxs[ashi][0:flamesize:trip])
candle_axs[ashi].set_xticklabels(dfs[ashi].index[0:flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

yhani = dfs[ashi].closePrice[0:flamesize]
candle_axs[ashi].set_ylim(min(yhani)-buff,max(yhani)+buff)
candle_axs[ashi].grid(True,linestyle='dotted')



fig.add_axes(mac_axs["60m"])
fig.add_axes(candle_axs["60m"])



class Index(object):
    lex_in_5m = 0 # 5mグラフにおける左端のx座標 left edge x-cood
    redn = date2num(dfs["5m"].index[0+flamesize]) # 5mグラフにおける右端のx座標が表す時間を数値化したもの right edge datetime number
    oneMind = 0
    entrytype = 0
    entryprice = 0
    oneMprice = 0
    oneMnow = dfs["1m"].index[0]
    entrytime = dfs["5m"].index[0]
    entrypricetext = ' '
    watching_ashi = "60m"


    def uooooo(self, ashi):
        fig.delaxes(mac_axs[self.watching_ashi])
        fig.delaxes(candle_axs[self.watching_ashi])
        self.watching_ashi = ashi
        fig.add_axes(mac_axs[ashi])
        fig.add_axes(candle_axs[ashi])

        rex_in_this_ashi = np.abs(np.asarray(date2num(dfs[ashi].index)) - self.redn).argmin() + 1

        if (date2num(dfs[ashi].index[rex_in_this_ashi]) - self.redn > 0):
            rex_in_this_ashi = rex_in_this_ashi-1
        lex_in_this_ashi = rex_in_this_ashi-flamesize
        if(lex_in_this_ashi<0):
            lex_in_this_ashi = 0

        nowdf = dfs[ashi][lex_in_this_ashi:rex_in_this_ashi]

        mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], nowdf.openPrice, nowdf.highPrice, nowdf.lowPrice, nowdf.closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
        candle_axs[ashi].scatter(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi], nowdf.MA_mid, s = 1)
        candle_axs[ashi].scatter(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi], nowdf.MA_short, s = 1)
        candle_axs[ashi].scatter(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi], nowdf.MA_long, s = 1)
        yhani = dfs[ashi].closePrice[lex_in_this_ashi:rex_in_this_ashi]
        candle_axs[ashi].set_ylim(min(yhani)-buff,max(yhani)+buff)
        candle_axs[ashi].grid(True,linestyle='dotted')
        candle_axs[ashi].set_xlim(0,rex_in_this_ashi-lex_in_this_ashi)
        candle_axs[ashi].set_xticks(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi:trip])
        candle_axs[ashi].set_xticklabels(dfs[ashi].index[lex_in_this_ashi:rex_in_this_ashi:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

        main = dfs[ashi].macd_main[lex_in_this_ashi:rex_in_this_ashi].shift()
        signal = dfs[ashi].macd_signal[lex_in_this_ashi:rex_in_this_ashi].shift()
        mac_axs[ashi].plot(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi], main)
        mac_axs[ashi].plot(idxs[ashi][0:rex_in_this_ashi-lex_in_this_ashi], signal)
        mainhani = dfs[ashi].macd_main[lex_in_this_ashi:rex_in_this_ashi]
        signalhani = dfs[ashi].macd_signal[lex_in_this_ashi:rex_in_this_ashi]
        y1hani = mainhani+signalhani
        mac_axs[ashi].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        mac_axs[ashi].grid(True,linestyle='dotted')
        mac_axs[ashi].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[rex_in_this_ashi-1],5))
        if(self.entrypricetext!=''):
            pips = self.entrytype*(round((dfs[ashi].closePrice[rex_in_this_ashi-1]-self.entryprice)*nomalize,3))-spread
            pipstext = str(pips)
            pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
        else:
            pricetext = 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs[ashi].texts:
            txt.set_visible(False)
        candle_axs[ashi].text(0.05,0.85,pricetext,transform=candle_axs[ashi].transAxes)

        plt.show()
    



    def get_func_of_switch_ashi(self, ashi):
        def switch(event):
            dp.writelog("switch_ashi "+ashi)
            self.uooooo(ashi)
        return switch



    def move_lex_in_5m(self, new_lex_in_5m):
        self.lex_in_5m = new_lex_in_5m
        i = self.lex_in_5m
        self.redn = date2num(dfs["5m"].index[i+flamesize])

        self.oneMind = 0
        ashi = "5m"
        candle_axs[ashi].set_xlim(i,i+flamesize)
        candle_axs[ashi].set_xticks(idxs[ashi][i:i+flamesize:trip])
        candle_axs[ashi].set_xticklabels(dfs[ashi].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
        yhani = dfs[ashi].closePrice[i:i+flamesize]
        candle_axs[ashi].set_ylim(min(yhani)-buff,max(yhani)+buff)
        #candle_axs[ashi].grid(True,linestyle='dotted')
        mainhani = dfs[ashi].macd_main[i:i+flamesize]
        signalhani = dfs[ashi].macd_signal[i:i+flamesize]
        y1hani = mainhani+signalhani

        mac_axs[ashi].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        mac_axs[ashi].grid(True,linestyle='dotted')
        mac_axs[ashi].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        if(enpricetext!=''):
            pips = self.entrytype*(round((dfs[ashi].closePrice[i+flamesize-1]-self.entryprice)*nomalize,3))-spread
            pipstext = str(pips)
            pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        else:
            pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs[ashi].texts:
            txt.set_visible(False)
        candle_axs[ashi].text(0.05,0.85,pricetext,transform=candle_axs["5m"].transAxes)
        plt.draw()

    def next(self, event):
        self.move_lex_in_5m(self.lex_in_5m+1)
        dp.writelog("next")

    def prev(self, event):
        self.move_lex_in_5m(self.lex_in_5m-1)
        dp.writelog("prev")

    def skip_to_time(self, date_text): 
        dn = date2num(dt.strptime(date_text, '%Y-%m-%d %H:%M'))
        new_rex_in_5m = np.abs(np.asarray(date2num(dfs[ashi].index)) - dn).argmin() + 1
        new_lex_in_5m = new_rex_in_5m - flamesize
        self.move_lex_in_5m(new_lex_in_5m)
        dp.writelog('skip_to_time ' + date_text)



    def buy(self, event):
        i = self.lex_in_5m
        self.entryprice = dfs["5m"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["5m"].texts:
            txt.set_visible(False)
        candle_axs["5m"].text(0.05,0.85,pricetext,transform=candle_axs["5m"].transAxes)
        self.entrytype = 1
        self.entrytime = dfs["5m"].index[i+flamesize-1]

        logtext = 'buy at ' + str(dfs["5m"].index[i+flamesize-1])
        dp.writelog(logtext)

    def sell(self, event):
        i = self.lex_in_5m
        self.entryprice = dfs["5m"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["5m"].texts:
            txt.set_visible(False)
        candle_axs["5m"].text(0.05,0.85,pricetext,transform=candle_axs["5m"].transAxes)
        self.entrytype = -1
        self.entrytime = dfs["5m"].index[i+flamesize-1]

        logtext = 'sell at ' + str(dfs["5m"].index[i+flamesize-1])
        dp.writelog(logtext)

    def exit(self, event):
        i = self.lex_in_5m
        enprice = self.entryprice
        etype = self.entrytype
        exprice = dfs["5m"].closePrice[i+flamesize-1]
        extime = dfs["5m"].index[i+flamesize-1]
        entime = self.entrytime
        self.entrypricetext = ''
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["5m"].texts:
            txt.set_visible(False)
        candle_axs["5m"].text(0.05,0.85,pricetext,transform=candle_axs["5m"].transAxes)
        pips = etype*(exprice-enprice)*nomalize - spread
        pips = round(pips, 1)

        text = str(entime) + "," + str(extime) + "," + str(pips) + "," + str(etype) + "\n"

        logfile_path = pair+'/'+'log_'+pair+'/'
        filename = 'log_'+year+'_'+month+'.csv'

        try:
            oup = open(logfile_path+filename,"a")
        except FileNotFoundError:
            os.makedirs(logfile_path)
            oup = open(logfile_path+filename,"a")
        oup.write(text)
        oup.close()

        logtext = 'exit at ' + str(extime)
        dp.writelog(logtext)

        


callback = Index()



# ボタンを設置。冗長だがボタンを入れた変数の束縛がなくなるとボタンが働かなくなるので仕方ない


btn_1m = Button(plt.axes([0.33, 0.04, 0.1, 0.035]), '1m',color = 'black')
btn_1m.on_clicked(callback.get_func_of_switch_ashi("1m"))
#btn_5m = Button(plt.axes([0.44, 0.04, 0.1, 0.035]), '5m',color = 'black')
#btn_5m.on_clicked(callback.get_func_of_switch_ashi("5m"))
btn_15m = Button(plt.axes([0.55, 0.04, 0.1, 0.035]), '15m',color = 'black')
btn_15m.on_clicked(callback.get_func_of_switch_ashi("15m"))

btn_60m = Button(plt.axes([0.33, 0.00, 0.1, 0.035]), '60m',color = 'black')
btn_60m.on_clicked(callback.get_func_of_switch_ashi("60m"))
btn_4h = Button(plt.axes([0.44, 0.00, 0.1, 0.035]), '4h',color = 'black')
btn_4h.on_clicked(callback.get_func_of_switch_ashi("4h"))
btn_1d = Button(plt.axes([0.55, 0.00, 0.1, 0.035]), '1d',color = 'black')
btn_1d.on_clicked(callback.get_func_of_switch_ashi("1d"))

btn_prev = Button(plt.axes([0.7, 0.0, 0.1, 0.075]), 'Previous',color = 'black')
btn_prev.on_clicked(callback.prev)
btn_next = Button(plt.axes([0.81, 0.0, 0.1, 0.075]), 'Next',color = 'black')
btn_next.on_clicked(callback.next)

btn_buy = Button(plt.axes([0.0, 0.0, 0.1, 0.075]), 'Buy',color = 'black')
btn_buy.on_clicked(callback.buy)
btn_sell = Button(plt.axes([0.11, 0.0, 0.1, 0.075]), 'Sell',color = 'black')
btn_sell.on_clicked(callback.sell)
btn_exit = Button(plt.axes([0.22, 0.0, 0.1, 0.075]), 'Exit',color = 'black')
btn_exit.on_clicked(callback.exit)

tbx_skip = TextBox(plt.axes([0.6, 0.08, 0.4, 0.035]), '', color = 'green', initial = initial_time_text)
tbx_skip.on_submit(callback.skip_to_time)

plt.show()
