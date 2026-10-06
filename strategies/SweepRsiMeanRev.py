"""
Sweep 2 — mean-reversion (stock freqtrade pattern: RSI dip buy, fade back to mean).

Long-only futures. Same fee/stake/exits contract as the other sweep arms.
"""

from freqtrade.strategy import DecimalParameter, IStrategy
import talib.abstract as ta
from pandas import DataFrame


class SweepRsiMeanRev(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "4h"

    minimal_roi = {"0": 0.04}
    stoploss = -0.05

    trailing_stop = False

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

    rsi_buy = DecimalParameter(10, 40, default=30, decimals=0, space="buy")
    rsi_sell = DecimalParameter(55, 85, default=70, decimals=0, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["bb_lower"] = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)["lowerband"]
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Buy the dip only while price is still above the long-term trend,
        # otherwise mean reversion just catches falling knives.
        dataframe.loc[
            (
                (dataframe["rsi"] < self.rsi_buy.value)
                & (dataframe["close"] < dataframe["bb_lower"])
                & (dataframe["close"] > dataframe["ema_200"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > self.rsi_sell.value)
                | (dataframe["close"] > dataframe["ema_200"] * 1.05)
            )
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
