from datetime import datetime, timezone, timedelta
import pandas as pd
from agent.data.kraken_xstocks import KrakenXStocksClient


def update_outcomes(csv_path: str, kraken_base: str):
    df = pd.read_csv(csv_path)

    client = KrakenXStocksClient(kraken_base)
    now = datetime.now(timezone.utc)

    for i, row in df.iterrows():
        if pd.isna(row["price"]):
            continue

        signal_time = datetime.fromisoformat(row["timestamp_utc"])
        symbol = row["symbol"]

        current_price = client.get_last_price(symbol)

        if current_price is None:
            continue

        # 1 hour
        if pd.isna(row["price_1h_later"]):
            if now - signal_time >= timedelta(hours=1):
                df.at[i, "price_1h_later"] = current_price
                df.at[i, "return_1h_pct"] = ((current_price - row["price"]) / row["price"]) * 100

        # 1 day
        if pd.isna(row["price_1d_later"]):
            if now - signal_time >= timedelta(days=1):
                df.at[i, "price_1d_later"] = current_price
                df.at[i, "return_1d_pct"] = ((current_price - row["price"]) / row["price"]) * 100

        # 3 day
        if pd.isna(row["price_3d_later"]):
            if now - signal_time >= timedelta(days=3):
                df.at[i, "price_3d_later"] = current_price
                df.at[i, "return_3d_pct"] = ((current_price - row["price"]) / row["price"]) * 100

    df.to_csv(csv_path, index=False)