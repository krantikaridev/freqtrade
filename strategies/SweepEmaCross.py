"""
Sweep 1 — trend (stock freqtrade pattern: EMA cross + ADX gate).

Written for the 6 Oct parallel backtest sweep (#580). Long-only futures,
no protections of its own so the sweep runs the same rules for every arm.
Parameters are hyperopt-able so the winner can be tuned without a rewrite.
"""

from freqtrade.strategy import DecimalParameter, IStrategy
import talib.abstract as ta
from pandas import DataFrame


class SweepEmaCross(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "4h"

    minimal_roi = {"0": 0.10, "48": 0.05, "96": 0.02}
    stoploss = -0.06

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    startup_candle_count = 220

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    fast_ema = DecimalParameter(10, 30, default=20, decimals=0, space="buy")
    slow_ema = DecimalParameter(40, 120, default=50, decimals=0, space="buy")
    adx_threshold = DecimalParameter(15, 35, default=20, decimals=0, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=int(self.fast_ema.value))
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=int(self.slow_ema.value))
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["close"] > dataframe["ema_slow"])
                & (dataframe["adx"] > self.adx_threshold.value)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["ema_fast"] < dataframe["ema_slow"]) & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
