# Hybrid Sleeve Design v1

**Status**: Draft v1  
**Date**: July 2026  
**Goal**: Build a scalable, income-oriented trading system using Freqtrade with multiple sleeves and dynamic risk allocation.

## 1. Overview

This document defines the initial **Hybrid Sleeve Architecture** for the freqtrade system. The goal is to create a system that can multiply capital reasonably fast while maintaining control and adaptability.

We will start simple, test in real conditions, and iterate.

### Core Principles
- Quality and risk management over aggressive returns
- Dynamic allocation between sleeves
- Leverage strong signals from X (Twitter)
- Focus on accessible instruments (Crypto Perps + Tokenized Assets)
- Start with day-to-week timeframe
- Build → Measure → Improve

## 2. Sleeve Structure (v1)

We will start with **3 sleeves**:

| Sleeve | Name                    | Style                    | Timeframe     | Primary Edge          | Target Risk Share | Description |
|--------|-------------------------|--------------------------|---------------|-----------------------|-------------------|-----------|
| 1      | X-Signal Momentum       | High-conviction Swing    | 1–7 days      | Strong X signals      | 40–60%            | Fastest capital growth using high-quality signals from X |
| 2      | Trend Following         | Trend Continuation       | 3–21 days     | Technical + Narrative | 25–35%            | More stable returns by riding strong trends |
| 3      | Tactical / Mean Reversion | Short-term Reversion   | Hours – 3 days| Overextended moves    | 15–25%            | Smaller, more frequent opportunities |

### Notes on Sleeves
- Sleeve 1 will be the most aggressive and signal-driven.
- Sleeve 2 provides more stability.
- Sleeve 3 acts as a tactical buffer.
- Risk allocation between sleeves will be **dynamic** (not fixed percentages).

## 3. Dynamic Risk Allocation (Initial Approach)

Instead of fixed allocation, we will adjust capital across sleeves based on:

- Recent performance of each sleeve (last 7–14 days)
- Current market regime (trending vs ranging)
- Overall portfolio drawdown level

**Initial Rules (v1)**:
- No sleeve should exceed 60% of total risk capital at any time.
- If one sleeve is performing very well, it can temporarily receive more allocation.
- If overall portfolio is in drawdown, reduce risk across all sleeves.

This logic will be refined after we have real performance data.

## 4. Signal Sources

### Primary Signal Source: X (Twitter)
- Strong focus on extracting high-quality signals from X.
- We will build or integrate tools to monitor and score signals from X.
- Only high-conviction signals will be used (especially in Sleeve 1).

### Secondary Sources
- Technical analysis
- On-chain data (where relevant)
- Narrative strength

## 5. Instruments

To maximize accessibility and speed:

- **Primary**: Crypto Perpetual Futures (high liquidity + leverage)
- **Secondary**: Tokenized Stocks / Assets (easier legal access than traditional US stocks)
- **Exploratory**: Options (where defined risk and edge exist)

Focus will be on instruments that allow fast position building and exiting.

## 6. Risk Management (System Level)

- Overall portfolio risk limits
- Per-sleeve risk limits
- Max drawdown thresholds
- Position sizing rules
- Kill switches / emergency pause logic

Detailed risk rules will be defined in a separate document.

## 7. Success Metrics for v1

We will consider v1 successful if we achieve:

- Positive expectancy across the system over 2–3 months of live trading
- Controlled drawdowns (target: under 15–20%)
- Clear understanding of which sleeves work and which need improvement
- Reasonable operational effort

## 8. Open Questions & Future Improvements

- How to best extract and score signals from X?
- Should we add a 4th sleeve later (e.g., Options or Volatility)?
- How sophisticated should dynamic allocation become?
- Integration with on-chain execution (possible future link with Nanoclaw ideas)?

---

**Next Actions**
- Finalize this design after review
- Start building supporting components in Freqtrade
- Define detailed rules for each sleeve
