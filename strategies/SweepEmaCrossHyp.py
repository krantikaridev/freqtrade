"""SweepEmaCross with the #580 $250-stake hyperopt result written back as defaults.

Derived from hyperopt run strategy_SweepEmaCross_2026-10-06_16-27-28.fthypt
(20 epochs, buy space only, Sharpe loss, 1h, 2026-04-09..2026-10-06).
"""
from SweepEmaCross import SweepEmaCross
from freqtrade.strategy import DecimalParameter


class SweepEmaCrossHyp(SweepEmaCross):
    fast_ema = DecimalParameter(10, 30, default=24, decimals=0, space="buy")
    slow_ema = DecimalParameter(40, 120, default=78, decimals=0, space="buy")
    adx_threshold = DecimalParameter(15, 35, default=15, decimals=0, space="buy")
