def score_signal(premium_discount: float | None, liquidity: dict, cfg: dict) -> tuple[int, str]:
    if premium_discount is None:
        return 0, "NO DATA"

    signals_cfg = cfg.get("signals", {})
    buy_threshold = float(signals_cfg.get("dislocation_buy_threshold_pct", 1.5))
    sell_threshold = float(signals_cfg.get("dislocation_sell_threshold_pct", -1.5))
    min_liquidity = float(signals_cfg.get("min_liquidity_usd_1pct_depth", 25000))
    min_imbalance = float(signals_cfg.get("min_orderbook_imbalance", 0.15))

    score = 0

    if premium_discount >= buy_threshold:
        score += 30
    elif premium_discount <= sell_threshold:
        score -= 30

    imbalance = liquidity.get("imbalance")
    if imbalance is not None:
        if imbalance >= min_imbalance:
            score += 25
        elif imbalance <= -min_imbalance:
            score -= 25

    bid_depth = liquidity.get("bid_depth_1pct_usd") or 0
    ask_depth = liquidity.get("ask_depth_1pct_usd") or 0
    if min(bid_depth, ask_depth) >= min_liquidity:
        score += 15
    else:
        score -= 10

    spread = liquidity.get("spread_pct")
    if spread is not None:
        if spread <= 0.20:
            score += 10
        elif spread >= 1.00:
            score -= 15

    if score >= 70:
        label = "STRONG WATCH"
    elif score >= 40:
        label = "POSITIVE WATCH"
    elif score <= -70:
        label = "RISK OFF"
    elif score <= -40:
        label = "NEGATIVE WATCH"
    else:
        label = "NEUTRAL"

    return score, label
