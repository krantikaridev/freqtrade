# MVP definition (Sept 2026)

## Bar
Ship a Freqtrade dry-run on Oracle Always Free that can produce **better-than-flat** results versus NanoClaw’s ~0 PnL baseline.

## In scope now
- One sleeve: Trend Following
- Binance USDT-M: BTC, ETH, SOL, BNB
- Dry-run only
- Docker-based ops on Oracle Always Free

## Out of scope now
- Live orders
- X-signal ingestion
- Full hybrid allocation across 3 sleeves
- NanoClaw development

## Exit criteria to consider tiny live
- Multi-week dry-run log with positive expectancy and controlled drawdown
- Documented backtest (same strategy/config) that is not catastrophically curve-fit
- Explicit human go-ahead
