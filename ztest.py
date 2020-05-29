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
    idxs[ashi] = [x for x in range(len(dfs[ashi].index))]

axs = {ashi:[None,None] for ashi in ashis}
graphs = {ashi:[None,None] for ashi in ashis}


plt.style.use('dark_background')


ashi = "5m"
fig = plt.figure(ashi)

axs[ashi][1] = fig.add_axes((0.05,0.15,0.9,0.2))
axs[ashi][0] = fig.add_axes((0.05,0.35,0.9,0.6),sharex=axs[ashi][1])

nowpricetext = str(round(dfs[ashi].closePrice[flamesize-1],5))
entrypricetext = ''
pricetext = 'entryprice:' + entrypricetext + "\n" +'nowprice:' + nowpricetext
axs[ashi][0].text(0.05,0.85,pricetext,transform=axs[ashi][0].transAxes)

mac_main = dfs[ashi].macd_main.shift()
mac_signal = dfs[ashi].macd_signal.shift()
graphs[ashi][1] = axs[ashi][1].plot(idxs[ashi], mac_main, linewidth = lw)
graphs[ashi][1] = axs[ashi][1].plot(idxs[ashi], mac_signal, linewidth = lw)
mainhani = dfs[ashi].macd_main[0:flamesize]
signalhani = dfs[ashi].macd_signal[0:flamesize]
y1hani = mainhani+signalhani

buff = 5.0e-04*dfs["5m"].closePrice[0]
axs[ashi][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
axs[ashi][1].grid(True,linestyle='dotted')
axs[ashi][1].tick_params(labelbottom=False)

graphs[ashi][0] = mpf.candlestick2_ohlc_indexed_by_openTime(axs[ashi][0], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
MAmid = dfs[ashi].MA_mid.shift()
MAshort = dfs[ashi].MA_short.shift()
MAlong = dfs[ashi].MA_long.shift()
graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi], MAmid, s=1)
graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi], MAshort, s=1)
graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi], MAlong, s=1)

axs[ashi][0].set_xlim(idxs[ashi][0],idxs[ashi][flamesize])
axs[ashi][0].set_xticks(idxs[ashi][0:flamesize:trip])
axs[ashi][0].set_xticklabels(dfs[ashi].index[0:flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

yhani = dfs[ashi].closePrice[0:flamesize]
axs[ashi][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
axs[ashi][0].grid(True,linestyle='dotted')


class Index(object):
    ind = 0
    oneMind = 0
    entrytype = 0
    entryprice = 0
    oneMprice = 0
    oneMnow = dfs["1m"].index[0]
    entrytime = dfs["5m"].index[0]
    entrypricetext = ' '

    def prepare_times(self, ashi, i):
        now = date2num(dfs["5m"].index[i+flamesize])
        fig = plt.figure(ashi)
        axs[ashi][1] = fig.add_axes((0.05,0.15,0.9,0.2))
        axs[ashi][0] = fig.add_axes((0.05,0.35,0.9,0.6),sharex=axs[ashi][1])
        idx = np.abs(np.asarray(date2num(dfs[ashi].index)) - now).argmin() + 1
        if (date2num(dfs[ashi].index[idx]) - now > 0):
            idx = idx-1
        start = idx-flamesize
        if(start<0):
            start = 0

        return start,idx

    def show_times(self, ashi,start, idx):
        start = idx-flamesize
        if(start<0):
            start = 0
        nowdf = dfs[ashi][start:idx]

        graphs[ashi][0] = mpf.candlestick2_ohlc_indexed_by_openTime(axs[ashi][0], nowdf.openPrice, nowdf.highPrice, nowdf.lowPrice, nowdf.closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
        graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi][0:idx-start], nowdf.MA_mid, s = 1)
        graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi][0:idx-start], nowdf.MA_short, s = 1)
        graphs[ashi][0] = axs[ashi][0].scatter(idxs[ashi][0:idx-start], nowdf.MA_long, s = 1)
        yhani = dfs[ashi].closePrice[start:idx]
        axs[ashi][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
        axs[ashi][0].grid(True,linestyle='dotted')
        axs[ashi][0].set_xlim(idxs[ashi][0],idxs[ashi][idx-start])
        axs[ashi][0].set_xticks(idxs[ashi][0:idx-start:trip])
        axs[ashi][0].set_xticklabels(dfs[ashi].index[start:idx:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

        main = dfs[ashi].macd_main[start:idx].shift()
        signal = dfs[ashi].macd_signal[start:idx].shift()
        graphs[ashi][1] = axs[ashi][1].plot(idxs[ashi][0:idx-start], main)
        graphs[ashi][1] = axs[ashi][1].plot(idxs[ashi][0:idx-start], signal)
        mainhani = dfs[ashi].macd_main[start:idx]
        signalhani = dfs[ashi].macd_signal[start:idx]
        y1hani = mainhani+signalhani
        axs[ashi][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        axs[ashi][1].grid(True,linestyle='dotted')
        axs[ashi][1].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[idx-1],5))
        if(self.entrypricetext!=''):
            pips = self.entrytype*(round((dfs[ashi].closePrice[idx-1]-self.entryprice)*nomalize,3))-spread
            pipstext = str(pips)
            pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
        else:
            pricetext = 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs[ashi][0].texts:
            txt.set_visible(False)
        axs[ashi][0].text(0.05,0.85,pricetext,transform=axs[ashi][0].transAxes)

        plt.show()
    



    def get_func_of_switch_ashi(self, ashi):
        def switch(event):
            dp.writelog("switch_ashi "+ashi)
            i = self.ind
            start, idx = self.prepare_times(ashi,i)
            self.show_times(ashi, start, idx)
            plt.figure(0)
        return switch



    def next(self, event):
        self.ind += 1
        i = self.ind
        self.oneMind = 0
        ashi = "5m"
        axs[ashi][0].set_xlim(idxs[ashi][i],idxs[ashi][i+flamesize])
        axs[ashi][0].set_xticks(idxs[ashi][i:i+flamesize:trip])
        axs[ashi][0].set_xticklabels(dfs[ashi].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
        yhani = dfs[ashi].closePrice[i:i+flamesize]
        axs[ashi][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
        #axs[ashi][0].grid(True,linestyle='dotted')
        mainhani = dfs[ashi].macd_main[i:i+flamesize]
        signalhani = dfs[ashi].macd_signal[i:i+flamesize]
        y1hani = mainhani+signalhani

        axs[ashi][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        axs[ashi][1].grid(True,linestyle='dotted')
        axs[ashi][1].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        if(enpricetext!=''):
            pips = self.entrytype*(round((dfs[ashi].closePrice[i+flamesize-1]-self.entryprice)*nomalize,3))-spread
            pipstext = str(pips)
            pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        else:
            pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs[ashi][0].texts:
            txt.set_visible(False)
        axs[ashi][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        plt.draw()

        logtext = 'next'
        dp.writelog(logtext)

    def prev(self, event):
        self.ind -= 1
        i = self.ind
        self.oneMind = 0
        ashi = "5m"
        axs[ashi][0].set_xlim(idxs[ashi][i],idxs[ashi][i+flamesize])
        axs[ashi][0].set_xticks(idxs[ashi][i:i+flamesize:trip])
        axs[ashi][0].set_xticklabels(dfs[ashi].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
        yhani = dfs[ashi].closePrice[i:i+flamesize]
        axs[ashi][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
        #axs[ashi][0].grid(True,linestyle='dotted')
        mainhani = dfs[ashi].macd_main[i:i+flamesize]
        signalhani = dfs[ashi].macd_signal[i:i+flamesize]
        y1hani = mainhani+signalhani

        axs[ashi][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        axs[ashi][1].grid(True,linestyle='dotted')
        axs[ashi][1].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        if(enpricetext!=''):
            pips = self.entrytype*(round((dfs[ashi].closePrice[i+flamesize-1]-self.entryprice)*nomalize,3))-spread
            pipstext = str(pips)
            pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        else:
            pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs[ashi][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        plt.draw()

        logtext = 'previous'
        dp.writelog(logtext)


    def skip_to_time(self, text):
        ashi = "5m"
        date = text
        future = date2num(dt.strptime(date, '%Y-%m-%d %H:%M'))
        idx = np.abs(np.asarray(date2num(dfs[ashi].index)) - future).argmin() + 1
        i = idx - flamesize
        self.ind = i
        axs[ashi][0].set_xlim(idxs[ashi][i],idxs[ashi][i+flamesize])
        axs[ashi][0].set_xticks(idxs[ashi][i:i+flamesize:trip])
        axs[ashi][0].set_xticklabels(dfs[ashi].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
        yhani = dfs[ashi].closePrice[i:i+flamesize]
        axs[ashi][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
        #axs[ashi][0].grid(True,linestyle='dotted')
        mainhani = dfs[ashi].macd_main[i:i+flamesize]
        signalhani = dfs[ashi].macd_signal[i:i+flamesize]
        y1hani = mainhani+signalhani

        axs[ashi][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
        axs[ashi][1].grid(True,linestyle='dotted')
        axs[ashi][1].tick_params(labelbottom=False)

        nowpricetext = str(round(dfs[ashi].closePrice[i+flamesize-1],5))
        enpricetext = ''
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs[ashi][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        plt.draw()
        logtext = 'move to ' + str(date)
        dp.writelog(logtext)



    def buy(self, event):
        i = self.ind
        self.entryprice = dfs["5m"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        self.entrytype = 1
        self.entrytime = dfs["5m"].index[i+flamesize-1]

        logtext = 'buy at ' + str(dfs["5m"].index[i+flamesize-1])
        dp.writelog(logtext)

    def sell(self, event):
        i = self.ind
        self.entryprice = dfs["5m"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        self.entrytype = -1
        self.entrytime = dfs["5m"].index[i+flamesize-1]

        logtext = 'sell at ' + str(dfs["5m"].index[i+flamesize-1])
        dp.writelog(logtext)

    def exit(self, event):
        i = self.ind
        enprice = self.entryprice
        etype = self.entrytype
        exprice = dfs["5m"].closePrice[i+flamesize-1]
        extime = dfs["5m"].index[i+flamesize-1]
        entime = self.entrytime
        self.entrypricetext = ''
        nowpricetext = str(round(dfs["5m"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
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


    def oneMbuy(self, event):

        self.entryprice = self.oneMprice
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = self.entrypricetext
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        self.entrytype = 1
        self.entrytime = self.oneMnow

        logtext = 'buy at ' + str(self.oneMnow)
        dp.writelog(logtext)

    def oneMsell(self, event):

        self.entryprice = self.oneMprice
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = self.entrypricetext
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
        self.entrytype = -1
        self.entrytime = self.oneMnow

        logtext = 'sell at ' + str(self.oneMnow)
        dp.writelog(logtext)

    def oneMexit(self, event):
        enprice = self.entryprice
        etype = self.entrytype
        exprice = self.oneMprice
        extime = self.oneMnow
        entime = self.entrytime
        self.entrypricetext = ''
        nowpricetext = str(exprice)
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in axs["5m"][0].texts:
            txt.set_visible(False)
        axs["5m"][0].text(0.05,0.85,pricetext,transform=axs["5m"][0].transAxes)
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

btn_1mbuy = Button(plt.axes([0.0, 0.11, 0.1, 0.035]), '1Buy',color = 'black')
btn_1mbuy.on_clicked(callback.oneMbuy)
btn_1msell = Button(plt.axes([0.11, 0.11, 0.1, 0.035]), '1Sell',color = 'black')
btn_1msell.on_clicked(callback.oneMsell)
btn_1mexit = Button(plt.axes([0.22, 0.11, 0.1, 0.035]), '1Exit',color = 'black')
btn_1mexit.on_clicked(callback.oneMexit)

tbx_skip = TextBox(plt.axes([0.6, 0.08, 0.4, 0.035]), '', color = 'green', initial = initial_time_text)
tbx_skip.on_submit(callback.skip_to_time)

plt.show()
