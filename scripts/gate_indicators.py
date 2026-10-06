"""Entry-time indicators for the gate replay (no lookahead)."""
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def adx_wilder(df: pd.DataFrame, n: int = 14):
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus_dm = ((up > dn) & (up > 0)) * up
    minus_dm = ((dn > up) & (dn > 0)) * dn
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift()).abs(),
                    (df["low"] - df["close"].shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / n, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, float("nan"))
    return dx.ewm(alpha=1 / n, adjust=False).mean(), plus_di, minus_di


def load_candles(pair: str, tf: str) -> pd.DataFrame:
    slug = pair.replace("/", "_").replace(":", "_")
    path = "data/binance/futures/%s-%s-futures.feather" % (slug, tf)
    df = pd.read_feather(path).sort_values("date").reset_index(drop=True)
    df["ema_fast"] = ema(df["close"], 21)
    df["ema_slow"] = ema(df["close"], 55)
    df["ema_trend"] = ema(df["close"], 200)
    df["adx"], df["pdi"], df["mdi"] = adx_wilder(df)
    df["vol_ma"] = df["volume"].rolling(20).mean()
    return df
