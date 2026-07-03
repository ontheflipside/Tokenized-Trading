from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import load_market_snapshot, read_watchlist
from src.paper_trader import append_paper_events
from src.report_writer import write_csv, write_html
from src.signal_engine import build_signals


def load_config() -> dict:
    config_path = ROOT / "configs" / "config.yaml"
    example_path = ROOT / "configs" / "config.example.yaml"
    selected = config_path if config_path.exists() else example_path
    with selected.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main() -> None:
    config = load_config()
    watchlist_path = ROOT / config["inputs"]["watchlist_path"]

    watchlist = read_watchlist(watchlist_path)
    snapshot = load_market_snapshot(watchlist, config)
    signals = build_signals(snapshot, config)

    write_csv(signals, ROOT / config["outputs"]["latest_signals_csv"])
    write_html(signals, ROOT / config["outputs"]["latest_signals_html"], config)
    event_log = append_paper_events(signals, ROOT / config["outputs"]["paper_trades_csv"])

    print("Tokenized Securities Research completed.")
    print(f"Signals generated: {len(signals)}")
    print(f"Paper events logged: {len(event_log)}")
    print(f"CSV report: {config['outputs']['latest_signals_csv']}")
    print(f"HTML report: {config['outputs']['latest_signals_html']}")


if __name__ == "__main__":
    main()
