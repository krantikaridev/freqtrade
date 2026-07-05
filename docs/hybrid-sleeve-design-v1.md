# Hybrid Sleeve Design v1

**Status**: v1 (Active Development)  
**Date**: July 2026  
**Audience**: Development team, traders, stakeholders  
**Goal**: Build a scalable, multi-strategy trading system on Freqtrade with dynamic risk allocation and high-quality trade filtering.

---

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
2. [Sleeve Structure (v1)](#2-sleeve-structure-v1)
3. [Sleeve Specifications](#3-sleeve-specifications)
4. [Trade Quality Requirements](#4-trade-quality-requirements)
5. [Dynamic Risk Allocation Rules (v1)](#5-dynamic-risk-allocation-rules-v1)
6. [Signal Sources](#6-signal-sources)
7. [Instruments & Trading Mechanics](#7-instruments--trading-mechanics)
8. [System-Level Risk Management](#8-system-level-risk-management)
9. [Success Metrics for v1](#9-success-metrics-for-v1)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Open Questions & Future Iterations](#11-open-questions--future-iterations)

---

## 1. Overview & Philosophy

The **Hybrid Sleeve** system is a multi-strategy trading approach that combines three distinct sleeves (strategies) with different characteristics, time horizons, and risk profiles. Rather than running a single monolithic strategy, sleeves operate in parallel and share a common capital pool with **dynamic risk allocation**.

### Guiding Principles

- **Quality over Quantity**: High-conviction trades preferred over high-frequency trading. Nanoclaw taught us that many mediocre trades + small capital = death spiral.
- **Dynamic Risk Allocation**: Risk budgets are adjusted based on sleeve performance, market conditions, and portfolio state—not locked into fixed percentages.
- **Strong Signal Focus**: Primary edge comes from high-quality signals from X (formerly Twitter), supplemented by technical analysis.
- **Start Simple, Iterate**: v1 focuses on core mechanics; sophistication increases with real performance data.
- **Accessible Instruments**: Focus on crypto perpetuals and tokenized assets with high liquidity and fast execution.
- **Day-to-Week Timeframe**: Emphasis on swing trading and tactical positioning; not scalping or ultra-long-term holding.

---

## 2. Sleeve Structure (v1)

We will start with **3 sleeves**, each optimized for a specific trading style and market condition:

| Sleeve | Name                    | Style                    | Timeframe     | Primary Edge Source       | Initial Risk Budget | Status |
|--------|-------------------------|--------------------------|---------------|---------------------------|---------------------|--------|
| 1      | X-Signal Momentum       | High-conviction Swing    | 1–7 days      | Strong signals from X     | 45–55%              | Active |
| 2      | Trend Following         | Trend Continuation       | 3–21 days     | Technical + Narrative     | 25–35%              | Active |
| 3      | Tactical Mean Reversion | Short-term Reversion     | Hours – 4 days| Overextended moves + X    | 15–25%              | Active |

### Sleeve Characteristics

**Allocation Strategy:**
- Initial (default) allocation: Sleeve 1 = 50%, Sleeve 2 = 30%, Sleeve 3 = 20%
- Allocation is **dynamic** and adjusts based on performance and system state
- No single sleeve shall exceed 65% of total risk capital at any time (cap)
- No single sleeve shall fall below 10% unless in emergency drawdown mode

---

## 3. Sleeve Specifications

### Sleeve 1: X-Signal Momentum

**Purpose**: Capture high-conviction, fast-moving opportunities based on strong X signals.

**Entry Criteria**:
- Signal strength from X >= 75% confidence (manually scored or ML-based)
- Confirmed technical setup (e.g., support break, breakout above resistance)
- Risk/reward ratio >= 1:2 (1% risk for 2% potential gain)
- Signal posted within last 6–12 hours (fresh signals only)
- No recent loss streak on this sleeve (max 2 consecutive losses)

**Exit Criteria**:
- Target price hit (partial or full)
- Stop loss triggered (pre-defined based on technical level)
- Time-based exit after 5–7 days if not profitable (tactical exit)
- System drawdown > 15% (protective exit, may hold at reduced size)

**Position Sizing**:
- Max position size: 3–5% of account per trade
- Risk per trade: 0.8–1.2% of account
- Adjusted downward if system volatility is elevated (ATR > 60th percentile)

**Time Horizon**:
- Typical hold: 1–7 days
- Target: 3–4 day average hold time
- Exit within market hours or at tactical breakout

**Performance Target**:
- Win rate: >= 55%
- Average winner: 2.0–3.0x average loser
- Monthly return target: 3–5% (with 15% max drawdown constraint)

---

### Sleeve 2: Trend Following

**Purpose**: Ride established trends with lower-conviction but more stable setups.

**Entry Criteria**:
- ADX (Average Directional Index) >= 25 (strong trend)
- Price above 200-day MA (uptrend) or below (downtrend)
- Technical confirmation: higher low (uptrend) or lower high (downtrend)
- Risk/reward ratio >= 1:3 (lower conviction → higher reward target)
- Not entering during consolidation phases (volatility < 30th percentile excluded)

**Exit Criteria**:
- Trend break (ADX < 20 or 200-day MA cross)
- Breakeven stop + profit target cascade (e.g., 1st target at 1:1, move stop to breakeven)
- Time-based exit after 14–21 days (rebalance opportunity)
- Trailing stop if profitable (let winners run)
- System drawdown > 20% (protective exit)

**Position Sizing**:
- Max position size: 2–4% of account per trade
- Risk per trade: 0.5–0.8% of account
- Generally smaller than Sleeve 1 due to longer hold time

**Time Horizon**:
- Typical hold: 3–21 days
- Target: 7–10 day average hold time
- Can hold longer if trend remains strong (with trailing stops)

**Performance Target**:
- Win rate: >= 50% (longer time horizon, accept lower win rate)
- Average winner: 2.5–4.0x average loser (higher reward to compensate)
- Monthly return target: 2–4%

---

### Sleeve 3: Tactical Mean Reversion

**Purpose**: Capture frequent but smaller opportunities from overextended moves.

**Entry Criteria**:
- Price overextended > 2 standard deviations from 20-period moving average
- Confirmation from oscillator (RSI 70+ or 30-, or MACD divergence)
- X signal if available (secondary confirmation, not required)
- Risk/reward ratio >= 1:1.5 (high frequency → lower reward per trade)
- Lower confidence trades acceptable here (signal strength >= 50%)

**Exit Criteria**:
- Move back to mean (20-period MA) or within 1 std dev
- Stop loss at opposite extreme (e.g., 3+ std dev if shorting oversold)
- Time-based exit after 1–4 days (don't hold reversion plays long-term)
- System drawdown > 15% (conservative reversion trades)
- Profit target hit (often small, 0.5–1.5% per trade)

**Position Sizing**:
- Max position size: 1.5–3% of account per trade
- Risk per trade: 0.3–0.6% of account (highest frequency → smallest per-trade risk)
- Can have multiple concurrent positions (up to 3–4)

**Time Horizon**:
- Typical hold: Hours to 4 days
- Target: 1–2 day average hold time
- Quick exit on confirmed reversal

**Performance Target**:
- Win rate: >= 55% (smaller moves = higher win rate easier)
- Average winner: 1.0–2.0x average loser (smaller moves, quick exits)
- Monthly return target: 1–2%
- Frequency: 8–15 trades per month (2–3 per week)

---

## 4. Trade Quality Requirements

All trades across all sleeves must pass a **quality gate** before execution. This prevents the "Nanoclaw trap" of high rotation + low-quality trades.

### Entry Quality Thresholds

| Criterion | Sleeve 1 | Sleeve 2 | Sleeve 3 | Rationale |
|-----------|----------|----------|----------|-----------|
| **Min Signal Strength** | 75% | 60% | 50% | Higher conviction for faster trades |
| **Min Edge Estimate** | 0.8% | 0.5% | 0.3% | Must have measurable positive expectancy |
| **Min R:R Ratio** | 1:2 | 1:3 | 1:1.5 | Reward must justify risk |
| **System Drawdown Block** | > 20% | > 25% | > 15% | Stop new trades during losses |

### Quality Metrics

- **Signal Strength**: Confidence level in trade opportunity (0–100%)
  - Sleeve 1: Derived from X signal quality + technical confirmation score
  - Sleeve 2: Technical setup clarity (trend strength, confirmation quality)
  - Sleeve 3: Oscillator reading + mean-reversion setup robustness

- **Edge Estimate**: Expected win rate × average winner − (1 − win rate) × average loser
  - Calculated from backtest or recent historical performance
  - Must be positive after accounting for slippage and commissions

- **Risk/Reward Ratio**: Exit target (in $) ÷ Stop loss (in $)
  - Tighter stops = higher frequency (Sleeve 3)
  - Wider stops = lower frequency (Sleeves 1 & 2)

### Play Budget (Trade Frequency Limit)

To prevent over-trading, daily play budgets are enforced:

| Sleeve | Max Trades / Day | Max Trades / Week | Rationale |
|--------|------------------|-------------------|-----------|
| Sleeve 1 | 3 | 8 | High conviction → fewer opportunities |
| Sleeve 2 | 2 | 5 | Trend setup → lower frequency |
| Sleeve 3 | 5 | 12 | Reversion → more frequent |
| **System Total** | **8** | **20** | Prevents over-rotation |

- **Daily reset**: Play budgets reset at 00:00 UTC
- **Enforcement**: Trades are rejected if daily budget is exhausted, regardless of signal quality
- **Override**: Manual override possible during exceptional market conditions (documented in trade log)

---

## 5. Dynamic Risk Allocation Rules (v1)

Instead of static allocation percentages, risk is dynamically adjusted based on sleeve performance and system state. This allows the system to concentrate capital where it's working and retreat where it's struggling.

### Base Allocation (Default State)

```
Sleeve 1 (X-Signal Momentum):     50% of risk capital
Sleeve 2 (Trend Following):       30% of risk capital
Sleeve 3 (Tactical Mean Rev):     20% of risk capital
```

### Performance-Based Adjustment (7-Day Lookback)

Each sleeve tracks recent performance and adjusts allocation:

```
Sleeve Return (7d)      Allocation Adjustment     Max Cap
+5.0% or better         +5% (55% → 58% max)       65%
+2.0% to +5.0%          +2% (52% → 54%)           65%
0% to +2.0%             No change
-1.0% to 0%             -2% (48% → 50%)           50%
-2.0% to -1.0%          -4% (46% → 48%)           45%
-5.0% or worse          -8% (42% to 50%) + pause  35%
```

**Mechanics**:
- Calculate 7-day Sharpe ratio (or simple return) for each sleeve
- Update allocation quarterly (every 2 weeks) to avoid whipsaw
- Reallocate capital smoothly (don't move all at once)
- Rebalance occurs at start of trading day (UTC 00:00)

### Drawdown-Based Risk Reduction

**Portfolio Drawdown Level** → **Overall Risk Scale Factor**

```
Current Drawdown     Risk Scale     Trading Mode
0% to 5%             100%           Aggressive (normal)
5% to 10%            85%            Cautious (reduce size slightly)
10% to 15%           70%            Defensive (half-size trades)
15% to 20%           50%            Conservative (quarter-size)
> 20%                0%             Paused (no new trades)
```

**Application**:
- All position sizes are multiplied by the risk scale
- Sleeve 3 (safest) reduces last; Sleeve 1 (aggressive) reduces first
- If portfolio DD > 20%, **no new trades** regardless of sleeve allocation
- If portfolio DD > 25%, **close open positions gradually** (over 2–4 hours)

### Volatility Adjustment

Market-wide volatility affects position sizing:

```
VIX Equivalent (Crypto)   Position Size Adjustment
< 20 (Low vol)            110% (can go slightly larger)
20–35 (Normal)            100% (default)
35–50 (High vol)          75% (reduce size)
> 50 (Panic vol)          50% (very cautious)
```

- VIX equivalent for crypto calculated as 30-day rolling ATR percentile
- Adjustment applied to all sleeves equally

### Constraint Rules (Hard Limits)

1. **No single sleeve** exceeds 65% of total risk at any time
2. **No single sleeve** falls below 10% unless in emergency mode (DD > 20%)
3. **Total per-trade risk** never exceeds 1.5% of account
4. **Max concurrent open positions** across all sleeves: 8
5. **Max correlation-weighted exposure** to any single asset: 5% of account

---

## 6. Signal Sources

### Primary: X (Twitter) Signals

**Criteria for High-Quality X Signals**:
- Posted by known, verified traders/analysts with track record
- Clear entry/exit levels specified (specific price points, not vague)
- Technical reasoning provided (not just "buy because bullish")
- Tagging relevant assets with clear timeframe (e.g., "$BTC 1D" or "ETH swing trade")
- Community validation (strong engagement, likes/retweets from other credible sources)

**Processing Flow**:
1. Monitor X accounts for new posts
2. Score signal quality (0–100%) based on criteria above
3. Perform additional technical confirmation
4. Add to trade queue for next opportunity
5. Log signal source and reasoning in trade journal

### Secondary: Technical Indicators

**Sleeve 1 & 2**: ADX, Moving Averages (20/50/200), Support/Resistance  
**Sleeve 2 & 3**: Bollinger Bands, RSI, MACD  
**All Sleeves**: Volatility (ATR, Bollinger Band Width)

**Confirmation Standard**:
- Multiple indicators should align (not rely on single indicator)
- Avoid indicator divergence (conflicting signals)
- Price action takes priority over indicators

### Tertiary: Narrative Strength

- Market sentiment (bull/bear/consolidation phases)
- Macroeconomic drivers (Fed policy, economic data)
- On-chain metrics (whale accumulation, exchange flows)
- Future releases (option expiration dates, funding events)

**Usage**: Secondary confirmation only; never primary trigger.

---

## 7. Instruments & Trading Mechanics

### Primary Instruments

**Crypto Perpetual Futures** (via Binance, Bybit, Deribit, etc.):
- High liquidity
- Fast execution
- Leverage available (start 2–3x, max 5x)
- Tight spreads

**Instruments to Trade**:
- Major pairs: BTC/USDT, ETH/USDT
- Alt-season pairs: SOL, AVAX, ARB, OP, DOGE (liquid alts)
- Stablecoin pairs: USDC/USDT spread plays (lower vol)

### Position Management

**Entry**:
- Market order if high urgency (strong signal, limited time window)
- Limit order if time permits (save slippage)
- Scale-in for Sleeve 2 (3 tranches) to reduce entry risk

**Exit**:
- Predefined stop-loss (no discretion)
- Profit target 1 (partial exit, move stop to breakeven)
- Profit target 2 (larger exit, trailing stop or time-based)
- Manual close only if technical invalidation or emergency

**Leverage**:
- Conservative: 2–3x (start here)
- Normal: 3–4x (after 4 weeks of stable performance)
- Aggressive: 4–5x (only during optimal regime, rare)

### Slippage & Commission Budget

- Assumed slippage: 0.05–0.1% per trade
- Exchange commission: 0.02–0.04% per trade (maker/taker)
- Total cost per trade: 0.1–0.15%
- Minimum edge must exceed this cost

---

## 8. System-Level Risk Management

### Capital Allocation

- **Starting Capital**: TBD by trader
- **Per-sleeve allocation**: Dynamic (see Section 5)
- **Cash Reserve**: Always maintain 5–10% uninvested (liquidity buffer)
- **Emergency Capital**: 5% set aside for margin/maintenance (if using leverage)

### Position Sizing Formula

```
Position Size = (Account Size × Risk % × Drawdown Factor × Vol Factor) / Stop Loss $
```

Where:
- **Account Size**: Current equity
- **Risk %**: 0.5–1.2% depending on sleeve and setup
- **Drawdown Factor**: From portfolio DD level (Section 5)
- **Vol Factor**: From market volatility (Section 5)
- **Stop Loss $**: Exit price − Entry price in $ terms

### Drawdown Management

**Defined Thresholds**:
- Warning: 10% DD → reduce sizing by 30%
- Defensive: 15% DD → reduce sizing by 50%
- Emergency: 20% DD → pause all new trades
- Liquidation: 25% DD → close 50% of open positions

**Recovery Rules**:
- Must reach 0% DD (or near peak equity) before aggressive trading resumes
- Gradual increase over 5 trading days
- Sleeve 1 resume first (most stable), then Sleeves 2 & 3

### Max Loss Rules

- **Per trade**: 1% max loss (stop at 1% below entry + slippage)
- **Per day**: 2% max loss (stop trading after 2 losing days)
- **Per week**: 3.5% max loss (mandatory review after exceeding)
- **Per month**: 8% max loss (performance review + strategy adjustment)

### Emergency Controls

**Kill Switch Triggers**:
1. Margin level below 5x (if using leverage)
2. Portfolio DD exceeds 25%
3. 4 consecutive losing trades
5. Manual override by trader (emergency market conditions)

**Action**: Close all positions, pause system, manual assessment.

---

## 9. Success Metrics for v1

### Financial Targets (3-Month Horizon)

| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| **Monthly Return** | 3–5% | 1% (prove system works) |
| **Sharpe Ratio** | > 1.0 | > 0.5 |
| **Win Rate** | > 52% | > 50% |
| **Profit Factor** | > 1.5 | > 1.2 (total wins / total losses) |
| **Max Drawdown** | < 15% | < 20% |
| **Avg Trade Hold** | 4–5 days | < 14 days |
| **Avg Win / Avg Loss** | > 1.8x | > 1.5x |

### Operational Targets

| Metric | Target |
|--------|--------|
| **Trades per month** | 15–25 (quality, not quantity) |
| **Avg position size** | 2–3% of account |
| **System uptime** | > 99% |
| **Execution latency** | < 100ms (from signal to filled) |

### Data Collection & Learning

- Keep detailed trade log: entry/exit, signal source, reason for exit, $P&L
- Weekly performance review: Which sleeve is performing? Why?
- Monthly strategy review: Adjust thresholds based on data
- Live results after 8–12 weeks should inform v1.5 improvements

---

## 10. Implementation Roadmap

### Phase 1: Core System (Weeks 1–2)
- ✅ RiskManager + PositionSizer + DrawdownManager (base classes)
- ✅ TradeQualityGate + PlayBudget (prevent over-trading)
- [ ] Sleeve 1 entry/exit logic implemented
- [ ] Basic backtesting harness

### Phase 2: Sleeve Implementation (Weeks 3–4)
- [ ] Sleeve 1 (X-Signal Momentum) backtest & paper trade
- [ ] Sleeve 2 (Trend Following) backtest & paper trade
- [ ] Sleeve 3 (Mean Reversion) backtest & paper trade
- [ ] Dynamic allocation framework

### Phase 3: Integration & Testing (Weeks 5–6)
- [ ] All 3 sleeves running together
- [ ] Dynamic allocation active
- [ ] Paper trading for 2–3 weeks
- [ ] Performance review & adjustments

### Phase 4: Go Live (Week 7+)
- [ ] Small live account ($1k–$5k start)
- [ ] Daily monitoring & trade journaling
- [ ] Weekly performance reviews
- [ ] Scale capital after 4 weeks of consistent profitability

---

## 11. Open Questions & Future Iterations

### For v1 (Immediate)
- How to best score X signals programmatically? (Manual for now, ML later)
- Should leverage be fixed or dynamic? (Start fixed at 3x)
- How often to rebalance allocation? (Every 2 weeks, may change)
- What's the optimal play budget distribution? (Adjust after 4 weeks of live data)

### For v1.5 (Next Iteration)
- Add 4th sleeve? (E.g., volatility or options strategies)
- Implement machine learning signal scoring
- Add on-chain data feeds (whale tracking, exchange flows)
- Portfolio-level correlation hedging

### For v2 (Future)
- Sleeve-specific performance attribution (what drives each sleeve's returns?)
- Leverage optimization (dynamic 2–5x based on regime)
- Options integration (defined-risk setups)
- Multi-exchange arbitrage

---

## Appendix A: Terminology

- **Sleeve**: Independent strategy running within the system
- **Edge**: Measurable positive expectancy (avg win − avg loss > 0)
- **Drawdown (DD)**: Current loss from peak equity
- **Signal Strength**: Confidence level in trade opportunity (0–100%)
- **R:R Ratio**: Risk/Reward ratio (1:2 means risking $1 to make $2)
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)

---

## Appendix B: Example Trade Journal Entry

```
Date:           2026-07-05
Entry Time:     14:32 UTC
Symbol:         BTC/USDT

SIGNAL INFO:
Source:         X (@KnownTrader), Technical Setup
Signal Strength: 78%
R:R Ratio:      1:2.5
Edge Estimate:  0.8%

ENTRY:
Price:          $64,500 (limit order filled)
Position Size:  3% of account
Leverage:       3x
Stop Loss:      $62,800 (1.7% below entry)
Target 1:       $66,500 (exit 50%)
Target 2:       $68,200 (exit 50%, trailing stop)

EXIT:
Time:           2026-07-06 09:15 UTC
Exit Price:     $66,480
Hold Time:      18.7 hours
P&L:            +$2,980 (+1.6% on account)

NOTES:
- Clean break above resistance, confirmed by volume
- X signal spotted at 14:15 UTC, 17 min before entry
- Took target 1 at $66,500, held second half to $66,480
- No technical invalidation, exited due to 2-day time target
```

---

**Version History**:
- v1.0 (2026-07-05): Initial draft
- v1.1 (2026-07-05): Added quality gates, dynamic allocation rules, trade examples
