from pathlib import Path
import pandas as pd
from datetime import datetime, timezone


class PaperPortfolio:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            pd.DataFrame(columns=[
                "timestamp_utc", "symbol", "action", "price", "score", "label", "reason"
            ]).to_csv(self.path, index=False)

    def log_signal(self, symbol: str, action: str, price: float | None, score: int, label: str, reason: str) -> None:
        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "action": action,
            "price": price,
            "score": score,
            "label": label,
            "reason": reason,
        }
        existing = pd.read_csv(self.path)
        pd.concat([existing, pd.DataFrame([row])], ignore_index=True).to_csv(self.path, index=False)
