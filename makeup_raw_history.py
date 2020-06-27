import sys
import numpy as np
import pandas as pd
from matplotlib.dates import date2num
import datetime
import calendar
import os


pairname = "USDGBP" if len(sys.argv)==1 else sys.argv[1]
rh_root = "raw_histories/" + pairname

ashis = ["m01","m05","m15","h01","h04","d01"]
ashis = ["h04","d01"]
tmds = [datetime.timedelta(minutes=1), datetime.timedelta(minutes=5), datetime.timedelta(minutes=15), datetime.timedelta(hours=1), datetime.timedelta(hours=4), datetime.timedelta(days=1)]


dfs = {}
for ashi, tmd in zip(ashis, tmds):
	df = pd.read_csv(rh_root + "/alltime/market_" + ashi + ".csv", parse_dates=True)
	df["openTime"] = pd.to_datetime(df.openTime)
	df["closeTime"] = df.openTime.shift(-1)
	df["openX"] = df.index
	df["closeX"] = df.openX + 1
	df.closeTime[len(df)-1] = df.openTime[len(df)-1] + tmd
	for ashi2 in ashis:
		df["matching_closeX_in_"+ashi2] = np.zeros(len(df), dtype=int)
	dfs[ashi] = df



for ashi1 in ashis:
	df1 = dfs[ashi1]
	for ashi2 in ashis:
		df2 = dfs[ashi2]

		cx2 = 1
		for cx1 in range(1,len(df1)+1):
			while cx2 < len(df2) and df1.closeTime[cx1-1] >= df2.closeTime[cx2]:
				cx2 += 1
			df1["matching_closeX_in_"+ashi2][cx1-1] = cx2



for ashi in ashis:
	print(dfs[ashi])














# /raw_histories/<通貨ペア名>/alltime/ に market_<足>.csv という名前でデータ置いとく
# そしてここを適切に編集して実行





"""
pairname = "USDGBP"
ashis = ["5m","15m","60m","4h","1d","1m"]
ymlist = [(y,m) for y in [2018,2019] for m in range(1,13)]




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
"""