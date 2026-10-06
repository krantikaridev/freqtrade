"""Decision gate for freqtrade signals (paper-first, #580).

Generate -> judge -> enforce, outside the strategy:
  strategy signal -> confidence gate -> risk limits -> receipt CSV.

No live trading. Routes: trade | wait | skip | blocked.
"""
from .gate import ConfidenceGate, Signal, Verdict
from .limits import RiskEnforcer, LimitsConfig, LimitCheck
from .receipts import ReceiptWriter, RECEIPT_COLS

__all__ = ["ConfidenceGate", "Signal", "Verdict", "RiskEnforcer",
           "LimitsConfig", "LimitCheck", "ReceiptWriter", "RECEIPT_COLS"]
