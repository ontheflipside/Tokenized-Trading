def _sum_depth(levels: list, reference_price: float, pct_band: float, side: str) -> float:
    total = 0.0
    if side == "bid":
        cutoff = reference_price * (1 - pct_band / 100)
        for price, qty, *_ in levels:
            p, q = float(price), float(qty)
            if p >= cutoff:
                total += p * q
    else:
        cutoff = reference_price * (1 + pct_band / 100)
        for price, qty, *_ in levels:
            p, q = float(price), float(qty)
            if p <= cutoff:
                total += p * q
    return total


def orderbook_metrics(orderbook: dict | None, pct_band: float = 1.0) -> dict:
    if not orderbook:
        return {"bid_depth_1pct_usd": None, "ask_depth_1pct_usd": None, "imbalance": None, "spread_pct": None}

    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])
    if not bids or not asks:
        return {"bid_depth_1pct_usd": None, "ask_depth_1pct_usd": None, "imbalance": None, "spread_pct": None}

    best_bid = float(bids[0][0])
    best_ask = float(asks[0][0])
    mid = (best_bid + best_ask) / 2.0

    bid_depth = _sum_depth(bids, mid, pct_band, "bid")
    ask_depth = _sum_depth(asks, mid, pct_band, "ask")
    total_depth = bid_depth + ask_depth

    imbalance = (bid_depth - ask_depth) / total_depth if total_depth > 0 else None
    spread_pct = ((best_ask - best_bid) / mid) * 100 if mid > 0 else None

    return {
        "bid_depth_1pct_usd": bid_depth,
        "ask_depth_1pct_usd": ask_depth,
        "imbalance": imbalance,
        "spread_pct": spread_pct,
    }
