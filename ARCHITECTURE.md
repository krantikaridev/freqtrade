# System Manager Foundation Architecture

**Date**: July 2026  
**Version**: 0.1.0  
**Status**: Foundation Complete - Ready for Sleeve Implementation

## Overview

This document describes the core foundation of the Hybrid Sleeve trading system, focusing on the **System Manager** and **Risk Management** architecture.

## Directory Structure

```
src/
├── __init__.py           # Package exports
├── main.py               # Entry point and demo
├── system/
│   ├── __init__.py
│   ├── manager.py        # SystemManager - central orchestration
│   └── config.py         # ConfigLoader - configuration management
└── risk/
    ├── __init__.py
    ├── base.py           # Abstract base classes and interfaces
    └── simple.py         # Simple/default implementations

config/
└── system_config.json    # System configuration

docs/
└── hybrid-sleeve-design-v1.md  # High-level design
```

## Core Components

### 1. SystemManager (`src/system/manager.py`)

**Purpose**: Central orchestration point for the entire trading system.

**Key Responsibilities**:
- System initialization and startup
- Configuration loading and validation
- Risk management component setup
- Equity tracking and state updates
- Future: Sleeve coordination and dynamic allocation

**API**:
```python
manager = SystemManager(mode=TradingMode.BACKTESTING, config_path=Path("config/system_config.json"))

# Initialization
await manager.initialize()  # Load config, init risk management
manager.start()             # Start trading
manager.stop()              # Stop trading

# State queries
manager.get_status()        # Get system status
manager.get_risk_manager()  # Access risk manager
manager.update_equity(100000, 100000)  # Update current equity

# Sleeve coordination (placeholders for future)
manager.get_sleeve_allocation()       # Get current allocations
manager.get_dynamic_allocation()      # Get dynamic adjustments
manager.update_sleeve_performance(...)# Record sleeve performance
```

**Initialization Flow**:
```
1. Create SystemManager
   ↓
2. Load Configuration
   ├─ ConfigLoader reads config file or uses defaults
   ├─ Apply programmatic overrides (if provided)
   └─ Validate required fields
   ↓
3. Initialize Risk Management
   ├─ Create RiskManager instance
   ├─ Load risk parameters from config
   └─ Set up position sizing, drawdown control
   ↓
4. System Ready
   ├─ _initialized = True
   ├─ Ready for sleeve setup (future)
   └─ Ready for trading
```

### 2. ConfigLoader (`src/system/config.py`)

**Purpose**: Clean configuration management with dot-notation access.

**Features**:
- Load from JSON config files
- Fallback to sensible defaults
- Dot-notation config access (`config.get("risk.max_drawdown")`)
- Configuration validation
- Environment awareness (backtesting vs live)

**Usage**:
```python
loader = ConfigLoader(Path("config/system_config.json"))
config = loader.load()

max_drawdown = loader.get("risk.max_portfolio_drawdown", default=0.20)
```

### 3. Risk Management Architecture

Risk management uses **abstract base classes** to define interfaces, with **simple implementations** for v0.1.

#### Base Classes (`src/risk/base.py`)

Three abstract base classes define the interface for extensibility:

**RiskManager**: Overall system risk control
- `check_position_allowed(symbol, size)` - Gate new positions
- `get_max_risk_amount()` - Calculate risk budget
- `update_state(equity, peak)` - Update with current portfolio state

**PositionSizer**: Calculate position sizes
- `calculate_size(params)` - Compute position size based on risk
- `adjust_for_volatility(base_size, volatility)` - Scale for market conditions

**DrawdownManager**: Control drawdown and recovery
- `get_drawdown_state(equity, peak)` - Calculate current drawdown
- `get_risk_reduction_factor(drawdown_pct)` - Scale risk inversely with drawdown
- `is_emergency_exit_triggered(drawdown_pct)` - Emergency stop logic

#### Simple Implementations (`src/risk/simple.py`)

Provides working implementations suitable for v0.1:

**SimpleRiskManager**:
- Tracks concurrent positions (max_concurrent_positions)
- Enforces risk budget exhaustion
- Foundation for per-sleeve limits (future)

**SimplePositionSizer**:
- Risk-based sizing: `size = (account * risk_pct) / stop_loss_pct`
- Volatility adjustment (inverse scaling)
- Max position constraints

**SimpleDrawdownManager**:
- Linear drawdown tracking
- Proportional risk reduction (warning threshold → max drawdown)
- Emergency exit trigger

### 4. Configuration File (`config/system_config.json`)

Contains all runtime parameters:
- **mode**: backtesting | live | paper
- **risk**: Risk parameters (max_drawdown, position_size_pct, etc.)
- **sleeves**: Sleeve count and default allocations
- **trading**: Instruments, timeframes, mode flags

## Initialization Example

```python
import asyncio
from pathlib import Path
from src.system.manager import SystemManager
from src.risk.base import TradingMode

async def main():
    manager = SystemManager(
        mode=TradingMode.BACKTESTING,
        config_path=Path("config/system_config.json")
    )
    
    # Initialize
    if await manager.initialize():
        # Start trading
        manager.start()
        
        # Update equity periodically
        manager.update_equity(current_equity=100000, peak_equity=100000)
        
        # Get status
        status = manager.get_status()
        print(status)
        
        # Stop
        manager.stop()
    else:
        print("Initialization failed")

asyncio.run(main())
```

## Key Design Decisions

### 1. Abstract Interfaces First
Risk management is defined via abstract base classes (`RiskManager`, `PositionSizer`, `DrawdownManager`) before implementation. This allows:
- Easy extension for specialized sleeves
- Clear contract for future implementations
- Testing of different risk models without core changes

### 2. Configuration-Driven Design
All parameters live in `system_config.json`. The system can be adjusted without code changes:
- Risk thresholds (drawdown, position size, etc.)
- Sleeve allocations
- Trading instruments and timeframes

### 3. Async-Ready Architecture
`SystemManager.initialize()` and `start()` are async-ready for future I/O operations (exchange connections, live data, etc.).

### 4. Separation of Concerns
- **SystemManager**: Orchestration only
- **ConfigLoader**: Configuration only
- **RiskManager**: Risk logic only
- **PositionSizer**: Position sizing only
- **DrawdownManager**: Drawdown control only

### 5. Placeholder Methods for Future Expansion
- `get_sleeve_allocation()`: Returns static allocations now, dynamic later
- `update_sleeve_performance()`: Records sleeve data for future dynamic allocation
- `get_dynamic_allocation()`: Will compute based on sleeve metrics

## Extensibility Points

### For v0.2+: Sleeve Integration
1. Create `Sleeve` base class in `src/sleeves/base.py`
2. Implement sleeve-specific strategies
3. Hook into `SystemManager.update_sleeve_performance()`
4. Implement dynamic allocation in `get_dynamic_allocation()`

### For v0.2+: Advanced Risk Management
1. Extend `RiskManager` with dynamic position limits per sleeve
2. Implement advanced drawdown strategies
3. Add correlation tracking between sleeves
4. Add emergency pause/kill-switch logic

### For v0.2+: Monitoring & Logging
1. Add comprehensive event logging
2. Integrate with external monitoring (Prometheus, etc.)
3. Add health checks
4. Add performance metrics tracking

## Success Criteria (Achieved ✓)

- [x] System initializes without errors
- [x] Configuration loads cleanly (with defaults fallback)
- [x] Risk management foundation is in place
- [x] Interfaces designed for extension
- [x] Code is clean, readable, well-documented
- [x] Ready for sleeve implementation

## Next Steps (v0.2)

1. **Implement Sleeves** (`src/sleeves/`)
   - Create base `Sleeve` class
   - Implement Sleeve 1 (X-Signal Momentum)
   - Integrate with SystemManager

2. **Dynamic Allocation** 
   - Track sleeve performance
   - Implement dynamic allocation logic
   - Test with backtesting data

3. **Integration with Freqtrade**
   - Create Freqtrade bot interface
   - Wire strategies to sleeves
   - Integrate with Freqtrade lifecycle

4. **Testing & Validation**
   - Unit tests for risk management
   - Integration tests for initialization
   - Backtesting simulation
