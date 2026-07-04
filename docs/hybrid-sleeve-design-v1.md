# Hybrid Sleeve Design v1

**Status**: v1 (Draft)  
**Date**: July 2026  
**Goal**: Build a scalable trading system using Freqtrade with multiple sleeves and dynamic risk allocation.

## 1. Overview & Philosophy

This document defines the initial architecture for a **Hybrid Sleeve** trading system. The core idea is to run multiple strategies (sleeves) with different characteristics, while dynamically allocating risk between them.

### Guiding Principles
- Quality over quantity of trades
- Dynamic risk allocation (not fixed percentages)
- Strong focus on high-quality signals from X
- Start simple → iterate based on real performance
- Focus on accessible instruments (Crypto Perps + Tokenized Assets)
- Day-to-week timeframe initially

## 2. Sleeve Structure (v1)

We will start with **3 sleeves**:

| Sleeve | Name                    | Style                    | Timeframe     | Primary Edge Source       | Initial Risk Budget | Purpose |
|--------|-------------------------|--------------------------|---------------|---------------------------|---------------------|--------|
| 1      | X-Signal Momentum       | High-conviction Swing    | 1–7 days      | Strong signals from X     | 45–55%              | Fast capital growth using high-quality X signals |
| 2      | Trend Following         | Trend Continuation       | 3–21 days     | Technical + Narrative     | 25–35%              | More stable returns by riding strong trends |
| 3      | Tactical Mean Reversion | Short-term Reversion     | Hours – 4 days| Overextended moves + X    | 15–25%              | Smaller but frequent opportunities |

### Notes
- Sleeve 1 will be the most aggressive and signal-heavy.
- Sleeve 2 provides stability.
- Sleeve 3 acts as a tactical buffer.
- Risk allocation will be **dynamic** based on recent performance and market conditions.

## 3. Dynamic Risk Allocation (v1)

Instead of fixed allocation, risk will be adjusted based on:

- Recent performance of each sleeve (last 7–14 days)
- Overall portfolio drawdown level
- Market regime (trending vs choppy)

**Initial Rules**:
- No single sleeve should exceed **60%** of total risk at any time.
- If one sleeve performs exceptionally well, it can temporarily receive higher allocation.
- During portfolio drawdown, overall risk across all sleeves will be reduced.

This logic will be implemented gradually and refined with live data.

## 4. Signal Sources

**Primary**: X (Twitter) — High-quality, high-conviction signals  
**Secondary**: Technical indicators + narrative strength  
**Future**: On-chain data, options flow, etc.

Sleeve 1 will rely most heavily on X signals.

## 5. Instruments

- **Primary**: Crypto Perpetual Futures (high liquidity + leverage)
- **Secondary**: Tokenized stocks/assets
- **Exploratory**: Options (defined risk setups)

Focus will be on instruments that allow fast entry/exit and good liquidity.

## 6. Risk Management (System Level)

- Per-sleeve risk limits
- Overall portfolio max drawdown rules
- Position sizing based on volatility and edge
- Emergency pause / kill switch logic
- Clear rules for reducing risk during losing streaks

Detailed risk rules will be documented separately.

## 7. Success Metrics for v1

- Positive expectancy across the system after 8–12 weeks of live trading
- Controlled drawdowns (target < 15–20%)
- Clear data on which sleeves perform well
- Reasonable operational load

## 8. Open Questions

- How to best extract and score high-quality signals from X?
- Should we add a 4th sleeve later (e.g. Options or Volatility)?
- How sophisticated should dynamic allocation logic become in v1 vs v2?
