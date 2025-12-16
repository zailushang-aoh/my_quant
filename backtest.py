from tqsdk import TqApi, TqAuth, TargetPosTask, TqBacktest
#from tqsdk.ta import BOLL
from datetime import date
from Indicator_Lib.Trend import *
import config

# 全局参数设置
SYMBOL = "SHFE.au2606"
POSITION_SIZE = 1
START_DATE = date(2025,1,1)
END_DATE = date(2025,12,1)
INIT_CASH = 20000


auth = TqAuth(config.TQ_USERNAME, config.TQ_PASSWORD)
api = TqApi(
    auth=auth,
    backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
    web_gui=True,
)

quote = api.get_quote(SYMBOL)
klines = api.get_kline_serial(SYMBOL, duration_seconds=1800, count=10000)
position = api.get_position(SYMBOL)

boll = BOLL(klines, 26, 2)
midline = boll["mid"].iloc[-1]
topline = boll["top"].iloc[-1]
bottomline = boll["bottom"].iloc[-1]

while True:
    # 通过wait_update刷新数据
    api.wait_update()
    # 策略逻辑，根据最新价和BOLL线判断开仓方向
    # 当最新价大于top, 开多仓位
    if quote.last_price > topline:
        api.insert_order(
            symbol=SYMBOL,
            direction="BUY",
            offset="OPEN",
            volume=POSITION_SIZE,
            price=quote.last_price,
        )
    #   当最新价小于bottom, 开空仓位
    elif quote.last_price < bottomline:
        api.insert_order(
            symbol=SYMBOL,
            direction="SELL",
            offset="OPEN",
            volume=POSITION_SIZE,
        )
    # 平仓逻辑, 如果持有多头头寸, 当最新价格小于中轨，则多头平仓
    if position.pos_long > 0:
        if quote.last_price < midline:
            api.insert_order(
                symbol=SYMBOL,
                direction="SELL",
                offset="CLOSE",
                volume=POSITION_SIZE,
            )
    # 平仓逻辑, 如果持有空头头寸, 当最新价格大于中轨，则空头平仓
    elif position.pos_short > 0:
        if quote.last_price > midline:
            api.insert_order(
                symbol=SYMBOL,
                direction="BUY",
            )
