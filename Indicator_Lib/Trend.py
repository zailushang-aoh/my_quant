# 移动平均线（MA / EMA）
# MACD（指数平滑异同移动平均线）
# 布林带（BOLL，中轨为趋势参考）
import math

import numpy as np
import pandas as pd

import tqsdk.tafunc

def SMA(series, n):
    """
    简单移动平均线

    Args:
        series (pandas.Series): Series格式的K线序列

        n (int): 窗口大小

    Returns:
        pandas.Series: 输出的Series为简单移动平均线
        
    """
    sma_data = series.rolling(n).mean()
    return sma_data

def WMA(series, n):
    """
    Weighted Moving Average，加权移动平均线

    Args:
        series (pandas.Series): Series格式的K线序列

        n (int): 周期n

    Returns:
        pandas.Series: 输出的Series为加权移动平均线

    Example::

        # 获取 CFFEX.IF1903 合约的WMA
        from tqsdk import TqApi, TqAuth, TqSim  
        from tqsdk.ta import WMA
        api = TqApi(auth=TqAuth("快期账户", "账户密码"))
        klines = api.get_kline_serial("CFFEX.IF1903", 24 * 60 * 60)
        ma = WMA(klines, 26)
        print(list(ma))
        # 预计的输出是这样的:
        [..., 0.0, 0.0, 0.0, ...]
    """
    weights = np.arange(1, n + 1)
    weights_sum = weights.sum()

    # 使用 rolling().apply() 自定义加权平均
    wma_data = series.rolling(window=n).apply(
        lambda x: np.dot(x, weights) / weights_sum,
        raw=True  # 提高性能，传入的是 ndarray 而非 Series
    )
    return wma_data

def std(series, n):
    """
    标准差

    Args:
        series (pandas.Series): Series格式的K线序列

        n (int): 窗口大小

    Returns:
        pandas.Series: 输出的Series为标准差

    Example::

        # 获取 CFFEX.IF1903 合约的std
        from tqsdk import TqApi, TqAuth, TqSim  
        from tqsdk.ta import std
        api = TqApi(auth=TqAuth("快期账户", "账户密码"))
        klines = api.get_kline_serial("CFFEX.IF1903", 24 * 60 * 60)
        ma = std(klines, 26)
        print(list(ma))
        # 预计的输出是这样的:
        [..., 0.0, 0.0, 0.0, ...]
        """
    std_data = series.rolling(n).std()
    return std_data

def EMA(series, n):
    """
    指数移动平均线

    Args:
        df (pandas): Dataframe格式的K线序列
    """
    ema_date = series.ewm(span=n, adjust=False).mean()
    return ema_date

def MACD(df, n_fast, n_slow, n_signal):
    """
    Moving Average Convergence Divergence，指数平滑异同移动平均线    

    Args:
        df (pandas.DataFrame): Dataframe格式的K线序列
        n_fast (int): 快速EMA的周期
        n_slow (int): 慢速EMA的周期
        n_signal (int): 移动平均线（MACD）的信号线（SMA）的周期

    Returns:
        pandas.DataFrame: 输出包含3列, 分别是"dif", "dea"和"macd", 
        其中"dif"为快速EMA减慢速EMA, "dea"为dif的EMA, "macd"为dif-dea的2倍

    Example::

        # 获取 CFFEX.IF1903 合约的MACD
        from tqsdk import TqApi, TqAuth, TqSim
        from tqsdk.ta import MACD

        api = TqApi(auth=TqAuth("快期账户", "账户密码"))
        klines = api.get_kline_serial("CFFEX.IF1903", 24 * 60 * 60)
        macd = MACD(klines, 12, 26, 9)
        print(list(macd["dif"]))
        print(list(macd["dea"]))
        print(list(macd["macd"]))
        # 预计的输出是这样的:
        [..., 0.0, 0.0, 0.0, ...]
        [..., 0.0, 0.0, 0.0, ...]
        [..., 0.0, 0.0, 0.0, ...]
    """
    # 创建新的DataFrame用于存储MACD结果
    new_df = pd.DataFrame()
    # 计算快速EMA
    fast_ema = EMA(df["close"], n_fast)
    low_ema = EMA(df["low"], n_slow)
    # 创建新的DataFrame用于存储MACD结果
    new_df["dif"] = fast_ema - low_ema
    new_df["dea"] = EMA(new_df["dif"], n_signal)
    new_df["macd"] = 2 * (new_df["dif"] - new_df["dea"])
    return new_df

def BOLL(df, n, k):
    """
    布林线

    Args:
        df (pandas.DataFrame): Dataframe格式的K线序列
        n (int): 周期n 常见的取20
        k (int): 计算参数k 常见的取2(表示95%的置信区间, 假设价格服从正态分布)

    Returns:
        pandas.DataFrame: 返回的dataframe包含3列, 分别是"mid", "top"和"bottom", 分别代表布林线的中、上、下轨

    Example::

        # 获取 CFFEX.IF1903 合约的布林线
        from tqsdk import TqApi, TqAuth, TqSim
        from tqsdk.ta import BOLL

        api = TqApi(auth=TqAuth("快期账户", "账户密码"))
        klines = api.get_kline_serial("CFFEX.IF1903", 24 * 60 * 60)
        boll=BOLL(klines, 26, 2)
        print(list(boll["mid"]))
        print(list(boll["top"]))
        print(list(boll["bottom"]))

        # 预计的输出是这样的:
        [..., 3401.338461538462, 3425.600000000001, 3452.3230769230777, ...]
        [..., 3835.083909752222, 3880.677579320277, 3921.885406954584, ...]
        [..., 2967.593013324702, 2970.5224206797247, 2982.760746891571, ...]
    """
    # 创建新的DataFrame用于存储布林线结果
    new_df = pd.DataFrame()
    # 计算中轨：收盘价的n周期移动平均线
    mid = SMA(df["close"], n)
    # 计算标准差：收盘价的n周期滚动标准差
    std = df["close"].rolling(n).std()

    # 构造布林线三轨：
    # 中轨为移动平均线
    # 上轨为中轨加上p倍标准差
    # 下轨为中轨减去p倍标准差
    new_df["mid"] = mid
    new_df["top"] = mid + k * std
    new_df["bottom"] = mid - k * std
    return new_df