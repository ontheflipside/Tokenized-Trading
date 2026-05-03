import yfinance as yf


def get_equity_last_price(symbol: str) -> float | None:
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period="2d", interval="1m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="1d")
        if hist.empty:
            return None
        return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        return None
