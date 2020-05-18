import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
from matplotlib.dates import date2num
import my_mpl_finance as mpf
from datetime import datetime as dt
import os
import shutil
import determin_pair as dp

lw = 1.0
trip = 20
times = 6
spread = 1.0
flamesize = 144

ashi = ['5M','15M','60M','4H','1D','1M']

pair = dp.pair()
year = '2018'
month = '6'

imagelog_path = pair+'/'+'log_'+pair+'/images/'+year+'_'+month

if(os.path.exists(imagelog_path)):
	shutil.rmtree(imagelog_path)
os.makedirs(imagelog_path)

logfile_path = pair+'/'+'log_'+pair+'/log_'+year+'_'+month+'.csv'
logdf = pd.read_csv(logfile_path,header= None)

path = pair+'/'+pair+'_'+year+'_'+month
df = [0]*times
for numb in range(times):
	df[numb] = pd.read_csv(path + '/time_'+str(numb)+'.csv', index_col=0, parse_dates=True)

buff = 5.0e-04*df[0].closePrice[0]
idxs = [0]*times
for k in range(times):
    x=0
    idxs[k] = [x for x in range(len(df[k].index))]

plt.style.use('dark_background')
fig = [0]*times
ax = [[0,0] for x in range(times)]
graph = [[0,0] for x in range(times)]

for data in range(len(logdf[0])):
#for data in range(3):
	start_time = logdf[0][data]
	goal_time = logdf[1][data]
	benefit = logdf[2][data]
	taipe = logdf[3][data]

	if(taipe==1):
		taipetext = 'buy'
	else:
		taipetext = 'sell'
	dirtitle = str(data) + '_' + taipetext + '_' + str(benefit)

	herepath = imagelog_path + '/' + dirtitle
	os.makedirs(herepath)

	for number in range(times):
		try:
			entry = date2num(dt.strptime(start_time, '%Y/%m/%d %H:%M'))
			exit = date2num(dt.strptime(goal_time, '%Y/%m/%d %H:%M'))
		except ValueError:
			entry = date2num(dt.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
			exit = date2num(dt.strptime(goal_time, '%Y-%m-%d %H:%M:%S'))

		fig[number] = plt.figure(number)
		ax[number][1] = fig[number].add_axes((0.05,0.15,0.9,0.2))
		ax[number][0] = fig[number].add_axes((0.05,0.35,0.9,0.6),sharex=ax[number][1])
		entry_idx = np.abs(np.asarray(date2num(df[number].index)) - entry).argmin()
		start = entry_idx-flamesize
		if(start < 0):
			start = 0

		exit_idx = np.abs(np.asarray(date2num(df[number].index)) - exit).argmin()
		goal = exit_idx + 20

		if(goal > idxs[number][-1]):
			goal = idxs[number][-1]

		nowdf = df[number][start:goal]

		graph[number][0] = mpf.candlestick2_ohlc_indexed_by_openTime(ax[number][0], nowdf.openPrice, nowdf.highPrice, nowdf.lowPrice, nowdf.closePrice, width=0.8, alpha=1.0, colorup='#FF0000', colordown='g')
		graph[number][0] = ax[number][0].scatter(idxs[number][0:goal-start], nowdf.MA_mid,s=1)
		graph[number][0] = ax[number][0].scatter(idxs[number][0:goal-start], nowdf.MA_short,s=1)
		graph[number][0] = ax[number][0].scatter(idxs[number][0:goal-start], nowdf.MA_long,s=1)
		yhani = df[number].closePrice[start:goal]

		xx = [entry_idx-start+1,exit_idx-start+1,exit_idx-start+1,entry_idx-start+1]
		yy = [0,0,200,200]
		ax[number][0].fill(xx,yy,color="y",alpha=0.4)

		ax[number][0].set_ylim(min(yhani)-buff,max(yhani)+buff)
		ax[number][0].grid(True,linestyle='dotted')
		ax[number][0].set_xlim(idxs[number][0],idxs[number][goal-start])
		ax[number][0].set_xticks(idxs[number][0:goal-start:trip])
		ax[number][0].set_xticklabels(df[number].index[start:goal:trip].strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

		main = df[number].macd_main[start:goal].shift()
		signal = df[number].macd_signal[start:goal].shift()
		graph[number][1] = ax[number][1].plot(idxs[number][0:goal-start], main)
		graph[number][1] = ax[number][1].plot(idxs[number][0:goal-start], signal)
		mainhani = df[number].macd_main[start:goal]
		signalhani = df[number].macd_signal[start:goal]
		y1hani = mainhani+signalhani
		ax[number][1].set_ylim(min(y1hani)-buff*0.01,max(y1hani)+buff*0.01)
		ax[number][1].grid(True,linestyle='dotted')
		ax[number][1].tick_params(labelbottom=False)

		

		imagetitle = ashi[number] + '.png'

		plt.savefig(herepath + '/' + imagetitle)
		plt.close()