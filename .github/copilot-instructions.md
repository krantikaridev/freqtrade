# GitHub Copilot Instructions - Hybrid Sleeve Trading System

**Project**: Freqtrade-based multi-strategy trading system with dynamic risk allocation  
**Focus**: Professional, sustainable, capital-preservation-first approach  
**Target**: v1 launch with 3 sleeves (X-Signal Momentum, Trend Following, Mean Reversion)

---

## 📌 Core Philosophy (Non-Negotiable)

### 1. Risk First, Always

**Capital preservation > profits**. Every decision must answer: "What's the worst-case scenario?"

- Risk management code is more important than entry signal code
- A bad position sizer kills the account; a missed signal is forgotten
- When in doubt, choose the more conservative approach
- Every feature should have a clear downside risk assessment

**Nanoclaw Lesson**: The previous system suffered catastrophic capital bleed from:
- Too many low-quality trades (high rotation)
- Insufficient play budget controls (no frequency limits)
- No quality gates (mediocre trades taken same as high-conviction ones)
- Position sizing didn't adapt to system state

**Action**: Apply quality gates, play budgets, and drawdown-aware sizing. **These are non-optional.**

### 2. Quality Over Quantity

**Better to take 5 high-conviction trades than 50 mediocre ones.**

- Signal strength >= 60% minimum (no "maybe" trades)
- Risk/reward ratio must be favorable (1:2 at minimum)
- Each sleeve has daily trade limits (enforced by code)
- Trades that don't meet quality thresholds are **rejected, not debated**

**Nanoclaw Lesson**: Running 100 trades with 40% win rate = death spiral. Running 15 trades with 65% win rate = sustainable.

**Action**: When implementing entry logic, ask: "Would this meet the quality gate?" If no, redesign.

### 3. Simple > Complex

**Prefer readable, maintainable code over clever, fragile optimizations.**

- Use clear variable names: `min_signal_strength` not `mss`
- Avoid nested logic > 2 levels deep
- Extract complex logic into separate functions with single responsibility
- Default configuration values should be sensible (not require tuning)
- Add comments explaining *why*, not *what* (code shows what)

**Anti-pattern**: 
```python
# ❌ DON'T: Clever but unclear
allocation = {s: (p * (1 + mr[s]/100) if mr[s] > 0 else p * 0.8) for s, p in base.items()}
```

**Correct approach**:
```python
# ✅ DO: Clear and maintainable
for sleeve_name, base_pct in base_allocation.items():
    recent_return = sleeve_metrics[sleeve_name].return_7d
    if recent_return > 0:
        # Boost allocation for performing sleeves (up to cap)
        adjusted = min(base_pct * (1 + recent_return / 100), MAX_SLEEVE_ALLOCATION)
    else:
        # Reduce allocation for underperforming sleeves
        adjusted = base_pct * 0.8
    allocation[sleeve_name] = adjusted
```

### 4. Sustainability Over Aggression

**Can this system run for 12+ months without manual intervention? Will it survive a surprise drawdown?**

- Design for 8-hour, then 24-hour unattended operation
- Assume network failures, exchange outages, API limits
- Emergency exit logic must be simple and automatic
- Every threshold should have a clear justification in the design doc

**Example**: 
- Max daily trades: 8 (prevents over-rotation)
- Max drawdown before pause: 20% (tested in backtest)
- Min signal strength: 60% (70th percentile of historical signals)

---

## 🏗️ Hybrid Sleeve Architecture - Key Concepts

### Sleeve Structure

**3 Sleeves in v1**:

1. **Sleeve 1: X-Signal Momentum** (45–55% risk allocation)
   - 1–7 day holds
   - High-conviction X signals (≥75% confidence)
   - Max 3 trades/day
   - Focus: Fast capital growth with quality signals

2. **Sleeve 2: Trend Following** (25–35% risk allocation)
   - 3–21 day holds
   - Technical setups (ADX ≥ 25, trend confirmation)
   - Max 2 trades/day
   - Focus: Stable, lower-friction returns

3. **Sleeve 3: Mean Reversion** (15–25% risk allocation)
   - Hours to 4 days
   - Overextended moves (>2σ from MA)
   - Max 5 trades/day
   - Focus: High-frequency tactical opportunities

### Risk Architecture

```
SystemManager (top level)
  ├─ RiskManager (capital allocation, drawdown tracking)
  │  ├─ TradeQualityGate (signal strength, edge, budget checks)
  │  ├─ PlayBudget (daily trade frequency limits)
  │  ├─ PositionSizer (calculate position size)
  │  └─ DrawdownManager (monitor portfolio state)
  ├─ Sleeve 1 Strategy
  ├─ Sleeve 2 Strategy
  └─ Sleeve 3 Strategy
```

**Key Rule**: All trades **must pass through TradeQualityGate before execution**. No exceptions.

### Dynamic Risk Allocation

Risk allocation adjusts based on:
- **7-day sleeve performance** (return, Sharpe ratio)
- **Portfolio drawdown level** (0% → 100% to 20%+ → 0%)
- **Market volatility** (ATR percentile scaling position sizes)

**Your job**: Implement allocation logic that:
1. Calculates sleeve performance metrics
2. Applies adjustment factors
3. Respects hard constraints (min 10%, max 65% per sleeve)
4. Smoothly transitions between allocations

---

## 💻 Code Quality Standards

### 1. Documentation Requirements

**Every module, class, and function needs**:
- Docstring explaining purpose and usage
- Parameter types and descriptions
- Return type and description
- Example if complex
- Link to design doc (if relevant)

```python
def check_trade_quality(
    self,
    symbol: str,
    signal_strength: float,
    edge_estimate: float,
    drawdown_pct: float = 0.0,
    system_enabled: bool = True
) -> QualityCheckResult:
    """
    Check if a trade meets quality gates before execution.
    
    Implements core Nanoclaw lesson: prevent low-quality trade rotation.
    Trades are rejected if they don't meet minimum quality thresholds,
    have insufficient edge, or play budget is exhausted.
    
    Args:
        symbol: Trading pair (e.g., "BTC/USDT")
        signal_strength: Confidence level (0-1 scale)
        edge_estimate: Expected edge as decimal (0.01 = 1%)
        drawdown_pct: Current portfolio drawdown (0-1 scale)
        system_enabled: Whether system is enabled for trading
        
    Returns:
        QualityCheckResult with decision and detailed reasoning
        
    References:
        See hybrid-sleeve-design-v1.md § Trade Quality Requirements
        
    Example:
        >>> result = gate.check_trade_quality("BTC/USDT", 0.78, 0.02)
        >>> if result.allowed:
        ...     execute_trade()
    """
```

### 2. Configuration-Driven Design

**Rule**: Hardcoded values are forbidden (except constants with clear names).

- All parameters live in config dicts or dataclass configs
- Default configs should have sensible v1 values (in `system/config.py`)
- Override mechanism for testing and experimentation
- Document what each parameter does

```python
# ✅ GOOD: Configuration-driven
quality_config = {
    "min_signal_strength": 0.60,
    "min_edge_pct": 0.005,
    "drawdown_disable_trading": True,
    "drawdown_threshold": 0.15,
}
gate = TradeQualityGate(quality_config)

# ❌ BAD: Hardcoded thresholds scattered
if signal_strength > 0.60 and edge > 0.005:
    ...
```

### 3. Logging & Observability

**Structured logging at key decision points**:
- `logger.info()`: Major state changes (trade accepted, drawdown triggered)
- `logger.warning()`: Threshold violations (trade rejected, budget exhausted)
- `logger.debug()`: Details for debugging (calculation steps, intermediate values)

```python
logger.info(
    f"Trade {symbol} ACCEPTED: "
    f"signal={signal_strength:.2f}, edge={edge_estimate*100:.2f}%, "
    f"remaining_budget={budget.get_trades_remaining()}"
)

logger.warning(
    f"Trade {symbol} REJECTED: drawdown={drawdown_pct*100:.1f}% "
    f"exceeds threshold {self.drawdown_threshold*100:.1f}%"
)
```

### 4. Testing & Validation

**Code is not complete until tested**:
- Unit tests for core logic (risk calculations, gate decisions)
- Integration tests for multi-sleeve interactions
- Edge case tests (boundary conditions, error states)
- Backtest validation before live trading

```python
def test_quality_gate_rejects_low_signal():
    gate = TradeQualityGate({"min_signal_strength": 0.60})
    result = gate.check_trade_quality("BTC/USDT", signal_strength=0.55, edge_estimate=0.02)
    assert not result.allowed
    assert result.reason == QualityRejectionReason.LOW_SIGNAL_STRENGTH
```

### 5. Type Hints & Dataclasses

**All functions and classes must have type hints**:
- Helps catch bugs early
- Documents intended usage
- Enables better IDE support
- Required for production code

```python
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class PlayBudgetConfig:
    max_trades_per_day: int = 10
    max_trades_per_session: Optional[int] = None
    reset_mode: str = "daily"  # "daily", "session", "manual"

class PlayBudget:
    def __init__(self, config: PlayBudgetConfig) -> None:
        ...
    
    def can_trade(self) -> bool:
        ...
```

---

## 🚨 Anti-Patterns & What NOT to Do

### 1. The Over-Trading Trap (Nanoclaw)

**❌ DON'T**:
```python
# No play budget → 50 trades in 1 day
# No quality gate → Take every signal
# Result: High slippage, commission death, whipsaws
```

**✅ DO**:
```python
# Enforce play budget
if not self.play_budget.can_trade():
    logger.warning(f"Daily budget exhausted: {self.play_budget.trades_today}/max")
    return False

# Enforce quality gate
result = self.quality_gate.check_trade_quality(...)
if not result.allowed:
    logger.debug(f"Trade rejected: {result.reason}")
    return False
```

### 2. Ignoring Drawdown

**❌ DON'T**:
```python
# Keep trading at full size during 20% drawdown
# Guaranteed to blow up when luck turns
```

**✅ DO**:
```python
# Scale position size based on portfolio drawdown
drawdown_pct = (peak_equity - current_equity) / peak_equity
if drawdown_pct > 0.20:
    # Pause all new trades
    logger.warning("Portfolio DD > 20%, stopping new trades")
    return False
elif drawdown_pct > 0.15:
    # Reduce position size to 50%
    position_size *= 0.50
```

### 3. Unclear Variable Names

**❌ DON'T**:
```python
ss = 0.75  # What does this mean?
dd = 0.15  # Drawdown? Dividend yield?
r = (s * w + t * 0.3) / 2  # Impossible to understand
```

**✅ DO**:
```python
signal_strength = 0.75  # Range 0-1, where 1 = 100% confidence
portfolio_drawdown_pct = 0.15  # Range 0-1, 0.15 = 15% loss from peak
allocation_adjusted = (sleeve1_alloc * sleeve1_weight + sleeve2_alloc * sleeve2_default_weight) / 2
```

### 4. Magic Numbers Without Justification

**❌ DON'T**:
```python
if signal > 0.6 and edge > 0.005 and dd < 0.2:
    # Where do these numbers come from?
```

**✅ DO**:
```python
# Thresholds based on hybrid-sleeve-design-v1.md § Trade Quality Requirements
MIN_SIGNAL_STRENGTH = 0.60  # Sleeve 1 requires 75%, but system-wide minimum is 60%
MIN_EDGE_PCT = 0.005  # 0.5% edge minimum (Sleeve 3)
MAX_DRAWDOWN_FOR_TRADING = 0.20  # Stop new trades at 20% DD

if signal > MIN_SIGNAL_STRENGTH and edge > MIN_EDGE_PCT and dd < MAX_DRAWDOWN_FOR_TRADING:
    ...
```

### 5. Mixing Business Logic with Technical Details

**❌ DON'T**:
```python
def process_trade(self):
    # Calculate equity update, fetch price, check signals, size position,
    # update database, send notification, write to log...
    # 150 lines of tangled logic
```

**✅ DO**:
```python
def process_trade(self):
    """High-level orchestration"""
    signal = self._get_signal()
    quality_check = self._check_quality(signal)
    if quality_check.allowed:
        position = self._calculate_position(quality_check)
        self._execute_trade(position)
        self._log_trade(position)

def _check_quality(self, signal):
    """Separated concern: quality validation"""
    return self.quality_gate.check_trade_quality(...)
```

---

## 📋 Task-Specific Guidance

### When Implementing a New Sleeve

1. **Define the sleeve** in `hybrid-sleeve-design-v1.md`
   - Entry criteria (specific, measurable)
   - Exit criteria (specific, measurable)
   - Target hold time
   - Risk/reward ratio
   - Performance targets

2. **Implement core logic** in `src/sleeves/`
   - Use consistent class structure: `Sleeve1XSignalMomentum`, etc.
   - Inherit from base class if applicable
   - Each sleeve tracks its own: recent trades, performance metrics, budget

3. **Add to RiskManager**
   - Register sleeve in `SystemManager`
   - Wire quality gate and play budget
   - Add sleeve-specific allocation logic

4. **Backtest extensively**
   - Test on 12+ months of historical data
   - Verify win rate, Sharpe ratio, max DD match design targets
   - If not, adjust entry/exit criteria (not thresholds)

5. **Paper trade 2–4 weeks**
   - Before going live, validate on live feeds
   - Check for slippage, order fill issues, timing
   - Monitor daily

### When Adding a Risk Control Feature

1. **Identify the downside risk** being addressed
   - Example: "Too many low-quality trades → death spiral"
   - Example: "High drawdown → compounding losses"

2. **Define the threshold or rule**
   - Should be in design doc first
   - Should have clear justification (backtested? historical data? theory?)

3. **Implement with clear logging**
   - Log when rule is triggered
   - Log the decision and reason
   - Make it observable and debuggable

4. **Test edge cases**
   - What happens at boundary? (draw down exactly at 15%?)
   - What if multiple rules trigger simultaneously?
   - Graceful degradation?

5. **Update configuration**
   - Add parameter to default config
   - Document in docstring
   - Make it tunable without code changes

### When Optimizing Performance

1. **Measure first** (don't optimize blindly)
   - Backtest current version
   - Identify bottleneck
   - Measure again after change

2. **Prefer clarity over cleverness**
   - 10% performance gain at cost of unreadable code = bad trade-off
   - 2% performance gain + 30% more readable code = good trade-off

3. **Avoid premature optimization**
   - System spends 90% of time waiting for market data, not computing
   - Optimize after profiling, not before

4. **Don't break safety guarantees**
   - Example: "I'll use float instead of Decimal for speed" → Financial data corruption

---

## 🔗 Key Files & Architecture

### Core Risk Management
- `src/risk/base.py` — Abstract interfaces (RiskManager, PositionSizer, DrawdownManager)
- `src/risk/simple.py` — Concrete implementations (SimpleRiskManager, etc.)
- `src/risk/quality_gate.py` — TradeQualityGate + PlayBudget (prevents Nanoclaw trap)

### System Orchestration
- `src/system/manager.py` — SystemManager (central hub)
- `src/system/config.py` — ConfigLoader + default configuration

### Documentation
- `docs/hybrid-sleeve-design-v1.md` — Design spec (source of truth)
- `.github/copilot-instructions.md` — This file

### Key Design Principles in Code
- **Quality gate is mandatory**: `result = quality_gate.check_trade_quality(...)`
- **Play budget is enforced**: `if not play_budget.can_trade(): return`
- **Drawdown adjusts position size**: `size *= get_drawdown_factor(dd_pct)`
- **All allocation is dynamic**: Adjust every 2 weeks based on performance
- **Configuration drives behavior**: No hardcoded thresholds in logic

---

## ✅ Checklist Before Submitting Code

- [ ] Code follows all guidelines above (simplicity, documentation, types)
- [ ] If adding logic, does it serve a clear purpose in hybrid-sleeve-design-v1.md?
- [ ] Logging is comprehensive (info, warning, debug at key points)
- [ ] Configuration is externalized (no magic numbers)
- [ ] All functions/classes have docstrings with examples
- [ ] Handles error cases (what if data is missing? API fails?)
- [ ] No hardcoded values or assumptions about market
- [ ] Backtest results (if applicable) meet design targets
- [ ] Code is testable (dependency injection, clear interfaces)
- [ ] Risk controls are documented and logged
- [ ] Design decisions reference hybrid-sleeve-design-v1.md

---

## 🎯 Remember: Nanoclaw Lessons

The previous system (Nanoclaw) failed due to:

1. **High trade rotation without quality gate** → Solution: TradeQualityGate
2. **No play budget limits** → Solution: PlayBudget with daily reset
3. **Fixed position sizing during drawdown** → Solution: Drawdown-aware scaling
4. **Mediocre signals treated same as high-conviction** → Solution: Signal strength thresholds
5. **Small capital amplified losses** → Solution: Risk-first thinking in all code

**Every line of code should prevent one of these failures.**

---

## 📞 Questions & Ambiguity

If a task is ambiguous:
1. Check `hybrid-sleeve-design-v1.md` first
2. Look for similar patterns in existing code
3. Prefer conservative approach (less risk) if unclear
4. Ask clarifying questions (document trade-offs)

**Golden Rule**: When in doubt, choose the approach that's safer for capital.

---

**Last Updated**: July 2026  
**Version**: v1.0  
**Applies To**: Hybrid Sleeve System, all development
