# Hybrid Sleeve System - Sleeve Documentation

## Overview

This document provides detailed information about each trading sleeve, their design, implementation status, and roadmap.

## Sleeve 1: X-Signal Momentum

### Profile

| Attribute | Value |
|-----------|-------|
| **File** | `sleeves/implementations/x_signal_momentum.py` |
| **Class** | `XSignalMomentumSleeve` |
| **Timeframe** | 1-7 days |
| **Style** | High-conviction swing trading |
| **Initial Allocation** | 45-55% |
| **Primary Edge** | Strong signals from X (Twitter) |
| **Position Style** | Aggressive |

### Characteristics

- **Signal-Heavy**: Relies heavily on high-quality signals from X/Twitter
- **Fast Growth**: Designed for capital appreciation
- **Conviction-Based**: Only enters on strong, high-conviction setups
- **Swing Duration**: Holds 1-7 days per position

### Risk Parameters

```python
RiskConfig(
    sleeve_id="x_signal_momentum",
    min_allocation=0.45,
    max_allocation=0.55,
    max_position_size=0.10,        # 10% per position
    max_open_positions=5,          # Up to 5 concurrent positions
    stop_loss_pct=0.05,           # 5% stop loss
    risk_per_trade=0.02            # 2% risk per trade
)
```

### Implementation Status

**Current**: Foundation only

- ✅ Base class structure
- ✅ Performance tracking
- ❌ X signal scoring system
- ❌ Market data integration
- ❌ Technical confirmation logic

### TODO

1. **X Signal Integration**
   - Connect to X API or signal aggregator
   - Score signals by: account influence, accuracy history, conviction level
   - Filter signals: only process high-conviction (score > 0.7)
   - Age filter: discard signals older than 24 hours

2. **Technical Confirmation**
   - Validate signal with price action
   - Check for oversold/overbought conditions
   - Confirm with volume surge

3. **Entry Logic**
   - Market order on signal receipt (or limit near current)
   - Position size = account risk / stop loss distance

4. **Exit Logic**
   - Hard stop at 5% loss
   - Trailing stop for profitable trades
   - Time-based exit: close after 7 days max

### Signal Example

```python
SleeveSignal(
    sleeve_id="x_signal_momentum",
    symbol="BTC/USDT",
    signal_type="buy",           # or 'sell'
    confidence=0.85,             # 85% confidence from X signal
    entry_price=42500.0,
    stop_loss=40375.0,           # 5% below entry
    take_profit=47500.0,         # 11.8% above entry
    timestamp=datetime.utcnow()
)
```

---

## Sleeve 2: Trend Following

### Profile

| Attribute | Value |
|-----------|-------|
| **File** | `sleeves/implementations/trend_following.py` |
| **Class** | `TrendFollowingSleeve` |
| **Timeframe** | 3-21 days |
| **Style** | Trend continuation |
| **Initial Allocation** | 25-35% |
| **Primary Edge** | Technical + narrative strength |
| **Position Style** | Moderate |

### Characteristics

- **Trend-Focused**: Identifies and rides strong trends
- **Stable Returns**: Lower volatility than Sleeve 1
- **Technical-Based**: Uses chart patterns and indicators
- **Narrative-Aware**: Confirms with news/sentiment
- **Longer Holding**: 3-21 day positions

### Risk Parameters

```python
RiskConfig(
    sleeve_id="trend_following",
    min_allocation=0.25,
    max_allocation=0.35,
    max_position_size=0.08,        # 8% per position
    max_open_positions=4,          # Up to 4 concurrent positions
    stop_loss_pct=0.07,           # 7% stop loss
    risk_per_trade=0.015           # 1.5% risk per trade
)
```

### Implementation Status

**Current**: Foundation only

- ✅ Base class structure
- ✅ Performance tracking
- ❌ Trend detection logic
- ❌ Technical indicator setup
- ❌ Narrative scoring

### TODO

1. **Trend Detection**
   - Moving average crossovers (50/200 MA)
   - Trend strength: measure slope and consistency
   - Minimum trend bars: 5+ consecutive highs or lows

2. **Technical Indicators**
   - MACD for momentum confirmation
   - RSI for overbought/oversold extremes
   - ADX for trend strength
   - Volume for confirmation

3. **Entry Logic**
   - Wait for pullback in established trend
   - Enter on bounce back to moving average
   - Position size = account risk / stop loss distance

4. **Exit Logic**
   - Hard stop at 7% loss
   - Trail stop: 1.5x average true range
   - Time-based: close after 21 days max

### Signal Example

```python
SleeveSignal(
    sleeve_id="trend_following",
    symbol="ETH/USDT",
    signal_type="buy",
    confidence=0.72,             # Moderate confidence
    entry_price=2250.0,
    stop_loss=2092.5,            # 7% below entry
    take_profit=2700.0,          # 20% above entry (strong trend)
    timestamp=datetime.utcnow()
)
```

---

## Sleeve 3: Tactical Mean Reversion

### Profile

| Attribute | Value |
|-----------|-------|
| **File** | `sleeves/implementations/tactical_mean_reversion.py` |
| **Class** | `TacticalMeanReversionSleeve` |
| **Timeframe** | Hours - 4 days |
| **Style** | Mean reversion on extremes |
| **Initial Allocation** | 15-25% |
| **Primary Edge** | Overextended moves + X signals |
| **Position Style** | Conservative |

### Characteristics

- **Tactical**: Exploits short-term overextensions
- **High Frequency**: Smaller but more frequent trades
- **Tight Risk**: Small stop losses, quick exits
- **Mean-Reversion-Focused**: Trades against extremes
- **Quick Turnarounds**: 1-4 day positions typical

### Risk Parameters

```python
RiskConfig(
    sleeve_id="tactical_mean_reversion",
    min_allocation=0.15,
    max_allocation=0.25,
    max_position_size=0.05,        # 5% per position
    max_open_positions=3,          # Up to 3 concurrent positions
    stop_loss_pct=0.03,           # 3% stop loss (tight)
    risk_per_trade=0.01            # 1% risk per trade
)
```

### Implementation Status

**Current**: Foundation only

- ✅ Base class structure
- ✅ Performance tracking
- ❌ Mean reversion detection
- ❌ Bollinger Band logic
- ❌ Volume confirmation

### TODO

1. **Mean Reversion Detection**
   - Bollinger Band breakouts: identify extremes
   - Z-score: measure deviation from mean (target 2.0+ std devs)
   - RSI: overbought (>70) or oversold (<30)
   - Volume: confirm with volume surge

2. **Setup Identification**
   - Price breaks 2-sigma Bollinger Band
   - RSI in extreme zone
   - Volume spike on breakdown
   - Identify pullback/reversal signals

3. **Entry Logic**
   - Enter on reversal candle or signal
   - Conservative position sizing (1% risk per trade)
   - Quick execution (limit orders near resistance)

4. **Exit Logic**
   - Hard stop at 3% loss (tight)
   - Target: 50% reversion of move ("reversion_target=0.5")
   - Time-based: close after 4 days max
   - Trail stop: dynamic based on reversion progress

### Signal Example

```python
SleeveSignal(
    sleeve_id="tactical_mean_reversion",
    symbol="SOL/USDT",
    signal_type="buy",
    confidence=0.68,             # Moderate-low confidence
    entry_price=98.0,
    stop_loss=95.06,             # 3% tight stop
    take_profit=103.0,           # ~50% reversion of the move
    timestamp=datetime.utcnow()
)
```

---

## Performance Metrics

Each sleeve tracks:

```python
@dataclass
class SleevePerformance:
    sleeve_id: str
    trades_executed: int         # Total trades sent by sleeve
    win_rate: float              # % of trades with profit
    profit_loss_pct: float       # Cumulative P&L %
    sharpe_ratio: Optional[float] # Risk-adjusted return (TBD)
    drawdown_pct: float          # Current drawdown from peak
    last_updated: Optional[datetime]
```

## Dynamic Allocation Strategy

Allocations are adjusted based on:

1. **Recent Performance** (7-14 days):
   - Best performer gets more allocation
   - Losing performer gets less
   - Enforce min/max bounds per sleeve

2. **Market Regime**:
   - Trending market: Increase Sleeve 2 allocation
   - Choppy market: Increase Sleeve 3 allocation
   - High-conviction signals: Increase Sleeve 1 allocation

3. **Portfolio Drawdown**:
   - If drawdown > 75% of limit: Reduce all allocations by 25%
   - If drawdown >= limit: Pause all trading

4. **Allocation Constraints**:
   - No sleeve < 10% (floor)
   - No sleeve > 60% (ceiling)
   - All sleeves sum to 100%

## Future Enhancements

### Short-term (v1.1)
- [ ] Integrate real market data feeds
- [ ] Add backtesting support
- [ ] Implement signal confirmation logic
- [ ] Add alert system

### Medium-term (v2.0)
- [ ] ML-based signal scoring
- [ ] Sentiment analysis integration
- [ ] Advanced technical indicators
- [ ] Options strategies

### Long-term (v3.0+)
- [ ] Multi-exchange support
- [ ] Quantitative optimization
- [ ] Real-time dashboards
- [ ] Strategy marketplace

## Testing Sleeves

### Manual Testing

```bash
# Start system in dev mode
python main.py

# Monitor output for signals and trades
# Check logs/ for detailed execution
```

### Unit Testing (TBD)

```bash
pytest tests/sleeves/
pytest tests/risk_management/
```

## Integration Notes

- Each sleeve runs independently within the system
- Sleeves share risk management but make independent decisions
- Coordination happens at the system level (HybridSleeveSystem)
- No inter-sleeve dependencies (loosely coupled)
