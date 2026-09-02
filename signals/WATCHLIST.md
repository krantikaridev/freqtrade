# Signal watchlist (v1.2)

Primary tracker: **[Quantral](https://quantral.com/leaderboard)** — Serenity (@aleabitoreddit) #2 lifetime; @citrini #1.
Secondary: SignalSnitch, TraderBro, ShadowAlpha, etc. (see `watchlist.json`).

Primary X: **@i36do** (mmmiitr). Research-only on Serenity — not auto-trade. Krantikari X ignored.

## Core feeds
| Source | Notes |
| --- | --- |
| Quantral top | citrini, aleabitoreddit, jukan05, crux_capital_, michaelsikand, … |
| @i36do feed slice | TechCharts, mind1nvestor, anandragn, VJNCapital, NoLimitGains, Nostre_damus, TFMetals, GavMcCracken, Polymarket |
| Bookmark ideas | 8/21 EMA A/B · TraderDev mining · TV MCP later · sell-puts later · BTC cycle regime |
| Grok Tasks (email) | Gold + crypto when Tasks actually email |

## Flow
1. Ingest deltas only (reuse bookmark cache)
2. Bucket → promote testable ideas into Freqtrade dry-run backlog
3. Weekday 8:00 IST digest; quiet if nothing new

See also: `STUCK.md`, `watchlist.json`
