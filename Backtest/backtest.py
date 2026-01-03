import sys
import os
# 将项目根目录（即 Indicator_Lib 所在目录）加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tqsdk import TqApi, TqAuth, TargetPosTask, TqBacktest, BacktestFinished, TqSim
from datetime import date
from Indicator_Lib.Trend import *
import config
import Strategy


# 全局参数设置
SYMBOL = "DCE.jm2605" # 合约代码
POSITION_SIZE = 1 # 仓位大小
START_DATE = date(2024,11,20) # 回测开始时间
END_DATE = date(2025,12,1) # 回测结束时间
INIT_CASH = 200000 # 初始资金

# 创建api实例
acc = TqSim(init_balance=INIT_CASH)
auth = TqAuth(config.TQ_USERNAME, config.TQ_PASSWORD)
api = TqApi( 
    account=acc,
    auth=auth,
    backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
    web_gui= config.WEB_HOST,
)

quote = api.get_quote(SYMBOL)
klines = api.get_kline_serial(SYMBOL, duration_seconds=1800, count=1000)
#ticks = api.get_tick_serial(SYMBOL, count=1000)
position = api.get_position(SYMBOL)
target_pos = TargetPosTask(api, SYMBOL)


try:
    while True:
        api.wait_update()
        if api.is_changing(klines):
           # 策略逻辑
           Strategy.strategy1.main(klines, quote, target_pos)

except BacktestFinished as e: 
    print(acc.trade_log)
    while True:
        api.wait_update()  
