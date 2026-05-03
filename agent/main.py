from datetime import datetime, timezone

from agent.config import AgentConfig
from agent.data.equity import get_equity_last_price
from agent.data.kraken_xstocks import KrakenXStocksClient
from agent.signals.dislocation import premium_discount_pct
from agent.signals.liquidity import orderbook_metrics
from agent.signals.scoring import score_signal
from agent.output.report import write_reports
from agent.portfolio.paper import PaperPortfolio


def action_from_score(score: int) -> str:
    if score >= 70:
        return "WATCH_BUY"
    if score <= -70:
        return "WATCH_EXIT"
    return "HOLD"


def run(config_path: str = "configs/config.yaml") -> dict:
    cfg = AgentConfig.from_yaml(config_path)
    client = KrakenXStocksClient(cfg.kraken_base)
    report_dir = cfg.report_directory
    portfolio = PaperPortfolio(report_dir / "paper_trades.csv")

    rows = []
    for item in cfg.watchlist:
        equity = item["equity"]
        token_pair = item["token_pair"]

        equity_price = get_equity_last_price(equity)
        token_price = client.get_last_price(token_pair)
        orderbook = client.get_order_book(token_pair, cfg.orderbook_depth)
        liquidity = orderbook_metrics(orderbook)

        pd_pct = premium_discount_pct(token_price, equity_price)
        score, label = score_signal(pd_pct, liquidity, cfg.raw)
        action = action_from_score(score)

        reason = f"premium_discount={pd_pct}, imbalance={liquidity.get('imbalance')}, spread={liquidity.get('spread_pct')}"
        portfolio.log_signal(token_pair, action, token_price, score, label, reason)

        rows.append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "equity": equity,
            "token_pair": token_pair,
            "equity_price": equity_price,
            "token_price": token_price,
            "premium_discount_pct": pd_pct,
            "bid_depth_1pct_usd": liquidity.get("bid_depth_1pct_usd"),
            "ask_depth_1pct_usd": liquidity.get("ask_depth_1pct_usd"),
            "orderbook_imbalance": liquidity.get("imbalance"),
            "spread_pct": liquidity.get("spread_pct"),
            "score": score,
            "label": label,
            "action": action,
        })

    csv_path, html_path = write_reports(rows, report_dir)
    return {"csv": str(csv_path), "html": str(html_path), "rows": rows}


if __name__ == "__main__":
    result = run()
    print(f"Wrote CSV: {result['csv']}")
    print(f"Wrote HTML: {result['html']}")
