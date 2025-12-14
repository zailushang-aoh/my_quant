from tqsdk import TqApi, TqAuth, TargetPosTask, TqBacktest
from tqsdk.ta import BOLL
import os
from dotenv import load_dotenv
from ..Indicator_Lib.Trend import *

# 从环境变量读取凭据，避免在代码中明文写入密码
load_dotenv()
TQ_USERNAME = os.getenv("TQ_USERNAME")
TQ_PASSWORD = os.getenv("TQ_PASSWORD")

# 全局参数设置
SYMBOL = "SHFE.au2606"
POSITION_SIZE = 1
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
INIT_CASH = 20000


auth = TqAuth(TQ_USERNAME, TQ_PASSWORD)
api = TqApi(
    auth=auth,
    backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
    web_gui=True,
)
quote = api.get_quote(SYMBOL)
klines = api.get_kline_serial(SYMBOL, duration_seconds=1800, count=10000)
position = api.get_position(SYMBOL)

mid, top, bottom = BOLL(klines, 26, 2)

# 策略逻辑，根据最新价和BOLL线判断开仓方向
#   当最新价大于top, 开多仓位
if quote.last_price > top:
    api.insert_order(
        symbol=SYMBOL,
        direction="BUY",
        offset="OPEN",
        volume=POSITION_SIZE,
        price=quote.last_price,
    )
#   当最新价小于bottom, 开空仓位
elif quote.last_price < bottom:
    api.insert_order(
        symbol=SYMBOL,
        direction="SELL",
        offset="OPEN",
        volume=POSITION_SIZE,
    )
# 平仓逻辑, 如果持有多头头寸, 当最新价格小于中轨，则多头平仓
if position.pos_long > 0:
    if quote.last_price < mid:
        api.insert_order(
            symbol=SYMBOL,
            direction="SELL",
            offset="CLOSE",
            volume=POSITION_SIZE,
        )
# 平仓逻辑, 如果持有空头头寸, 当最新价格大于中轨，则空头平仓
elif position.pos_short > 0:
    if quote.last_price > mid:
        api.insert_order(
            symbol=SYMBOL,
            direction="BUY",
        )
