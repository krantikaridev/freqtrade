# Hybrid Sleeve System Architecture

## Overview

The Hybrid Sleeve system is a modular, multi-strategy trading framework designed for scalability and maintainability. It orchestrates three independent trading sleeves with unified risk management and dynamic allocation.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 HybridSleeveSystem (Main Orchestrator)      │
│                                                             │
│  • Coordinates all sleeves                                │
│  • Manages signal processing                              │
│  • Orchestrates trade execution                           │
│  • Monitors system health                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Sleeve 1    │ │  Sleeve 2    │ │  Sleeve 3    │
│   (X-Sig)    │ │  (Trend)     │ │  (RevMean)   │
│              │ │              │ │              │
│ • Analyze    │ │ • Analyze    │ │ • Analyze    │
│ • Generate   │ │ • Generate   │ │ • Generate   │
│   Signals    │ │   Signals    │ │   Signals    │
│ • Track      │ │ • Track      │ │ • Track      │
│   Perf       │ │   Perf       │ │   Perf       │
└──────────────┘ └──────────────┘ └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────────────────────────────────────┐
│        Risk Management Layer                 │
│                                              │
│  • RiskManager (per-sleeve limits)          │
│  • DynamicAllocationManager                 │
│  • Position sizing                          │
│  • Drawdown control                         │
└──────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────┐
│        Monitoring & Logging                 │
│                                              │
│  • HealthMonitor                           │
│  • Structured JSON logging                 │
│  • Performance tracking                    │
└──────────────────────────────────────────────┘
```

## Core Components

### 1. HybridSleeveSystem

**Location**: `sleeves/system_manager.py`

**Responsibilities**:
- Initialize all sleeves
- Manage system lifecycle (start, stop, pause, resume)
- Process signals from all sleeves
- Execute trades with risk validation
- Monitor and report system health
- Adjust allocations dynamically

**Key Methods**:
```python
start()                    # Start the trading system
stop()                     # Stop gracefully
process_signals(data)      # Process signals from all sleeves
execute_trade(signal)      # Execute trade with risk validation
update_allocations(dd)     # Adjust allocations dynamically
get_system_status()        # Get comprehensive status
```

### 2. BaseSleeve (Abstract)

**Location**: `sleeves/base_sleeve.py`

**Responsibilities**:
- Define the interface for all sleeves
- Manage sleeve-specific state
- Track performance metrics
- Respond to allocation changes

**Key Methods** (to be implemented):
```python
analyze(market_data)       # Generate trading signals
on_trade_executed(info)    # Called when trade executes
on_trade_closed(result)    # Called when trade closes
```

### 3. Sleeve Implementations

**Location**: `sleeves/implementations/`

Each sleeve extends `BaseSleeve`:

#### Sleeve 1: XSignalMomentumSleeve
- High-conviction swing trading from X signals
- 45-55% initial allocation
- Aggressive position sizing

#### Sleeve 2: TrendFollowingSleeve
- Trend continuation with technical confirmation
- 25-35% initial allocation
- Moderate position sizing

#### Sleeve 3: TacticalMeanReversionSleeve
- Mean reversion on overextended moves
- 15-25% initial allocation
- Conservative position sizing

### 4. Risk Management

**Location**: `sleeves/risk_management/risk_manager.py`

**Components**:

#### RiskManager
- Enforces per-sleeve position limits
- Calculates risk per trade
- Monitors portfolio drawdown
- Validates trades before execution

**Key Methods**:
```python
register_sleeve(config)    # Register sleeve with limits
validate_trade(sleeve, size, balance)  # Pre-trade validation
calculate_risk_per_trade() # Calculate position size
should_pause_trading()     # Emergency stop check
```

#### DynamicAllocationManager
- Manages risk allocation across sleeves
- Enforces 60% max per sleeve rule
- Validates allocation sums to 100%

**Key Methods**:
```python
set_allocation(sleeve_id, pct)   # Set sleeve allocation
get_allocation(sleeve_id)        # Get sleeve allocation
validate_allocations()           # Validate total
```

### 5. Monitoring & Logging

**Location**: `sleeves/utils/monitoring.py`

**Components**:

#### HealthMonitor
- Tracks system health checks
- Logs trade execution events
- Reports overall system health

#### Logging
- Structured JSON logging
- File and console handlers
- Configurable log levels

### 6. Configuration

**Location**: `sleeves/utils/config.py`

**Functions**:
- Load environment variables from `.env`
- Load YAML config files
- Interpolate environment variables
- Support for dev/staging/prod environments

## Data Flow

### Trade Execution Flow

```
1. Market Data Available
        ↓
2. System.process_signals(market_data)
        ↓
3. For each active sleeve:
        ↓
   3a. Sleeve.analyze(market_data) → SleeveSignal
        ↓
   3b. Return signal or None
        ↓
4. System.execute_trade(signal) for each signal
        ↓
5. Risk Validation
   - RiskManager.validate_trade()
   - Check position size limits
   - Check open positions limit
        ↓
6. If valid: Execute Trade
   - Sleeve.on_trade_executed(trade_info)
   - Log execution
   - Add to active positions
        ↓
7. Return to step 1
```

### Allocation Update Flow

```
1. Monitor Portfolio Performance
        ↓
2. Calculate Performance Metrics (per-sleeve, 7-14 days)
        ↓
3. Check Current Drawdown
        ↓
4. If drawdown > threshold:
   - Reduce overall risk
   - Redistribute allocations
        ↓
5. DynamicAllocationManager.update_allocations()
        ↓
6. For each sleeve:
   - Sleeve.update_allocation(new_pct)
        ↓
7. Validate new allocations
        ↓
8. Continue trading with updated allocations
```

## Configuration System

### Config Loading Priority (highest to lowest):

1. Environment variables (`.env` file)
2. Environment-specific YAML (`config.{env}.yaml`)
3. Base YAML (`config.base.yaml`)
4. System defaults

### Config Files

```yaml
# config.base.yaml - Base template
exchange:
  name: "binance"
  key: "${EXCHANGE_API_KEY}"  # Interpolated from env
  secret: "${EXCHANGE_API_SECRET}"
max_open_trades: 10

# config.dev.yaml - Development overrides
dry_run: true
log_level: "DEBUG"

# config.prod.yaml - Production overrides
dry_run: false
log_level: "INFO"
trader_enabled: true
```

## Risk Management Rules

### Per-Sleeve Limits

Each sleeve has:
- Min/max allocation percentage
- Max position size (% of account)
- Max open positions
- Default stop loss %
- Risk per trade %

### Portfolio Rules

- **Max drawdown**: Portfolio stops trading if drawdown ≥ limit (default 20%)
- **Risk reduction**: Reduce allocations if drawdown > 75% of limit
- **Max single sleeve**: No sleeve exceeds 60% allocation

### Trade Validation

Before execution, each trade is validated for:
- Position size ≤ sleeve max
- Open positions < sleeve max
- Risk per trade ≤ sleeve limit
- Risk manager approval

## Extensibility

### Adding a New Sleeve

1. Create new class extending `BaseSleeve`:
   ```python
   class MyNewSleeve(BaseSleeve):
       def analyze(self, market_data):
           # Your logic
       def on_trade_executed(self, trade_info):
           # Track execution
       def on_trade_closed(self, trade_result):
           # Update performance
   ```

2. Create risk config in `main.py`:
   ```python
   RiskConfig(
       sleeve_id="my_new_sleeve",
       min_allocation=0.10,
       max_allocation=0.20,
       ...
   )
   ```

3. Register in `main.py`:
   ```python
   sleeves["my_new_sleeve"] = MyNewSleeve(config)
   system.register_sleeve(sleeves["my_new_sleeve"], risk_config)
   ```

### Adding New Risk Rules

1. Extend `RiskManager` class
2. Add validation method
3. Call from `HybridSleeveSystem.execute_trade()`

### Integrating with Freqtrade

The system is designed to work alongside Freqtrade:

1. **Signals from Freqtrade strategies**: Feed market data to sleeves
2. **Trade execution via Freqtrade**: Use Freqtrade's trade engine
3. **Performance tracking**: Collect from Freqtrade trades
4. **Configuration**: Use Freqtrade's config system

## Performance Considerations

- **Modular design**: Sleeves can be swapped without affecting others
- **Async-ready**: Structure supports async market data fetching
- **Memory efficient**: Sleeves maintain minimal state
- **Scalable**: Easy to add more sleeves

## Monitoring & Observability

### Logging

- Structured JSON logging for easy parsing
- Separate file and console handlers
- Configurable log levels per environment

### Metrics Tracked

Per sleeve:
- Trades executed
- Win rate
- Cumulative P&L
- Drawdown
- Sharpe ratio (when implemented)

System-wide:
- Total balance
- Open positions
- System health status
- Allocations

## Future Enhancements

1. **Advanced Risk**: Machine learning-based dynamic allocation
2. **Multi-exchange**: Support multiple exchanges simultaneously
3. **Real-time alerts**: Telegram/Discord notifications
4. **Performance dashboards**: Real-time web UI
5. **Backtesting framework**: Full historical simulation
6. **ML optimization**: Auto-tune parameters based on performance
