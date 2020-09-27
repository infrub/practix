import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
import pandas as pd
import my_mpl_finance as mpf
from datetime import datetime as dt
import os
import sys
import json
import math




#TODO 実際macdとかどういうパラメでやってるのか


trip = 24
flamesize = 96
yoyuu = 144
ashis = ["m01","m05","m15","h01","h04","d01"]

pairname = "USDJPY" if len(sys.argv)<=1 else sys.argv[1]
weeki = 1 if len(sys.argv)<=2 else int(sys.argv[2])
init_m05_rex = yoyuu if len(sys.argv)<=3 else int(sys.argv[3])

with open(f"raw_histories/{pairname}/style.json") as f:
    jsn1 = json.loads(f.read())
    rate_digpl = jsn1["rate_digpl"] # effective digit place of rates
    pips_digpl = jsn1["pips_digpl"] # effective digit place of pips
    ipv = jsn1["ipv"] # inverse of pips value (e.g. 100 in USDJPY)
    spread_pips = jsn1["spread_pips"] # spread_pips (単位はpips)

def textize_rate(x):
    return ("{:."+str(rate_digpl)+"f}").format(x)

def textize_pips(x):
    return ("{:."+str(pips_digpl)+"f}").format(x)



logfname = f"logs/{pairname}/week_{str(weeki).zfill(3)}.csv"
with open(logfname,"a") as f:
    f.write("entryX,exitX,entryTime,exitTime,entryStatus,entryPrice,exitPrice,profitPips\n")
def wrlog(entryX,exitX,entryTime,exitTime,entryStatus,entryPrice,exitPrice,profitPips):
    with open(logfname,"a") as f:
        f.write(f"{entryX},{exitX},{entryTime},{exitTime},{entryStatus},{textize_rate(entryPrice)},{textize_rate(exitPrice)},{textize_pips(profitPips)}\n")



dfs = {}
idxs = {}
for ashi in ashis:
    df = pd.read_csv("raw_histories/" + pairname + "/week_" + str(weeki).zfill(3) + "/market_"+ashi+".csv", parse_dates=True)
    df["openTime"] = pd.to_datetime(df.openTime)
    df["closeTime"] = pd.to_datetime(df.closeTime)
    dfs[ashi] = df
    idxs[ashi] = np.arange(len(dfs[ashi].index))


#styles
priceLineWidth = 0.6
bgcolor = "#131313"
plt.style.use('dark_background')
#fig = plt.figure(figsize=(12,7), num=f"{pairname} week_"+ str(weeki).zfill(3), facecolor=bgcolor)
fig = plt.figure(figsize=(12,7), num=f"the_game", facecolor=bgcolor)


candle_axs = {ashi:None for ashi in ashis}
mac_axs = {ashi:None for ashi in ashis}
nowPriceLines = {}
entryPriceLines = {}

rexs = {"m05":init_m05_rex}
lexs = {"m05":max(0,init_m05_rex-flamesize)}
for ashi in ashis:
    if ashi=="m05": continue
    rex = dfs["m05"]["matching_closeX_in_"+ashi][rexs["m05"]-1]
    rexs[ashi] = rex
    lexs[ashi] = max(0,rex-flamesize)

watching_ashi = "h01"
LONG,NOENT,SHORT = 1,0,-1
entryStatus = NOENT
entryTime = None
entryPrice = None
entryX = None
lastProfit = 0
sumProfit = 0


def create_ax(ashi):
    mpf.candlestick2_ohlc_indexed_by_openTime(candle_axs[ashi], dfs[ashi].openPrice, dfs[ashi].highPrice, dfs[ashi].lowPrice, dfs[ashi].closePrice, width=0.7, alpha=1.0, colorup="#fa2200", colordown="#0077ff")
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_short, color="#f6ad48", s=1) # 終値の単純移動平均(ピリオド5)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_mid, color="#aacf52", s=1) # 終値の単純移動平均(ピリオド13)
    candle_axs[ashi].scatter(idxs[ashi]+1, dfs[ashi].MA_long, color="#00b1a9", s=1) # 終値の単純移動平均(ピリオド25)
    candle_axs[ashi].set_xticks(np.arange(1,len(dfs[ashi]),trip)) # 1ずらしたほうが罫線のキリがよくなる
    candle_axs[ashi].set_xticklabels(dfs[ashi].openTime[1:len(dfs[ashi]):trip].dt.strftime('%Y-%m-%d\n%H:%M'),rotation=0,size="small")

    miny = round(min(dfs[ashi].lowPrice),rate_digpl-2)-(0.1**(rate_digpl-2))
    maxy = round(max(dfs[ashi].highPrice),rate_digpl-2)+(0.1**(rate_digpl-2))
    candle_axs[ashi].set_yticks(np.arange(miny,maxy,0.1**(rate_digpl-2)))

    candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
    miny = min(dfs[ashi].lowPrice[lexs[ashi]:rexs[ashi]])
    maxy = max(dfs[ashi].highPrice[lexs[ashi]:rexs[ashi]])
    buff = (maxy - miny)*0.05
    candle_axs[ashi].set_ylim(miny-buff,maxy+buff)
    candle_axs[ashi].grid(True,linestyle='dotted')

    
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_signal, color="lightslategrey", linewidth = 1.5) # MACD(5,11,4) sig
    mac_axs[ashi].plot(idxs[ashi]+1, dfs[ashi].macd_main, color="mediumvioletred", linewidth = 1.5) # MACD(5,11,4) main
    mac_axs[ashi].grid(True,linestyle='dotted')
    mac_axs[ashi].tick_params(labelbottom=False)


    nowPriceLines[ashi] = candle_axs[ashi].hlines(dfs["m05"].closePrice[rexs["m05"]-1],0,len(dfs[ashi]), color="yellow", linewidth=priceLineWidth)
    entryPriceLines[ashi] = candle_axs[ashi].hlines(0,0,len(dfs[ashi]), color=bgcolor, linewidth=priceLineWidth)

    update_text()


def move_tick_with_new_rex_in_m05(new_rex_in_m05):
    for ashi in ashis:
        rex = dfs["m05"]["matching_closeX_in_"+ashi][new_rex_in_m05-1]
        rexs[ashi] = rex
        lexs[ashi] = max(0,rex-flamesize)
        candle_axs[ashi].set_xlim(lexs[ashi],rexs[ashi])
        miny = min(dfs[ashi].lowPrice[lexs[ashi]:rexs[ashi]])
        maxy = max(dfs[ashi].highPrice[lexs[ashi]:rexs[ashi]])
        buff = (maxy - miny)*0.05
        candle_axs[ashi].set_ylim(miny-buff,maxy+buff)
        nowPriceLines[ashi].remove()
        nowPriceLines[ashi] = candle_axs[ashi].hlines(dfs["m05"].closePrice[rexs["m05"]-1],0,len(dfs[ashi]), color="yellow", linewidth=priceLineWidth)
    update_text()
    plt.draw()

def next_tick(event):
    if rexs["m05"] >= len(dfs["m05"]):
        print("RIGHT EDGE!")
        return
    move_tick_with_new_rex_in_m05(rexs["m05"]+1)

def prev_tick(event):
    move_tick_with_new_rex_in_m05(rexs["m05"]-1)

def get_func_of_switch_ashi(ashi): # TODO キーボードでいじったときだけなぜか色がすぐには変わらない(カーソル当てると変わる)
    global watching_ashi
    def switch(event):
        global watching_ashi
        fig.delaxes(mac_axs[watching_ashi])
        fig.delaxes(candle_axs[watching_ashi])
        btns[watching_ashi].color = bgcolor
        watching_ashi = ashi
        fig.add_axes(mac_axs[watching_ashi])
        fig.add_axes(candle_axs[watching_ashi])
        btns[watching_ashi].color = "lightseagreen"
        plt.draw()
    return switch


def update_text():
    for ashi in ashis:
        while len(candle_axs[ashi].texts) > 0:
            del candle_axs[ashi].texts[-1]
    while len(infobax.texts) > 0:
        del infobax.texts[-1]

    nowPrice = dfs['m05'].closePrice[rexs['m05']-1]

    ctext = "now: " + textize_rate(nowPrice)
    ttext = "sum: " + textize_pips(sumProfit) + " pips "
    if entryStatus == NOENT:
        ttext += f"    last: " + textize_pips(lastProfit) + " pips"
    elif entryStatus == LONG:
        ctext += f"\nbought: " + textize_rate(entryPrice)
        ttext += f"    latent: " + textize_pips((nowPrice-entryPrice)*ipv - spread_pips) + " pips"
    elif entryStatus == SHORT:
        ctext += f"\nsold: " + textize_rate(entryPrice)
        ttext += f"    latent: " + textize_pips((entryPrice-nowPrice)*ipv - spread_pips) + " pips"

    for ashi in ashis:
        candle_axs[ashi].text(0.05,0.95,ctext,verticalalignment='top',transform=candle_axs[ashi].transAxes)
    infobax.text(0,0.5,ttext,verticalalignment="center",horizontalalignment="left")
    infobax.text(1,0.5,f"{100.0*(rexs['m05']-yoyuu)/(len(dfs['m05'])-yoyuu):.1f}% of the week",verticalalignment="center",horizontalalignment="right")



def buy(event):
    global entryStatus, entryX, entryPrice, entryTime
    if entryStatus != NOENT: return

    entryStatus = LONG
    entryX = rexs["m05"]
    entryPrice = dfs["m05"].closePrice[entryX-1]
    entryTime = dfs["m05"].closeTime[entryX-1]

    for ashi in ashis:
        entryPriceLines[ashi].remove()
        entryPriceLines[ashi] = candle_axs[ashi].hlines(entryPrice,0,len(dfs[ashi]), color="coral", linewidth=priceLineWidth)
    update_text()
    btn_sell.color = bgcolor
    btn_sell.label.set_text("")
    btn_buy.color = "red"
    btn_buy.label.set_text("Exit")
    plt.draw()

def sell(event):
    global entryStatus, entryX, entryPrice, entryTime
    if entryStatus != NOENT: return

    entryStatus = SHORT
    entryX = rexs["m05"]
    entryPrice = dfs["m05"].closePrice[entryX-1]
    entryTime = dfs["m05"].closeTime[entryX-1]

    for ashi in ashis:
        entryPriceLines[ashi].remove()
        entryPriceLines[ashi] = candle_axs[ashi].hlines(entryPrice,0,len(dfs[ashi]), color="cornflowerblue", linewidth=priceLineWidth)
    update_text()
    btn_sell.color = "blue"
    btn_sell.label.set_text("Exit")
    btn_buy.color = bgcolor
    btn_buy.label.set_text("")
    plt.draw()

def exit(event):
    global entryStatus, entryX, entryPrice, entryTime, lastProfit, sumProfit
    if entryStatus == NOENT:
        return
    else:
        exitX = rexs["m05"]
        exitPrice = dfs["m05"].closePrice[exitX-1]
        exitTime = dfs["m05"].closeTime[exitX-1]
        lastProfit = entryStatus*(exitPrice-entryPrice)*ipv - spread_pips

    wrlog(entryX,exitX,entryTime,exitTime,entryStatus,entryPrice,exitPrice,lastProfit)

    entryStatus = NOENT
    sumProfit += lastProfit

    for ashi in ashis:
        entryPriceLines[ashi].remove()
        entryPriceLines[ashi] = candle_axs[ashi].hlines(0,0,len(dfs[ashi]), color=bgcolor, linewidth=priceLineWidth)
    update_text()
    btn_sell.color = "cornflowerblue"
    btn_sell.label.set_text("Sell")
    btn_buy.color = "coral"
    btn_buy.label.set_text("Buy")
    plt.draw()


def buyOrExit(event):
    if entryStatus == NOENT: buy(event)
    elif entryStatus == LONG: exit(event)

def sellOrExit(event):
    if entryStatus == NOENT: sell(event)
    elif entryStatus == SHORT: exit(event)


mutfname = f"logs/{pairname}/week_{str(weeki).zfill(3)}.mut"
with open(mutfname,"a") as f:
    f.write(f"nowX,nowTime,text\n")
def mutter(text):
    if len(text)!=0:
        nowX = rexs['m05']
        nowTime = dfs["m05"].closeTime[nowX-1]
        with open(mutfname,"a") as f:
            f.write(f"{nowX},{nowTime.strftime('%Y/%m/%d %H:%M')},{text}\n")
    else:
        hoge = text + "" # なぜかこのくらいしないとバグる



x1,x2,x3,x4 = 0.05,0.45,0.55,0.95
y0,y1,y2,y3,y4,y5,y6,y7 = 0.03,0.06,0.08,0.16,0.18,0.34,0.93,0.98

#(left,bottom,width,height)
acax_position = (x1,y5,x2-x1,y6-y5) # A面のcandle axの位置
amax_position = (x1,y4,x2-x1,y5-y4)
bcax_position = (x3,y5,x4-x3,y6-y5)
bmax_position = (x3,y4,x4-x3,y5-y4)
infobax_position = (x1,y6,x4-x1,y7-y6)

for ashi in ashis:
    if ashi == "m05":
        mac_axs[ashi] = fig.add_axes(amax_position, facecolor=bgcolor)
        candle_axs[ashi] = fig.add_axes(acax_position,sharex=mac_axs[ashi], facecolor=bgcolor)
    else:
        mac_axs[ashi] = fig.add_axes(bmax_position, facecolor=bgcolor)
        candle_axs[ashi] = fig.add_axes(bcax_position,sharex=mac_axs[ashi], facecolor=bgcolor)
    fig.delaxes(mac_axs[ashi])
    fig.delaxes(candle_axs[ashi])

infobax = fig.add_axes(infobax_position, facecolor=bgcolor)
infobax.spines['top'].set_visible(False)
infobax.spines['bottom'].set_visible(False)
infobax.spines['left'].set_visible(False)
infobax.spines['right'].set_visible(False)
infobax.xaxis.set_visible(False)
infobax.yaxis.set_visible(False)


# ボタンを設置。冗長だがボタンを入れた変数の束縛がなくなるとボタンが働かなくなるので仕方ない
btn_sell = Button(plt.axes([0.05, y2, 0.1, y3-y2]), 'Sell',color = 'cornflowerblue')
btn_sell.on_clicked(sellOrExit)
btn_buy = Button(plt.axes([0.16, y2, 0.1, y3-y2]), 'Buy',color = 'coral')
btn_buy.on_clicked(buyOrExit)

btn_prev = Button(plt.axes([0.44, y2, 0.055, y3-y2]), 'Prev',color = bgcolor)
btn_prev.on_clicked(prev_tick)
btn_next = Button(plt.axes([0.505, y2, 0.055, y3-y2]), 'Next',color = bgcolor)
btn_next.on_clicked(next_tick)

btns = {}
btns["m01"] = Button(plt.axes([0.65, y2, 0.045, y3-y2]), 'm01',color = bgcolor)
btns["m01"].on_clicked(get_func_of_switch_ashi("m01"))
btn_dummy1 = Button(plt.axes([0.70, y2, 0.045, y3-y2]), '',color = bgcolor)
btn_dummy1.on_clicked(lambda x: x)
btns["m15"] = Button(plt.axes([0.75, y2, 0.045, y3-y2]), 'm15',color = bgcolor)
btns["m15"].on_clicked(get_func_of_switch_ashi("m15"))
btns["h01"] = Button(plt.axes([0.80, y2, 0.045, y3-y2]), 'h01',color = bgcolor)
btns["h01"].on_clicked(get_func_of_switch_ashi("h01"))
btns["h04"] = Button(plt.axes([0.85, y2, 0.045, y3-y2]), 'h04',color = bgcolor)
btns["h04"].on_clicked(get_func_of_switch_ashi("h04"))
btns["d01"] = Button(plt.axes([0.90, y2, 0.045, y3-y2]), 'd01',color = bgcolor)
btns["d01"].on_clicked(get_func_of_switch_ashi("d01"))



keycon_available = True

class MyTextBox(TextBox):
    def begin_typing(self, x):
        global keycon_available
        super().begin_typing(x)
        #print("keycon disabled")
        keycon_available = False

    def stop_typing(self):
        global keycon_available
        super().stop_typing()
        #print("keycon enabled")
        keycon_available = True

    def what_do_on_submit(self,text):
        mutter(text)
        self.set_val("")

mtrbox = MyTextBox(plt.axes([x1, y0, x4-x1, y1-y0]), "", initial="",color=bgcolor,hovercolor="#333333")
mtrbox.on_submit(mtrbox.what_do_on_submit)

# キーボードで操作もね
try:
    with open(f"configs/ytest_config.json") as f:
        jsn2 = json.loads(f.read())
        def keycon(event):
            if keycon_available:
                if event.key in jsn2["keyconfig"]["buy"]: buy(event)
                elif event.key in jsn2["keyconfig"]["sell"]: sell(event)
                elif event.key in jsn2["keyconfig"]["exit"]: exit(event)
                elif event.key in jsn2["keyconfig"]["prev"]: prev_tick(event)
                elif event.key in jsn2["keyconfig"]["next"]: next_tick(event)
                elif event.key in jsn2["keyconfig"]["m01"]: get_func_of_switch_ashi("m01")(event)
                elif event.key in jsn2["keyconfig"]["m15"]: get_func_of_switch_ashi("m15")(event)
                elif event.key in jsn2["keyconfig"]["h01"]: get_func_of_switch_ashi("h01")(event)
                elif event.key in jsn2["keyconfig"]["h04"]: get_func_of_switch_ashi("h04")(event)
                elif event.key in jsn2["keyconfig"]["d01"]: get_func_of_switch_ashi("d01")(event)
                else: pass
            else:
                pass
except:
    raise Exception("please make ytest_config.json")
plt.connect('key_press_event',keycon)




ashi = "m05"
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

ashi = watching_ashi
fig.add_axes(mac_axs[ashi])
fig.add_axes(candle_axs[ashi])

for ashi in ashis:
    create_ax(ashi)

btns[watching_ashi].color = "lightseagreen"


plt.show()


#閉じたら日記に書き込む
blogfname = f"logs/{pairname}/blog.txt"
with open(blogfname,"a") as f:
    today = dt.now().strftime("%Y/%m/%d %H:%M:%S")
    f.write(f"\n\n\n{today} 完了")
    f.write(f"\n{pairname} week_{str(weeki).zfill(3)}")
    f.write(f"\nsumProfit: {sumProfit:.1f}")

print(f"sumProfit: {sumProfit:.1f}")