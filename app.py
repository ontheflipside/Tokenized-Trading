from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from src.data_loader import load_market_snapshot, read_watchlist
from src.paper_trader import append_paper_events
from src.report_writer import write_csv, write_html
from src.signal_engine import build_signals


ROOT = Path(__file__).resolve().parent
HISTORY_PATH = ROOT / "reports" / "signal_history.csv"
REQUIRED_HISTORY_COLUMNS = {"run_id", "symbol", "timestamp_utc", "final_score", "signal"}
WATCHLIST_COLUMNS = ["symbol", "name", "tokenized_pair", "category"]
LEGACY_RENAME_MAP = {
    "equity": "symbol",
    "token_pair": "tokenized_pair",
    "equity_price": "reference_price",
    "token_price": "tokenized_price",
    "premium_discount_pct": "premium_discount_percent",
    "spread_pct": "bid_ask_spread_percent",
    "score": "final_score",
    "label": "signal",
    "reason": "notes",
}


def load_config() -> dict:
    config_path = ROOT / "configs" / "config.yaml"
    example_path = ROOT / "configs" / "config.example.yaml"
    selected = config_path if config_path.exists() else example_path

    with selected.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_watchlist(path: Path) -> pd.DataFrame:
    if path.exists():
        watchlist = pd.read_csv(path)
    else:
        watchlist = pd.DataFrame(columns=WATCHLIST_COLUMNS)

    for column in WATCHLIST_COLUMNS:
        if column not in watchlist.columns:
            watchlist[column] = ""

    return watchlist[WATCHLIST_COLUMNS].fillna("")


def save_watchlist(path: Path, watchlist: pd.DataFrame) -> pd.DataFrame:
    cleaned = watchlist.copy()
    for column in WATCHLIST_COLUMNS:
        cleaned[column] = cleaned[column].astype(str).str.strip()

    cleaned = cleaned[cleaned["symbol"] != ""]
    cleaned["symbol"] = cleaned["symbol"].str.upper()
    cleaned = cleaned.drop_duplicates(subset=["symbol"], keep="last")
    cleaned = cleaned.sort_values("symbol")

    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(path, index=False)
    return cleaned


def normalize_signal_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        return history

    normalized = history.rename(columns=LEGACY_RENAME_MAP).copy()

    if "run_id" not in normalized.columns:
        normalized.insert(0, "run_id", "legacy")

    if "signal" not in normalized.columns and "signal_label" in normalized.columns:
        normalized["signal"] = normalized["signal_label"]

    if "final_score" in normalized.columns:
        normalized["final_score"] = pd.to_numeric(normalized["final_score"], errors="coerce")

    if "timestamp_utc" in normalized.columns:
        normalized["timestamp_utc"] = pd.to_datetime(normalized["timestamp_utc"], errors="coerce")

    return normalized


def append_signal_history(signals: pd.DataFrame) -> pd.DataFrame:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    run_id = pd.Timestamp.utcnow().strftime("%Y%m%d%H%M%S")
    history_rows = signals.copy()
    history_rows.insert(0, "run_id", run_id)

    if HISTORY_PATH.exists():
        existing = normalize_signal_history(pd.read_csv(HISTORY_PATH))
        combined = pd.concat([existing, history_rows], ignore_index=True)
    else:
        combined = history_rows

    if {"run_id", "symbol"}.issubset(combined.columns):
        combined = combined.drop_duplicates(subset=["run_id", "symbol"], keep="last")

    combined.to_csv(HISTORY_PATH, index=False)
    return combined


def load_signal_history() -> pd.DataFrame:
    if HISTORY_PATH.exists():
        return normalize_signal_history(pd.read_csv(HISTORY_PATH))
    return pd.DataFrame()


def run_agent() -> pd.DataFrame:
    config = load_config()
    watchlist_path = ROOT / config["inputs"]["watchlist_path"]

    watchlist = read_watchlist(watchlist_path)
    snapshot = load_market_snapshot(watchlist, config)
    signals = build_signals(snapshot, config)

    write_csv(signals, ROOT / config["outputs"]["latest_signals_csv"])
    write_html(signals, ROOT / config["outputs"]["latest_signals_html"], config)
    append_paper_events(signals, ROOT / config["outputs"]["paper_trades_csv"])
    append_signal_history(signals)

    return signals


def render_watchlist_editor(watchlist_path: Path) -> None:
    st.header("Watchlist")
    st.caption("Edit the symbols you want included in the next signal run.")

    watchlist = load_watchlist(watchlist_path)

    edited = st.data_editor(
        watchlist,
        num_rows="dynamic",
        width="stretch",
        key="watchlist_editor",
        column_config={
            "symbol": st.column_config.TextColumn("Symbol", required=True),
            "name": st.column_config.TextColumn("Company / Asset Name"),
            "tokenized_pair": st.column_config.TextColumn("Tokenized Pair"),
            "category": st.column_config.TextColumn("Category"),
        },
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save Watchlist"):
            saved = save_watchlist(watchlist_path, edited)
            st.success(f"Watchlist saved with {len(saved)} symbols.")
            st.rerun()

    with col2:
        st.info("Use the blank row at the bottom to add a symbol. Delete a row by selecting it and pressing delete.")


def render_latest_signals(signals: pd.DataFrame) -> None:
    st.header("Latest Signals")

    if signals.empty:
        st.info("No signal report found yet. Click 'Run Signal Report' in the sidebar.")
        return

    col1, col2, col3, col4 = st.columns(4)

    best_row = signals.sort_values("final_score", ascending=False).iloc[0]
    worst_row = signals.sort_values("final_score", ascending=True).iloc[0]

    col1.metric("Signals Generated", len(signals))
    col2.metric("Best Score", f"{best_row['symbol']} {best_row['final_score']}")
    col3.metric("Weakest Score", f"{worst_row['symbol']} {worst_row['final_score']}")
    col4.metric("Watch Signals", int(signals["signal"].isin(["STRONG_WATCH", "WATCH"]).sum()))

    st.dataframe(signals, width="stretch")

    csv_data = signals.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name="latest_signals.csv",
        mime="text/csv",
    )

    st.subheader("Plain English Summary")

    for _, row in signals.iterrows():
        st.write(
            f"**{row['symbol']}**: {row['signal']} with a score of "
            f"{row['final_score']}. Notes: {row['notes']}."
        )


def render_signal_history() -> None:
    st.header("Signal History")
    history = load_signal_history()

    if history.empty:
        st.info("No signal history has been recorded yet. Run a signal report to start building history.")
        return

    missing = REQUIRED_HISTORY_COLUMNS.difference(history.columns)
    if missing:
        st.warning(
            "The existing signal history file uses an older format and cannot be charted yet. "
            "Run a new signal report to create history in the current format."
        )
        st.caption(f"Missing columns: {', '.join(sorted(missing))}")
        st.dataframe(history, width="stretch")
        return

    history["timestamp_utc"] = pd.to_datetime(history["timestamp_utc"], errors="coerce")
    history = history.dropna(subset=["timestamp_utc", "symbol"])

    if history.empty:
        st.info("Signal history exists, but it does not contain usable timestamp and symbol rows yet.")
        return

    history = history.sort_values(["timestamp_utc", "symbol"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Historical Rows", len(history))
    col2.metric("Unique Symbols", history["symbol"].nunique())
    col3.metric("Runs Captured", history["run_id"].nunique())

    symbols = sorted(history["symbol"].dropna().unique())
    selected_symbols = st.multiselect(
        "Select symbols for history view",
        options=symbols,
        default=symbols,
    )

    filtered = history[history["symbol"].isin(selected_symbols)] if selected_symbols else history

    st.subheader("Score Trend")
    if not filtered.empty:
        chart_data = filtered.pivot_table(
            index="timestamp_utc",
            columns="symbol",
            values="final_score",
            aggfunc="last",
        ).sort_index()
        st.line_chart(chart_data)

    st.subheader("History Table")
    st.dataframe(filtered.sort_values("timestamp_utc", ascending=False), width="stretch")

    history_csv = history.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Signal History",
        data=history_csv,
        file_name="signal_history.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(
        page_title="Tokenized Equity Strategy Agent",
        layout="wide",
    )

    st.title("Tokenized Equity Strategy Agent")
    st.caption("Research dashboard for tokenized equity signal analysis.")

    st.warning(
        "This is a research tool. It does not place trades or execute orders. "
        "Current tokenized market metrics are placeholders until a live data provider is connected."
    )

    config = load_config()
    watchlist_path = ROOT / config["inputs"]["watchlist_path"]

    st.sidebar.header("Project Controls")
    st.sidebar.write("Watchlist file:")
    st.sidebar.code(str(watchlist_path))
    st.sidebar.write("History file:")
    st.sidebar.code(str(HISTORY_PATH))

    if st.sidebar.button("Run Signal Report"):
        with st.spinner("Running signal engine..."):
            signals = run_agent()
        st.success("Signal report generated and added to signal history.")
    else:
        latest_path = ROOT / config["outputs"]["latest_signals_csv"]
        if latest_path.exists():
            signals = pd.read_csv(latest_path)
        else:
            signals = pd.DataFrame()

    watchlist_tab, latest_tab, history_tab = st.tabs(["Watchlist", "Latest Signals", "Signal History"])

    with watchlist_tab:
        render_watchlist_editor(watchlist_path)

    with latest_tab:
        render_latest_signals(signals)

    with history_tab:
        render_signal_history()


if __name__ == "__main__":
    main()
