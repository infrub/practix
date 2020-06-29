import sys
import numpy as np
import pandas as pd
from matplotlib.dates import date2num
import datetime
import calendar
import os
from tqdm import trange


pairname = "USDJPY" if len(sys.argv)==1 else sys.argv[1]
rh_root = "raw_histories/" + pairname

yoyuu = 144
ashis = ["m01","m05","m15","h01","h04","d01"]
tmds = [datetime.timedelta(minutes=1), datetime.timedelta(minutes=5), datetime.timedelta(minutes=15), datetime.timedelta(hours=1), datetime.timedelta(hours=4), datetime.timedelta(days=1)]


alltime_dfs = {}
for ashi, tmd in zip(ashis, tmds):
    df = pd.read_csv(rh_root + "/alltime/market_" + ashi + ".csv", parse_dates=True)
    df["openTime"] = pd.to_datetime(df.openTime)
    df["closeTime"] = df.openTime.shift(-1)
    df.closeTime[len(df)-1] = df.openTime[len(df)-1] + tmd
    alltime_dfs[ashi] = df


df = alltime_dfs["h01"]




for weeki in trange(150):
    kireme_d = datetime.datetime(year=2018, month=1, day=7) + datetime.timedelta(days=7) * weeki
    if kireme_d >= datetime.datetime(year=2020, month=1, day=1): break
    owbf_d = kireme_d - datetime.timedelta(days=7)

    dfs = {}
    for ashi in ashis:
        df = alltime_dfs[ashi]
        kireme_x = len(df[df.openTime <= kireme_d])
        owbf_x = len(df[df.openTime <= owbf_d])
        df = df[max(owbf_x-yoyuu,0):kireme_x]
        df = df.reset_index(drop=True)

        df["openX"] = df.index
        df["closeX"] = df.openX + 1

        dfs[ashi] = df

    for ashi1 in ashis:
        df1 = dfs[ashi1]
        for ashi2 in ashis:
            df2 = dfs[ashi2]
            cx2 = 1
            temp = []
            for cx1 in range(1,len(df1)+1):
                while cx2 < len(df2) and df1.closeTime[cx1-1] >= df2.closeTime[cx2]:
                    cx2 += 1
                temp.append(cx2)
            df1["matching_closeX_in_"+ashi2] = np.array(temp)


    dirname = "week_" + str(weeki).zfill(3)
    os.makedirs(rh_root+'/'+dirname)

    for ashi in ashis:
        filename = 'market_' + ashi + '.csv'
        path = rh_root+'/'+dirname+'/'+filename
        dfs[ashi].to_csv(path, index=False)
