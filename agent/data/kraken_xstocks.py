import requests
from typing import Any


class KrakenXStocksClient:
    def __init__(self, base_url: str = "https://api.kraken.com/0/public", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, params=params or {}, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"Kraken API error: {payload['error']}")
        return payload.get("result", {})

    def get_tokenized_pairs(self) -> dict:
        return self._get("AssetPairs", {"aclass_base": "tokenized_asset"})

    def get_ticker(self, pair: str) -> dict | None:
        result = self._get("Ticker", {"pair": pair, "asset_class": "tokenized_asset"})
        if not result:
            return None
        return next(iter(result.values()))

    def get_last_price(self, pair: str) -> float | None:
        ticker = self.get_ticker(pair)
        if not ticker:
            return None
        try:
            return float(ticker["c"][0])
        except Exception:
            return None

    def get_order_book(self, pair: str, count: int = 25) -> dict | None:
        result = self._get("Depth", {"pair": pair, "count": count, "asset_class": "tokenized_asset"})
        if not result:
            return None
        return next(iter(result.values()))
