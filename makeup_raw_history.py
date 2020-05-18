import numpy as np
import pandas as pd
from matplotlib.dates import date2num
import datetime
import calendar
import os


# /raw_histories/<通貨ペア名>/alltime/ に market_<足>.csv という名前でデータ置いとく
# そしてここを適切に編集して実行
pairname = "USDGBP"
ashis = ["1m","5m","15m","60m","4h","1d"]
ymlist = [(y,m) for y in [2018,2019] for m in range(1,13)]


rh_root = "raw_histories/" + pairname


dfs = {}
for ashi in ashis:
	dfs[ashi] = pd.read_csv(rh_root + "/alltime/market_" + ashi + ".csv", index_col=0, parse_dates=True)

for year,month in ymlist:
	dirname = str(year) + '_' + str(month).zfill(2)
	os.makedirs(rh_root+'/'+dirname)

	firstday = 1
	lastday =  calendar.monthrange(year, month)[1]
	firstdate = date2num(datetime.datetime(year, month, firstday, 0, 0, 0))
	lastdate = date2num(datetime.datetime(year, month, lastday, 23, 59, 59))

	for ashi in ashis:
		f_idx = np.abs(np.asarray(date2num(dfs[ashi].index)) - firstdate).argmin() - 3
		if(f_idx<144):
			f_idx=144
		l_idx = np.abs(np.asarray(date2num(dfs[ashi].index)) - lastdate).argmin() + 3
		filename = 'market_' + ashi + '.csv'
		path = rh_root+'/'+dirname+'/'+filename
		dfs[ashi][f_idx-144:l_idx].to_csv(path)
