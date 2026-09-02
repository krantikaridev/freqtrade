"""
Sleeve 2 — Trend Following (MVP v1)

Simple, maintainable trend continuation for Binance USDT-M majors.
Timeframe: 4h (configured in config.dryrun.json).

Edge hypothesis: ride established trends with EMA structure + ADX filter;
skip chop. Not claimed profitable until dry-run / backtest evidence.
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.persistence import Trade
from datetime import datetime
from typing import Optional


class TrendFollowing(IStrategy):
    INTERFACE_VERSION = 3

    # Futures: allow both directions later; start long-biased for MVP simplicity
    can_short = True

    timeframe = "4h"

    # Conservative exits — preserve capital first
    minimal_roi = {
        "0": 0.12,
        "24": 0.06,
        "72": 0.03,
        "168": 0.01,
    }

    stoploss = -0.06

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    startup_candle_count = 200

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": True,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    @property
    def protections(self):
        return [
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 2,
                "stop_duration_candles": 12,
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 48,
                "trade_limit": 1,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.12,
            },
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=21)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=55)
        dataframe["ema_trend"] = ta.EMA(dataframe, timeperiod=200)

        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["plus_di"] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe["minus_di"] = ta.MINUS_DI(dataframe, timeperiod=14)

        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["volume_ma"] = dataframe["volume"].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Long: price above long EMA, fast > slow, ADX confirms trend, +DI dominates
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["ema_trend"])
                & (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["adx"] > 22)
                & (dataframe["plus_di"] > dataframe["minus_di"])
                & (dataframe["volume"] > dataframe["volume_ma"] * 0.8)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1

        # Short: mirror
        dataframe.loc[
            (
                (dataframe["close"] < dataframe["ema_trend"])
                & (dataframe["ema_fast"] < dataframe["ema_slow"])
                & (dataframe["adx"] > 22)
                & (dataframe["minus_di"] > dataframe["plus_di"])
                & (dataframe["volume"] > dataframe["volume_ma"] * 0.8)
                & (dataframe["volume"] > 0)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit long when trend structure breaks
        dataframe.loc[
            (
                (dataframe["ema_fast"] < dataframe["ema_slow"])
                | (dataframe["plus_di"] < dataframe["minus_di"])
            ),
            "exit_long",
        ] = 1

        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                | (dataframe["minus_di"] < dataframe["plus_di"])
            ),
            "exit_short",
        ] = 1

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        # Cap per-trade risk: ~2% of dry wallet via stake sizing floor/ceiling
        # Freqtrade already applies stake_amount/tradable_balance_ratio;
        # keep proposed stake within max_stake.
        stake = min(proposed_stake, max_stake)
        if min_stake is not None:
            stake = max(stake, min_stake)
        return stake

    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        # Conservative futures leverage for MVP dry-run
        return min(2.0, max_leverage)
