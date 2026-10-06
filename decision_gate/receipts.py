"""One receipt row per decision -> CSV (paper-first, #580)."""
import csv

RECEIPT_COLS = ["timestamp", "strategy", "pair", "side", "confidence",
                "votes", "route", "limits_checked", "limit_result",
                "stake", "outcome", "pnl_abs"]


class ReceiptWriter:
    def __init__(self, path: str):
        self.path = path
        self._fh = open(path, "w", newline="")
        self._w = csv.DictWriter(self._fh, fieldnames=RECEIPT_COLS)
        self._w.writeheader()

    def write(self, row: dict) -> None:
        self._w.writerow({c: row.get(c, "") for c in RECEIPT_COLS})
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()
