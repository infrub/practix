import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
from matplotlib.dates import date2num
import my_mpl_finance as mpf
from datetime import datetime as dt
import os
import sys

lw = 1.0
trip = 20

flamesize = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDGBP" if len(sys.argv)<=1 else sys.argv[1]
weeki = 0 if len(sys.argv)<=2 else int(sys.argv[2])
nomalize,spread = 10000.0, 1.0

initial_time_text = open("logs/nikki.txt").readlines()[-1]
def writelog(text):
    oup = open("logs/loglog.dat","a")
    logtext = text + '\n'
    oup.write(logtext)
    oup.close()
writelog('\n\n' + str(dt.now()))


dfs = {}
idxs = {}
for ashi in ashis:
    dfs[ashi] = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)
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
    if ashi == "m05":
        mac_axs[ashi] = fig.add_axes(amax_position)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi])
    else:
        mac_axs[ashi] = fig.add_axes(bmax_position)
        candle_axs[ashi] = fig.add_axes(bcax_position,sharex=mac_axs[ashi])
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])




buff = 5.0e-04*dfs["m05"].closePrice[0]



class Index(object):
    lex_in_m05 = 0 # m05グラフにおける左端のx座標 left edge x-cood
    redn = date2num(dfs["m05"].index[0+flamesize]) # m05グラフにおける右端のx座標が表す時間を数値化したもの right edge datetime number
    entrytype = 0
    entryprice = 0
    entrytime = dfs["m05"].index[0]
    entrypricetext = ' '
    watching_ashi = "h01"





    def create_aax(self, ashi):
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



    def create_bax(self, ashi):
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




    def get_func_of_switch_ashi(self, ashi):
        def switch(event):
            writelog("switch_ashi "+ashi)
            fig.delaxes(mac_axs[self.watching_ashi])
            fig.delaxes(candle_axs[self.watching_ashi])
            self.watching_ashi = ashi
            fig.add_axes(mac_axs[ashi])
            fig.add_axes(candle_axs[ashi])
            self.create_bax(ashi)
            plt.show()
        return switch



    def move_lex_in_m05(self, new_lex_in_m05):
        self.lex_in_m05 = new_lex_in_m05
        i = self.lex_in_m05
        self.redn = date2num(dfs["m05"].index[i+flamesize])

        ashi = "m05"
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
        candle_axs[ashi].text(0.05,0.85,pricetext,transform=candle_axs["m05"].transAxes)
        plt.draw()

    def next(self, event):
        self.move_lex_in_m05(self.lex_in_m05+1)
        writelog("next")

    def prev(self, event):
        self.move_lex_in_m05(self.lex_in_m05-1)
        writelog("prev")

    def skip_to_time(self, date_text): 
        dn = date2num(dt.strptime(date_text, '%Y-%m-%d %H:%M'))
        new_rex_in_m05 = np.abs(np.asarray(date2num(dfs[ashi].index)) - dn).argmin() + 1
        new_lex_in_m05 = new_rex_in_m05 - flamesize
        self.move_lex_in_m05(new_lex_in_m05)
        writelog('skip_to_time ' + date_text)



    def buy(self, event):
        i = self.lex_in_m05
        self.entryprice = dfs["m05"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["m05"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["m05"].texts:
            txt.set_visible(False)
        candle_axs["m05"].text(0.05,0.85,pricetext,transform=candle_axs["m05"].transAxes)
        self.entrytype = 1
        self.entrytime = dfs["m05"].index[i+flamesize-1]

        logtext = 'buy at ' + str(dfs["m05"].index[i+flamesize-1])
        writelog(logtext)

    def sell(self, event):
        i = self.lex_in_m05
        self.entryprice = dfs["m05"].closePrice[i+flamesize-1]
        self.entrypricetext = str(round(self.entryprice,5))
        nowpricetext = str(round(dfs["m05"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["m05"].texts:
            txt.set_visible(False)
        candle_axs["m05"].text(0.05,0.85,pricetext,transform=candle_axs["m05"].transAxes)
        self.entrytype = -1
        self.entrytime = dfs["m05"].index[i+flamesize-1]

        logtext = 'sell at ' + str(dfs["m05"].index[i+flamesize-1])
        writelog(logtext)

    def exit(self, event):
        i = self.lex_in_m05
        enprice = self.entryprice
        etype = self.entrytype
        exprice = dfs["m05"].closePrice[i+flamesize-1]
        extime = dfs["m05"].index[i+flamesize-1]
        entime = self.entrytime
        self.entrypricetext = ''
        nowpricetext = str(round(dfs["m05"].closePrice[i+flamesize-1],5))
        enpricetext = self.entrypricetext
        pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
        for txt in candle_axs["m05"].texts:
            txt.set_visible(False)
        candle_axs["m05"].text(0.05,0.85,pricetext,transform=candle_axs["m05"].transAxes)
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
        writelog(logtext)

        


callback = Index()


ashi = "m05"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])
callback.create_aax(ashi)

ashi = "h01"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])
callback.create_bax(ashi)






# ボタンを設置。冗長だがボタンを入れた変数の束縛がなくなるとボタンが働かなくなるので仕方ない


btn_m01 = Button(plt.axes([0.33, 0.04, 0.1, 0.035]), 'm01',color = 'black')
btn_m01.on_clicked(callback.get_func_of_switch_ashi("m01"))
#btn_m05 = Button(plt.axes([0.44, 0.04, 0.1, 0.035]), 'm05',color = 'black')
#btn_m05.on_clicked(callback.get_func_of_switch_ashi("m05"))
btn_m15 = Button(plt.axes([0.55, 0.04, 0.1, 0.035]), 'm15',color = 'black')
btn_m15.on_clicked(callback.get_func_of_switch_ashi("m15"))

btn_h01 = Button(plt.axes([0.33, 0.00, 0.1, 0.035]), 'h01',color = 'black')
btn_h01.on_clicked(callback.get_func_of_switch_ashi("h01"))
btn_h04 = Button(plt.axes([0.44, 0.00, 0.1, 0.035]), 'h04',color = 'black')
btn_h04.on_clicked(callback.get_func_of_switch_ashi("h04"))
btn_d01 = Button(plt.axes([0.55, 0.00, 0.1, 0.035]), 'd01',color = 'black')
btn_d01.on_clicked(callback.get_func_of_switch_ashi("d01"))

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
