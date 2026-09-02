# Tasks - freqtrade

## Done (MVP scaffold)
- [x] Lock product decisions (Oracle, dry-run, Binance USDT-M, Sleeve 2, BTC/ETH/SOL/BNB)
- [x] Add `config/config.dryrun.json`
- [x] Implement `strategies/TrendFollowing.py`
- [x] Add `docker-compose.yml` + `.env.example`
- [x] Refresh README for dry-run ops

## Current high priority
- [ ] Deploy dry-run on Oracle Always Free VM
- [ ] Download history + run first backtest; record results honestly
- [ ] Let dry-run soak; compare session PnL vs NanoClaw ~0 baseline
- [ ] Only then: tiny live capital discussion

## Later
- [ ] Sleeve 1 X-Signal Momentum (needs X bookmark / signal pipeline)
- [ ] Sleeve 3 Mean Reversion
- [ ] Dynamic risk allocation across sleeves
- [ ] Monitoring / alerting on the VM

## Notes
- Follow `.github/copilot-instructions.md`
- Never commit API secrets
