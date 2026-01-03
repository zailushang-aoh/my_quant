from tqsdk import TqApi, TqAuth, TargetPosTask, TqBacktest, BacktestFinished, TqSim
#from tqsdk.ta import BOLL
from datetime import date
from Indicator_Lib.Trend import *

def main(klines, quote, target_pos):
    boll = BOLL(klines, 26, 2)
    midline = boll["mid"].iloc[-1]
    topline = boll["top"].iloc[-1]
    bottomline = boll["bottom"].iloc[-1]
    #print(boll, midline, topline, bottomline)
    # 策略逻辑，根据最新价和BOLL线判断开仓方向
    # 当最新价大于top, 开多仓位
    if quote.last_price > topline:
        #print("最新价大于MA: 获取最新价:", quote.last_price)
        target_pos.set_target_volume(2)
        #print("最新价大于MA: 目标多头2手")
    #   当最新价小于bottom, 开空仓位
    elif quote.last_price < bottomline:
        target_pos.set_target_volume(-2)
        #print("最新价大于MA: 目标空头2手")
    else:
        #print("最新价小于MA: 目标空仓")
        target_pos.set_target_volume(0)
    return