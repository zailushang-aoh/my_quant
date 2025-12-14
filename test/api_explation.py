
from tqsdk import TqApi, TqAuth, TargetPosTask, TqBacktest
from tqsdk.ta import BOLL
import os
from dotenv import load_dotenv

# 从环境变量读取凭据，避免在代码中明文写入密码
load_dotenv()
TQ_USERNAME = os.getenv("TQ_USERNAME")
TQ_PASSWORD = os.getenv("TQ_PASSWORD")

auth = TqAuth(TQ_USERNAME, TQ_PASSWORD)
api = TqApi(
    auth=auth,
    # account="TQBR-17318514219-CTPsim-17318514219",
    # backtest=TqBacktest(start_dt="2023-06-01", end_dt="2023-06-30"),
    # debug=False,
    # loop=True,
    # disable_print=False,
)

# 获取上期所镍的行情数据
quote = api.get_quote("SHFE.ni2610")

# 输出quote所有可以输出的信息
print(quote.datetime, #: 行情从交易所发出的时间(北京时间), 格式为 "2017-07-26 23:04:21.000001"
      quote.last_price, #: 最新价

      quote.bid_price1,#: 买一价
      quote.bid_volume1, #: 卖一量
      quote.ask_price1,#: 卖一价
      quote.ask_volume1, #: 买一量

      quote.highest,#: 当日最高价
      quote.lowest,#: 当日最低价
      quote.open,#: 开盘价
      quote.close,#: 收盘价
      quote.average,#: 当日均价
      quote.volume,#: 成交量
      quote.amount,#: 成交额

      quote.open_interest, #: 持仓量
      quote.settlement, #: 结算价
      quote.upper_limit, #: 涨停价
      quote.lower_limit, #: 跌停价
      quote.pre_settlement ,#: 昨结算
      quote.pre_open_interest, #: 昨持仓
      quote.pre_close, #: 昨收盘
      quote.price_tick,#: 合约价格变动单位
      quote.price_decs,#: 合约价格小数位数
      quote.volume_multiple,#: 合约乘数
      quote.max_limit_order_volume,#: 最大限价单手数
      quote.min_limit_order_volume,#: 最小限价单手数
      quote.max_market_order_volume,#: 最大市价单手数
      quote.min_market_order_volume,#: 最小市价单手数
      quote.open_max_limit_order_volume,#: 最大限价开仓手数
      quote.open_max_market_order_volume,#: 最大市价开仓手数
      quote.open_min_limit_order_volume,#: 最小限价开仓手数
      quote.open_min_market_order_volume,#: 最小市价开仓手数
      quote.underlying_symbol,#: 标的合约
      quote.strike_price,#: 行权价
      quote.ins_class,#: 合约类型
      quote.instrument_id,#: 合约代码，包含了交易所代码
      quote.instrument_name,#: 合约中文名
      quote.exchange_id,#: 交易所代码
      quote.expired,#: 合约是否已下市
      quote.trading_time,#: 交易时间段
      quote.expire_datetime,#: 到期具体日，以秒为单位的 timestamp 值
      quote.delivery_month,#: 期货交割日年份，只对期货品种有效。期权推荐使用最后行权日年份
      quote.delivery_year,#: 期货交割日年份，只对期货品种有效。期权推荐使用最后行权日年份
      quote.last_exercise_datetime,#: 期权最后行权日，以秒为单位的 timestamp 值
      quote.exercise_year, #: 期权最后行权日年份，只对期权品种有效。
      quote.exercise_month,#: 期权最后行权日年份，只对期权品种有效。
      quote.option_class,#: 期权方向
      quote.exercise_type,#: 期权行权方式，美式:'A'，欧式:'E'
      quote.product_id,#: 品种代码
      quote.iopv,#: ETF实时单位基金净值
      quote.public_float_share_quantity,#: 日流通股数，只对证券产品有效。
      quote.stock_dividend_ratio,#: 除权表 ["20190601,0.15","20200107,0.2"…]
      quote.cash_dividend_ratio,#: 除息表 ["20190601,0.15","20200107,0.2"…]
      quote.expire_rest_days,#: 距离到期日的剩余天数（自然日天数），正数表示距离到期日的剩余天数，0表示到期日当天，负数表示距离到期日已经过去的天数
      quote.categories,#: 板块信息
      quote.position_limit #: 持仓限额
      )

# 获取tick数据
ticks = api.get_tick_serial("SHFE.ni2610", data_length=10000)
print(ticks.info)

# 获取k线数据
klines = api.get_kline_serial("SHFE.ni2610", data_length=10000, duration_seconds=1800)
print(klines.info)

# 下单
position = api.get_position("SHFE.ni2610")
account = api.get_account("SHFE.ni2610")
# 下单并返回委托单的引用，当该委托单有变化时 order 中的字段会对应更新
order = api.insert_order(symbol="SHFE.ni2610", direction="BUY", offset="OPEN", volume=5, limit_price=2750, advanced="FOK")
print("单状态: %s, 已成交: %d 手" % (order.status, order.volume_orign - order.volume_left))



while True:
    # 调用 wait_update 等待业务信息发生变化，例如: 行情发生变化, 委托单状态变化, 发生成交等等
    # 注意：其他合约的行情的更新也会触发业务信息变化，因此下面使用 is_changing 判断 FG209 的行情是否有变化
    api.wait_update()
    # 如果 FG209 的任何字段有变化，is_changing就会返回 True
    if api.is_changing(quote):
        print("行情变化", quote)
    # 只有当 FG209 的最新价有变化，is_changing才会返回 True
    if api.is_changing(quote, "last_price"):
        print("最新价变化", quote.last_price)
    # 当 FG209 的买1价/买1量/卖1价/卖1量中任何一个有变化，is_changing都会返回 True
    if api.is_changing(quote, ["ask_price1", "ask_volume1", "bid_price1", "bid_volume1"]):
        print("盘口变化", quote.ask_price1, quote.ask_volume1, quote.bid_price1, quote.bid_volume1)

api.close()
