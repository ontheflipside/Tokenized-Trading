from pathlib import Path
import pandas as pd
from datetime import datetime, timezone


class PaperPortfolio:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            pd.DataFrame(columns=[
                "timestamp_utc",
                "symbol",
                "action",
                "price",
                "score",
                "label",
                "reason",
                "price_1h_later",
                "price_1d_later",
                "price_3d_later",
                "return_1h_pct",
                "return_1d_pct",
                "return_3d_pct",
            ]).to_csv(self.path, index=False)

    def log_signal(
        self,
        symbol: str,
        action: str,
        price: float | None,
        score: int,
        label: str,
        reason: str,
    ) -> None:
        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "action": action,
            "price": price,
            "score": score,
            "label": label,
            "reason": reason,
            "price_1h_later": None,
            "price_1d_later": None,
            "price_3d_later": None,
            "return_1h_pct": None,
            "return_1d_pct": None,
            "return_3d_pct": None,
        }

        existing = pd.read_csv(self.path)
        updated = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
        updated.to_csv(self.path, index=False)