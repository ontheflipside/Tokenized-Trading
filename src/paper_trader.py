from __future__ import annotations

from pathlib import Path

import pandas as pd


EVENT_SIGNALS = {"STRONG_WATCH", "RISK_OFF"}


def append_paper_events(signals: pd.DataFrame, path: str | Path) -> pd.DataFrame:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    events = signals[signals["signal"].isin(EVENT_SIGNALS)].copy()
    if events.empty:
        return pd.read_csv(output_path) if output_path.exists() else pd.DataFrame()

    events = events[
        [
            "timestamp_utc",
            "symbol",
            "tokenized_pair",
            "signal",
            "final_score",
            "reference_price",
            "tokenized_price",
            "notes",
        ]
    ]

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, events], ignore_index=True)
    else:
        combined = events

    combined = combined.drop_duplicates(subset=["timestamp_utc", "symbol", "signal"])
    combined.to_csv(output_path, index=False)
    return combined
