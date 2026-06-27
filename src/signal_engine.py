from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _premium_discount_pct(row: pd.Series) -> float:
    if row["reference_price"] == 0:
        return 0.0
    return ((row["tokenized_price"] - row["reference_price"]) / row["reference_price"]) * 100.0


def _spread_pct(row: pd.Series) -> float:
    midpoint = (row["bid_price"] + row["ask_price"]) / 2.0
    if midpoint == 0:
        return 0.0
    return ((row["ask_price"] - row["bid_price"]) / midpoint) * 100.0


def _score_row(row: pd.Series, config: dict[str, Any]) -> tuple[float, str]:
    risk = config.get("risk", {})
    max_spread = float(risk.get("max_spread_percent", 1.5))
    max_premium = float(risk.get("max_premium_percent", 2.0))
    min_liquidity = float(risk.get("min_liquidity_score", 40))

    premium = float(row["premium_discount_percent"])
    spread = float(row["bid_ask_spread_percent"])
    liquidity = float(row["liquidity_score"])
    imbalance = float(row["imbalance_score"])
    volatility = float(row["volatility_score"])

    score = 0.0
    score += np.clip(-premium / max_premium, -1.0, 1.0) * 30.0
    score += np.clip(imbalance / 100.0, -1.0, 1.0) * 25.0
    score += ((liquidity - min_liquidity) / max(100.0 - min_liquidity, 1.0)) * 25.0
    score += np.clip((max_spread - spread) / max_spread, -1.0, 1.0) * 15.0
    score -= np.clip(volatility / 100.0, 0.0, 1.0) * 10.0

    score = float(np.clip(score, -100.0, 100.0))
    notes = []
    if premium > max_premium:
        notes.append("premium above risk limit")
    elif premium < -max_premium:
        notes.append("discount versus reference equity")
    if spread > max_spread:
        notes.append("wide spread")
    if liquidity < min_liquidity:
        notes.append("thin liquidity")
    if imbalance > 40:
        notes.append("positive order book imbalance")
    if imbalance < -40:
        notes.append("negative order book imbalance")

    return round(score, 2), "; ".join(notes) if notes else "no major risk flag"


def _signal(score: float, config: dict[str, Any]) -> str:
    agent = config.get("agent", {})
    strong = float(agent.get("score_buy_threshold", 70))
    watch = float(agent.get("score_watch_threshold", 40))
    caution = float(agent.get("score_caution_threshold", -40))
    risk_off = float(agent.get("score_exit_threshold", -70))

    if score >= strong:
        return "STRONG_WATCH"
    if score >= watch:
        return "WATCH"
    if score <= risk_off:
        return "RISK_OFF"
    if score <= caution:
        return "CAUTION"
    return "NEUTRAL"


def build_signals(snapshot: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    signals = snapshot.copy()
    signals["premium_discount_percent"] = signals.apply(_premium_discount_pct, axis=1).round(4)
    signals["bid_ask_spread_percent"] = signals.apply(_spread_pct, axis=1).round(4)

    scored = signals.apply(lambda row: _score_row(row, config), axis=1)
    signals["final_score"] = [item[0] for item in scored]
    signals["notes"] = [item[1] for item in scored]
    signals["signal"] = signals["final_score"].apply(lambda score: _signal(float(score), config))
    signals["timestamp_utc"] = pd.Timestamp.utcnow().isoformat()

    ordered_columns = [
        "symbol", "name", "tokenized_pair", "category",
        "reference_price", "tokenized_price", "premium_discount_percent",
        "bid_price", "ask_price", "bid_ask_spread_percent",
        "liquidity_score", "imbalance_score", "volatility_score",
        "final_score", "signal", "notes", "timestamp_utc",
    ]
    return signals[ordered_columns].sort_values("final_score", ascending=False)
