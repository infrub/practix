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
times = 6

dt_now = '\n\n' + str(dt.now())
dp.writelog(dt_now)

pair = dp.pair()
nomalize,spread = dp.spnm(pair)
year = '2018'
month = '9'

path = pair+'/'+pair+'_'+year+'_'+month

initial_text = open("nikki.txt").readlines()[-1]
flamesize = 144

df = [0]*times
for numb in range(times):
	df[numb] = pd.read_csv(path + '/time_'+str(numb)+'.csv', index_col=0, parse_dates=True)

idxs = [0]*times
for k in range(times):
    x=0
    idxs[k] = [x for x in range(len(df[k].index))]

plt.style.use('dark_background')

fig = [0]*times
ax = [[0,0] for x in range(times)]
graph = [[0,0] for x in range(times)]

number = 0
fig[number] = plt.figure(number)

ax[number][1] = fig[number].add_axes((0.05,0.15,0.9,0.2))
ax[number][0] = fig[number].add_axes((0.05,0.35,0.9,0.6),sharex=ax[number][1])

nowpricetext = str(round(df[number].closePrice[flamesize-1],5))
entrypricetext = ''
pricetext = 'entryprice:' + entrypricetext + "\n" +'nowprice:' + nowpricetext
ax[number][0].text(0.05,0.85,pricetext,transform=ax[number][0].transAxes)

mac_main = df[number].macd_main.shift()
mac_signal = df[number].macd_signal.shift()
graph[number][1] = ax[number][1].plot(idxs[number], mac_main, linewidth = lw)
graph[number][1] = ax[number][1].plot(idxs[number], mac_signal, linewidth = lw)
mainhani = df[number].macd_main[0:flamesize]
signalhani = df[number].macd_signal[0:flamesize]
y1hani = mainhani+signalhani

buff = 5.0e-04*df[0].closePrice[0]
ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
ax[number][1].grid(True,linestyle='dotted')
ax[number][1].tick_params(labelbottom=False)

graph[number][0] = mpf.candlestick2_ohlc_indexed_by_openTime(ax[number][0], df[number].openPrice, df[number].highPrice, df[number].lowPrice, df[number].closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
MAmid = df[number].MA_mid.shift()
MAshort = df[number].MA_short.shift()
MAlong = df[number].MA_long.shift()
graph[number][0] = ax[number][0].scatter(idxs[number], MAmid, s=1)
graph[number][0] = ax[number][0].scatter(idxs[number], MAshort, s=1)
graph[number][0] = ax[number][0].scatter(idxs[number], MAlong, s=1)

def show_log(df):
	logdf = pd.read_csv("logdf.csv",header= None)
	starts = logdf[0]
	goals = logdf[1]
	ystarts = [0]*len(starts)
	ygoals = [200]*len(goals)
	xx = [starts,goals,goals,starts]
	yy = [ystarts,ystarts,ygoals,ygoals]
	ax[number][0].fill(xx,yy,color="y",alpha=0.4)

#show_log(df)

ax[number][0].set_xlim(idxs[number][0],idxs[number][flamesize])
ax[number][0].set_xticks(idxs[number][0:flamesize:trip])
ax[number][0].set_xticklabels(df[number].index[0:flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

yhani = df[number].closePrice[0:flamesize]
ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
ax[number][0].grid(True,linestyle='dotted')


class Index(object):
	ind = 0
	oneMind = 0
	entrytype = 0
	entryprice = 0
	oneMprice = 0
	oneMnow = df[5].index[0]
	entrytime = df[0].index[0]
	entrypricetext = ' '

	def prepare_times(self, number, i):
		now = date2num(df[0].index[i+flamesize])
		fig[number] = plt.figure(number)
		plt.close()
		fig[number] = plt.figure(number)
		ax[number][1] = fig[number].add_axes((0.05,0.15,0.9,0.2))
		ax[number][0] = fig[number].add_axes((0.05,0.35,0.9,0.6),sharex=ax[number][1])
		idx = np.abs(np.asarray(date2num(df[number].index)) - now).argmin() + 1
		if (date2num(df[number].index[idx]) - now > 0):
		    idx = idx-1
		start = idx-flamesize
		if(start<0):
		    start = 0

		return start,idx

	def show_times(self, number,start, idx):
		start = idx-flamesize
		if(start<0):
		    start = 0
		nowdf = df[number][start:idx]

		graph[number][0] = mpf.candlestick2_ohlc_indexed_by_openTime(ax[number][0], nowdf.openPrice, nowdf.highPrice, nowdf.lowPrice, nowdf.closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
		graph[number][0] = ax[number][0].scatter(idxs[number][0:idx-start], nowdf.MA_mid, s = 1)
		graph[number][0] = ax[number][0].scatter(idxs[number][0:idx-start], nowdf.MA_short, s = 1)
		graph[number][0] = ax[number][0].scatter(idxs[number][0:idx-start], nowdf.MA_long, s = 1)
		yhani = df[number].closePrice[start:idx]
		ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
		ax[number][0].grid(True,linestyle='dotted')
		ax[number][0].set_xlim(idxs[number][0],idxs[number][idx-start])
		ax[number][0].set_xticks(idxs[number][0:idx-start:trip])
		ax[number][0].set_xticklabels(df[number].index[start:idx:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

		main = df[number].macd_main[start:idx].shift()
		signal = df[number].macd_signal[start:idx].shift()
		graph[number][1] = ax[number][1].plot(idxs[number][0:idx-start], main)
		graph[number][1] = ax[number][1].plot(idxs[number][0:idx-start], signal)
		mainhani = df[number].macd_main[start:idx]
		signalhani = df[number].macd_signal[start:idx]
		y1hani = mainhani+signalhani
		ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
		ax[number][1].grid(True,linestyle='dotted')
		ax[number][1].tick_params(labelbottom=False)

		nowpricetext = str(round(df[number].closePrice[idx-1],5))
		if(self.entrypricetext!=''):
			pips = self.entrytype*(round((df[number].closePrice[idx-1]-self.entryprice)*nomalize,3))-spread
			pipstext = str(pips)
			pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
		else:
			pricetext = 'entryprice:' + self.entrypricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[number][0].texts:
		    txt.set_visible(False)
		ax[number][0].text(0.05,0.85,pricetext,transform=ax[number][0].transAxes)

		plt.show()
	
	def submit(self, text):
		number = 0
		date = text
		future = date2num(dt.strptime(date, '%Y-%m-%d %H:%M'))
		idx = np.abs(np.asarray(date2num(df[number].index)) - future).argmin() + 1
		i = idx - flamesize
		self.ind = i
		ax[number][0].set_xlim(idxs[number][i],idxs[number][i+flamesize])
		ax[number][0].set_xticks(idxs[number][i:i+flamesize:trip])
		ax[number][0].set_xticklabels(df[number].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
		yhani = df[number].closePrice[i:i+flamesize]
		ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
		#ax[number][0].grid(True,linestyle='dotted')
		mainhani = df[number].macd_main[i:i+flamesize]
		signalhani = df[number].macd_signal[i:i+flamesize]
		y1hani = mainhani+signalhani

		ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
		ax[number][1].grid(True,linestyle='dotted')
		ax[number][1].tick_params(labelbottom=False)

		nowpricetext = str(round(df[number].closePrice[i+flamesize-1],5))
		enpricetext = ''
		pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
			txt.set_visible(False)
		ax[number][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		plt.draw()
		logtext = 'move to ' + str(date)
		dp.writelog(logtext)

	def next(self, event):
		self.ind += 1
		i = self.ind
		self.oneMind = 0
		number = 0
		ax[number][0].set_xlim(idxs[number][i],idxs[number][i+flamesize])
		ax[number][0].set_xticks(idxs[number][i:i+flamesize:trip])
		ax[number][0].set_xticklabels(df[number].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
		yhani = df[number].closePrice[i:i+flamesize]
		ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
		#ax[number][0].grid(True,linestyle='dotted')
		mainhani = df[number].macd_main[i:i+flamesize]
		signalhani = df[number].macd_signal[i:i+flamesize]
		y1hani = mainhani+signalhani

		ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
		ax[number][1].grid(True,linestyle='dotted')
		ax[number][1].tick_params(labelbottom=False)

		nowpricetext = str(round(df[number].closePrice[i+flamesize-1],5))
		enpricetext = self.entrypricetext
		if(enpricetext!=''):
			pips = self.entrytype*(round((df[number].closePrice[i+flamesize-1]-self.entryprice)*nomalize,3))-spread
			pipstext = str(pips)
			pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		else:
			pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[number][0].texts:
		    txt.set_visible(False)
		ax[number][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		plt.draw()

		logtext = 'next'
		dp.writelog(logtext)

	def prev(self, event):
		self.ind -= 1
		i = self.ind
		self.oneMind = 0
		number = 0
		ax[number][0].set_xlim(idxs[number][i],idxs[number][i+flamesize])
		ax[number][0].set_xticks(idxs[number][i:i+flamesize:trip])
		ax[number][0].set_xticklabels(df[number].index[i:i+flamesize:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")
		yhani = df[number].closePrice[i:i+flamesize]
		ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
		#ax[number][0].grid(True,linestyle='dotted')
		mainhani = df[number].macd_main[i:i+flamesize]
		signalhani = df[number].macd_signal[i:i+flamesize]
		y1hani = mainhani+signalhani

		ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
		ax[number][1].grid(True,linestyle='dotted')
		ax[number][1].tick_params(labelbottom=False)

		nowpricetext = str(round(df[number].closePrice[i+flamesize-1],5))
		enpricetext = self.entrypricetext
		if(enpricetext!=''):
			pips = self.entrytype*(round((df[number].closePrice[i+flamesize-1]-self.entryprice)*nomalize,3))-spread
			pipstext = str(pips)
			pricetext = 'pips:' + pipstext + "\n" + 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		else:
			pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[number][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		plt.draw()

		logtext = 'previous'
		dp.writelog(logtext)


	def buy(self, event):
		i = self.ind
		self.entryprice = df[0].closePrice[i+flamesize-1]
		self.entrypricetext = str(round(self.entryprice,5))
		nowpricetext = str(round(df[0].closePrice[i+flamesize-1],5))
		enpricetext = self.entrypricetext
		pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		self.entrytype = 1
		self.entrytime = df[0].index[i+flamesize-1]

		logtext = 'buy at ' + str(df[0].index[i+flamesize-1])
		dp.writelog(logtext)

	def sell(self, event):
		i = self.ind
		self.entryprice = df[0].closePrice[i+flamesize-1]
		self.entrypricetext = str(round(self.entryprice,5))
		nowpricetext = str(round(df[0].closePrice[i+flamesize-1],5))
		enpricetext = self.entrypricetext
		pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		self.entrytype = -1
		self.entrytime = df[0].index[i+flamesize-1]

		logtext = 'sell at ' + str(df[0].index[i+flamesize-1])
		dp.writelog(logtext)

	def oneMbuy(self, event):

		self.entryprice = self.oneMprice
		self.entrypricetext = str(round(self.entryprice,5))
		nowpricetext = self.entrypricetext
		enpricetext = self.entrypricetext
		pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
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
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
		self.entrytype = -1
		self.entrytime = self.oneMnow

		logtext = 'sell at ' + str(self.oneMnow)
		dp.writelog(logtext)


	def exit(self, event):
		i = self.ind
		enprice = self.entryprice
		etype = self.entrytype
		exprice = df[0].closePrice[i+flamesize-1]
		extime = df[0].index[i+flamesize-1]
		entime = self.entrytime
		self.entrypricetext = ''
		nowpricetext = str(round(df[0].closePrice[i+flamesize-1],5))
		enpricetext = self.entrypricetext
		pricetext = 'entryprice:' + enpricetext + "\n" +'nowprice:' + nowpricetext
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
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
		for txt in ax[0][0].texts:
		    txt.set_visible(False)
		ax[0][0].text(0.05,0.85,pricetext,transform=ax[0][0].transAxes)
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

	def showM15(self, event):
		logtext = 'see 15M'
		dp.writelog(logtext)
		i = self.ind
		number = 1
		start, idx = self.prepare_times(number,i)
		self.show_times(number, start, idx)
		plt.figure(0)
		
	def showM60(self, event):
		logtext = 'see 60M'
		dp.writelog(logtext)
		i = self.ind
		number = 2
		start, idx = self.prepare_times(number,i)
		self.show_times(number, start, idx)
		plt.figure(0)

	def showH4(self, event):
		logtext = 'see 4H'
		dp.writelog(logtext)
		i = self.ind
		number = 3
		start, idx = self.prepare_times(number,i)
		self.show_times(number, start, idx)
		plt.figure(0)

	def showD1(self, event):
		logtext = 'see 1D'
		dp.writelog(logtext)
		i = self.ind
		number = 4
		start, idx = self.prepare_times(number,i)
		self.show_times(number, start, idx)
		plt.figure(0)

	def showM1(self, event):
		logtext = 'see 1M'
		dp.writelog(logtext)
		self.oneMind += 1
		i = self.ind
		diff = self.oneMind - 1
		number = 5
		start, idx = self.prepare_times(number,i)
		idx = idx + diff
		self.oneMprice = round(df[number].closePrice[idx-1],5)
		self.oneMnow = df[number].index[idx-1]
		self.show_times(number, start, idx)
		plt.figure(0)

plt.figure(0)

callback = Index()
axprev = plt.axes([0.7, 0.0, 0.1, 0.075])
axnext = plt.axes([0.81, 0.0, 0.1, 0.075])
axbuy = plt.axes([0.0, 0.0, 0.1, 0.075])
axsell = plt.axes([0.11, 0.0, 0.1, 0.075])
axexit = plt.axes([0.22, 0.0, 0.1, 0.075])

bnext = Button(axnext, 'Next',color = 'black')
bnext.on_clicked(callback.next)
bprev = Button(axprev, 'Previous',color = 'black')
bprev.on_clicked(callback.prev)
bbuy = Button(axbuy, 'Buy',color = 'black')
bbuy.on_clicked(callback.buy)
bsell = Button(axsell, 'Sell',color = 'black')
bsell.on_clicked(callback.sell)
bexit = Button(axexit, 'Exit',color = 'black')
bexit.on_clicked(callback.exit)

axoneMbuy = plt.axes([0.0, 0.11, 0.1, 0.035])
axoneMsell = plt.axes([0.11, 0.11, 0.1, 0.035])
axoneMexit = plt.axes([0.22, 0.11, 0.1, 0.035])

boneMbuy = Button(axoneMbuy, '1Buy',color = 'black')
boneMbuy.on_clicked(callback.oneMbuy)
boneMsell = Button(axoneMsell, '1Sell',color = 'black')
boneMsell.on_clicked(callback.oneMsell)
boneMexit = Button(axoneMexit, '1Exit',color = 'black')
boneMexit.on_clicked(callback.oneMexit)

axM15 = plt.axes([0.33, 0.04, 0.1, 0.035])
bM15 = Button(axM15, 'M15',color = 'black')
bM15.on_clicked(callback.showM15)

axM60 = plt.axes([0.33, 0, 0.1, 0.035])
bM60 = Button(axM60, 'M60',color = 'black')
bM60.on_clicked(callback.showM60)

axH4 = plt.axes([0.44, 0.04, 0.1, 0.035])
bH4 = Button(axH4, 'H4',color = 'black')
bH4.on_clicked(callback.showH4)

axD1 = plt.axes([0.44, 0, 0.1, 0.035])
bD1 = Button(axD1, 'D1',color = 'black')
bD1.on_clicked(callback.showD1)

axM1 = plt.axes([0.55, 0, 0.1, 0.035])
bM1 = Button(axM1, 'M1',color = 'black')
bM1.on_clicked(callback.showM1)

axbox = plt.axes([0.6, 0.08, 0.4, 0.035])

text_box = TextBox(axbox, '', color = 'green', initial = initial_text)
text_box.on_submit(callback.submit)

plt.show()
