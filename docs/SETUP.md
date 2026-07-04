# Hybrid Sleeve Trading System - Setup Guide

## Overview

This is the foundation for a **Hybrid Sleeve trading system** on Freqtrade. It implements a modular, multi-strategy architecture with dynamic risk allocation.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment tool (venv or conda)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/krantikaridev/freqtrade.git
cd freqtrade
```

### 2. Create and Activate Virtual Environment

**Using venv:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Using conda:**

```bash
conda create -n hybrid-sleeve python=3.10
conda activate hybrid-sleeve
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
cp config/.env.example .env
```

Edit `.env` with your settings:

```env
ENVIRONMENT=dev
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
INITIAL_BALANCE=1000
MAX_PORTFOLIO_DRAWDOWN=0.20
LOG_LEVEL=INFO
```

**⚠️ IMPORTANT:** Never commit `.env` to version control. It's in `.gitignore` for security.

### 5. Verify Installation

```bash
python main.py
```

You should see:

```
============================================================
HYBRID SLEEVE SYSTEM STATUS
============================================================
Status: RUNNING
Portfolio Balance: $1000.00
Total Trades: 0
Open Positions: 0

SLEEVE DETAILS:

  x_signal_momentum:
    Enabled: True
    Allocation: 50.0%
    ...
```

## Project Structure

```
freqtrade/
├── config/                          # Configuration files
│   ├── config.base.yaml            # Base config template
│   ├── config.dev.yaml             # Development overrides
│   ├── config.staging.yaml         # Staging overrides
│   ├── config.prod.yaml            # Production overrides
│   └── .env.example                # Environment variables template
├── sleeves/                        # Main package
│   ├── __init__.py                 # Package init
│   ├── base_sleeve.py              # Abstract base class
│   ├── system_manager.py           # Main orchestrator
│   ├── risk_management/            # Risk management module
│   │   ├── __init__.py
│   │   └── risk_manager.py         # RiskManager & DynamicAllocationManager
│   ├── implementations/            # Sleeve implementations
│   │   ├── __init__.py
│   │   ├── x_signal_momentum.py    # Sleeve 1
│   │   ├── trend_following.py      # Sleeve 2
│   │   └── tactical_mean_reversion.py  # Sleeve 3
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── monitoring.py           # Logging & health monitoring
│       └── config.py               # Configuration utilities
├── main.py                         # Entry point
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── docs/
│   ├── hybrid-sleeve-design-v1.md # Design document
│   ├── SETUP.md                    # This file
│   ├── ARCHITECTURE.md             # Architecture details
│   └── SLEEVES.md                  # Sleeve documentation
└── README.md                       # Main readme
```

## Running the System

### Development Mode

```bash
# Activate venv
source venv/bin/activate

# Ensure .env is configured
cat .env

# Run the system
python main.py
```

### With Specific Environment

```bash
# Set environment before running
export ENVIRONMENT=dev
python main.py
```

### Stopping the System

Press `Ctrl+C` to gracefully stop the system.

## Configuration

### Environment-Specific Configs

1. **Development (`dev`)**
   - Dry run enabled (no real trades)
   - Verbose logging (DEBUG level)
   - Small stake amounts for testing
   - API server on localhost:8080

2. **Staging (`staging`)**
   - Dry run enabled
   - Normal logging (INFO level)
   - Realistic stake amounts
   - API server accessible

3. **Production (`prod`)**
   - Live trading enabled
   - Normal logging (INFO level)
   - API server disabled for security
   - Max open trades restricted

### Risk Parameters

Edit risk configs in `main.py` → `create_risk_configs()`:

```python
RiskConfig(
    sleeve_id="x_signal_momentum",
    min_allocation=0.45,           # Minimum % allocation
    max_allocation=0.55,           # Maximum % allocation
    max_position_size=0.10,        # Max size per position (% of account)
    max_open_positions=5,          # Max concurrent positions
    stop_loss_pct=0.05,           # Default stop loss
    risk_per_trade=0.02            # Risk per trade (% of account)
)
```

## Understanding the System

### The Three Sleeves

#### Sleeve 1: X-Signal Momentum (45-55% allocation)
- **Style**: High-conviction swing trading
- **Timeframe**: 1-7 days
- **Edge**: Strong signals from X (Twitter)
- **Focus**: Fast capital growth using quality signals

#### Sleeve 2: Trend Following (25-35% allocation)
- **Style**: Trend continuation
- **Timeframe**: 3-21 days
- **Edge**: Technical + narrative strength
- **Focus**: Stable returns by riding strong trends

#### Sleeve 3: Tactical Mean Reversion (15-25% allocation)
- **Style**: Short-term reversion
- **Timeframe**: Hours - 4 days
- **Edge**: Overextended moves + X signals
- **Focus**: Smaller but frequent opportunities

### Risk Management

The system implements:

- **Per-sleeve limits**: Each sleeve has min/max allocation
- **Position sizing**: Based on account risk and volatility
- **Drawdown control**: Portfolio max drawdown limits
- **Dynamic allocation**: Adjusts based on performance and market conditions
- **Emergency controls**: Pause/resume functionality

### Dynamic Allocation

Allocations are adjusted based on:

1. **Recent performance** (7-14 days)
2. **Market regime** (trending vs. choppy)
3. **Portfolio drawdown** (reduce risk during losses)

**Rule**: No single sleeve exceeds 60% allocation at any time.

## Development Workflow

### Adding a New Feature

1. Create a feature branch:
   ```bash
   git checkout -b feat/new-feature
   ```

2. Implement changes

3. Test locally:
   ```bash
   python main.py
   ```

4. Commit with clear messages:
   ```bash
   git commit -m "feat: Add new feature description"
   ```

5. Create a pull request

### Implementing a Sleeve Optimization

1. Extend `BaseSleeve` in `sleeves/implementations/`
2. Implement `analyze()` with your logic
3. Register in `create_risk_configs()`
4. Test with `python main.py`

### Testing

Run tests (when test suite is added):

```bash
pytest tests/
```

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'sleeves'
```

**Solution**: Ensure you're in the project root directory and have activated the virtual environment.

### Configuration Errors

```
FileNotFoundError: Config file not found: config/config.dev.yaml
```

**Solution**: Create the missing config file or ensure `ENVIRONMENT` is set correctly.

### Missing Dependencies

```
ModuleNotFoundError: No module named 'pythonjsonlogger'
```

**Solution**: Reinstall requirements:

```bash
pip install -r requirements.txt
```

## Next Steps

1. **Implement sleeve analysis logic**
   - Integrate X signal scoring
   - Add technical indicators
   - Implement mean reversion detection

2. **Add backtesting support**
   - Integrate with Freqtrade backtester
   - Performance metrics tracking

3. **Add monitoring & alerting**
   - Telegram notifications
   - Performance dashboards
   - Health check alerts

4. **Implement live trading**
   - Exchange API integration
   - Order management
   - Position tracking

## Support & Resources

- **Design Document**: [docs/hybrid-sleeve-design-v1.md](../docs/hybrid-sleeve-design-v1.md)
- **Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Sleeves Details**: [docs/SLEEVES.md](../docs/SLEEVES.md)
- **Freqtrade Docs**: https://www.freqtrade.io/en/latest/

## License

MIT License - See LICENSE file for details
