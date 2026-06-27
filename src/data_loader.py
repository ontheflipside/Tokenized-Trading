from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class MarketRow:
    symbol: str
    name: str
    tokenized_pair: str
    category: str
    reference_price: float
    tokenized_price: float
    bid_price: float
    ask_price: float
    liquidity_score: float
    imbalance_score: float
    volatility_score: float


def read_watchlist(path: str | Path) -> pd.DataFrame:
    watchlist = pd.read_csv(path)
    required = {"symbol", "name", "tokenized_pair", "category"}
    missing = required.difference(watchlist.columns)
    if missing:
        raise ValueError(f"Watchlist is missing required columns: {sorted(missing)}")
    return watchlist


def _stable_unit(symbol: str, salt: str) -> float:
    raw = f"{symbol}:{salt}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _latest_close(symbol: str, period: str, interval: str) -> float:
    data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)

    if data.empty:
        raise ValueError(f"No price data returned for {symbol}")

    close = data["Close"].dropna()

    if close.empty:
        raise ValueError(f"No closing price available for {symbol}")

    latest = close.iloc[-1]

    if hasattr(latest, "iloc"):
        latest = latest.iloc[-1]

    return float(latest)


def _simulated_tokenized_metrics(symbol: str, reference_price: float) -> dict[str, float]:
    """Create deterministic placeholder market metrics for v1 development."""
    premium_pct = (_stable_unit(symbol, "premium") - 0.5) * 4.0
    spread_pct = 0.05 + _stable_unit(symbol, "spread") * 1.75
    liquidity_score = 20.0 + _stable_unit(symbol, "liquidity") * 80.0
    imbalance_score = (_stable_unit(symbol, "imbalance") - 0.5) * 200.0
    volatility_score = _stable_unit(symbol, "volatility") * 100.0

    tokenized_price = reference_price * (1 + premium_pct / 100.0)
    bid_price = tokenized_price * (1 - spread_pct / 200.0)
    ask_price = tokenized_price * (1 + spread_pct / 200.0)

    return {
        "tokenized_price": round(tokenized_price, 4),
        "bid_price": round(bid_price, 4),
        "ask_price": round(ask_price, 4),
        "liquidity_score": round(liquidity_score, 2),
        "imbalance_score": round(imbalance_score, 2),
        "volatility_score": round(volatility_score, 2),
    }


def load_market_snapshot(watchlist: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    period = config.get("data", {}).get("yfinance_period", "5d")
    interval = config.get("data", {}).get("yfinance_interval", "1d")

    rows: list[MarketRow] = []
    errors: list[dict[str, str]] = []

    for item in watchlist.to_dict(orient="records"):
        symbol = str(item["symbol"]).strip().upper()
        try:
            reference_price = _latest_close(symbol, period=period, interval=interval)
            metrics = _simulated_tokenized_metrics(symbol, reference_price)
            rows.append(
                MarketRow(
                    symbol=symbol,
                    name=str(item["name"]),
                    tokenized_pair=str(item["tokenized_pair"]),
                    category=str(item["category"]),
                    reference_price=round(reference_price, 4),
                    **metrics,
                )
            )
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)})

    if not rows:
        raise RuntimeError(f"No market rows could be loaded. Errors: {errors}")

    snapshot = pd.DataFrame([row.__dict__ for row in rows])
    if errors:
        snapshot.attrs["errors"] = errors
    return snapshot
