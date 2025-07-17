import pandas as pd
import numpy as np
import ta

def sma(data, period=20):
    return data['Close'].rolling(window=period).mean()

def ema(data, period=20):
    return data['Close'].ewm(span=period, adjust=False).mean()

def bollinger_bands(data, period=20):
    sma_ = sma(data, period)
    std = data['Close'].rolling(window=period).std()
    upper = sma_ + 2 * std
    lower = sma_ - 2 * std
    return sma_, upper, lower

def rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(data, fast=12, slow=26, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def stochastic_oscillator(data, k_period=14, d_period=3):
    low_min = data['Low'].rolling(window=k_period).min()
    high_max = data['High'].rolling(window=k_period).max()
    k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d

def fibonacci_retracement(data):
    max_price = data['High'].max()
    min_price = data['Low'].min()
    diff = max_price - min_price
    levels = {
        '0.0%': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '78.6%': max_price - 0.786 * diff,
        '100.0%': min_price
    }
    return levels

def ichimoku_cloud(data):
    nine_high = data['High'].rolling(window=9).max()
    nine_low = data['Low'].rolling(window=9).min()
    tenkan_sen = (nine_high + nine_low) / 2

    period26_high = data['High'].rolling(window=26).max()
    period26_low = data['Low'].rolling(window=26).min()
    kijun_sen = (period26_high + period26_low) / 2

    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    period52_high = data['High'].rolling(window=52).max()
    period52_low = data['Low'].rolling(window=52).min()
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

    chikou_span = data['Close'].shift(-26)

    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

def standard_deviation(data, period=20):
    return data['Close'].rolling(window=period).std()

def adx(data, period=14):
    adx_indicator = ta.trend.ADXIndicator(high=data['High'], low=data['Low'], close=data['Close'], window=period)
    return adx_indicator.adx()
