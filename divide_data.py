import numpy as np
import pandas as pd
from matplotlib.dates import date2num
import datetime
import calendar
import os
import determin_pair as dp

pair = dp.pair()
flamesize = 144
df = [0]*6
df[0] = pd.read_csv(pair + "/market.csv", index_col=0, parse_dates=True)
df[1] = pd.read_csv(pair + "/market15M.csv", index_col=0, parse_dates=True)
df[2] = pd.read_csv(pair + "/market60M.csv", index_col=0, parse_dates=True)
df[3] = pd.read_csv(pair + "/market4H.csv", index_col=0, parse_dates=True)
df[4] = pd.read_csv(pair + "/market1D.csv", index_col=0, parse_dates=True)
df[5] = pd.read_csv(pair + "/market1M.csv", index_col=0, parse_dates=True)

yearlist = [2018,2019]
monthlist = [i+1 for i in range(12)]

for year in yearlist:
	for month in monthlist:
		dirname = pair + '_' + str(year) + '_' + str(month)
		os.makedirs(pair+'/'+dirname)

		firstday = 1
		lastday =  calendar.monthrange(year, month)[1]
		firstdate = date2num(datetime.datetime(year, month, firstday, 0, 0, 0))
		lastdate = date2num(datetime.datetime(year, month, lastday, 23, 59, 59))

		for number in range(6):
			f_idx = np.abs(np.asarray(date2num(df[number].index)) - firstdate).argmin() - 3
			if(f_idx<144):
				f_idx=144
			l_idx = np.abs(np.asarray(date2num(df[number].index)) - lastdate).argmin() + 3
			filename = 'time_' + str(number) + '.csv'
			path = pair+'/'+dirname+'/'+filename
			df[number][f_idx-144:l_idx].to_csv(path)
