"""
Sweep 3 — breakout (stock freqtrade pattern: Donchian/rolling-high breakout on volume).

Long-only futures. Same fee/stake/exits contract as the other sweep arms.
"""

from freqtrade.strategy import DecimalParameter, IStrategy
import talib.abstract as ta
from pandas import DataFrame


class SweepDonchianBreakout(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "4h"

    minimal_roi = {"0": 0.12, "72": 0.06, "168": 0.02}
    stoploss = -0.05

    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.03
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

    breakout_period = DecimalParameter(12, 60, default=20, decimals=0, space="buy")
    vol_mult = DecimalParameter(1.0, 2.5, default=1.5, decimals=1, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        period = int(self.breakout_period.value)
        dataframe["don_high"] = dataframe["high"].rolling(period).max().shift(1)
        dataframe["don_low"] = dataframe["low"].rolling(period).min().shift(1)
        dataframe["vol_sma"] = dataframe["volume"].rolling(20).mean()
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["don_high"])
                & (dataframe["volume"] > self.vol_mult.value * dataframe["vol_sma"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["don_low"]) & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
