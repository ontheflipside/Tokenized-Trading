def premium_discount_pct(token_price: float | None, equity_price: float | None) -> float | None:
    if token_price is None or equity_price is None or equity_price == 0:
        return None
    return ((token_price - equity_price) / equity_price) * 100.0
