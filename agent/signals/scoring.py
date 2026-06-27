def score_signal(premium_discount: float | None, liquidity: dict, cfg: dict) -> dict:
    if premium_discount is None:
        return {
            "score": 0,
            "label": "NO DATA",
            "signal_label": "NO DATA",
            "confidence": "NONE",
            "reason": "Missing tokenized price or underlying equity price.",
        }

    signals_cfg = cfg.get("signals", {})
    buy_threshold = float(signals_cfg.get("dislocation_buy_threshold_pct", 1.5))
    sell_threshold = float(signals_cfg.get("dislocation_sell_threshold_pct", -1.5))
    min_liquidity = float(signals_cfg.get("min_liquidity_usd_1pct_depth", 25000))
    min_imbalance = float(signals_cfg.get("min_orderbook_imbalance", 0.15))

    score = 0
    reasons = []

    if premium_discount >= buy_threshold:
        score += 30
        signal_label = "PREMIUM"
        reasons.append("Tokenized price is trading above the underlying equity.")
    elif premium_discount <= sell_threshold:
        score -= 30
        signal_label = "DISCOUNT"
        reasons.append("Tokenized price is trading below the underlying equity.")
    else:
        signal_label = "NO MATERIAL DISLOCATION"
        reasons.append("Tokenized price is close to the underlying equity.")

    imbalance = liquidity.get("imbalance")
    if imbalance is not None:
        if imbalance >= min_imbalance:
            score += 25
            reasons.append("Buyer pressure is stronger than seller pressure.")
        elif imbalance <= -min_imbalance:
            score -= 25
            reasons.append("Seller pressure is stronger than buyer pressure.")
        else:
            reasons.append("Order book pressure is balanced.")
    else:
        reasons.append("Order book imbalance data is unavailable.")

    bid_depth = liquidity.get("bid_depth_1pct_usd") or 0
    ask_depth = liquidity.get("ask_depth_1pct_usd") or 0
    if min(bid_depth, ask_depth) >= min_liquidity:
        score += 15
        reasons.append("Liquidity depth is sufficient.")
    else:
        score -= 10
        reasons.append("Liquidity depth is thin, so the signal is less reliable.")

    spread = liquidity.get("spread_pct")
    if spread is not None:
        if spread <= 0.20:
            score += 10
            reasons.append("Spread is tight.")
        elif spread >= 1.00:
            score -= 15
            reasons.append("Spread is wide.")
        else:
            reasons.append("Spread is moderate.")
    else:
        reasons.append("Spread data is unavailable.")

    if score >= 70:
        label = "STRONG WATCH"
        confidence = "HIGH"
    elif score >= 40:
        label = "POSITIVE WATCH"
        confidence = "MEDIUM"
    elif score <= -70:
        label = "RISK OFF"
        confidence = "HIGH NEGATIVE"
    elif score <= -40:
        label = "NEGATIVE WATCH"
        confidence = "MEDIUM NEGATIVE"
    else:
        label = "NEUTRAL"
        confidence = "LOW"

    return {
        "score": score,
        "label": label,
        "signal_label": signal_label,
        "confidence": confidence,
        "reason": " ".join(reasons),
    }