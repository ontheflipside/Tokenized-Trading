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


def load_config() -> dict:
    config_path = ROOT / "configs" / "config.yaml"
    example_path = ROOT / "configs" / "config.example.yaml"
    selected = config_path if config_path.exists() else example_path

    with selected.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def append_signal_history(signals: pd.DataFrame) -> pd.DataFrame:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    run_id = pd.Timestamp.utcnow().strftime("%Y%m%d%H%M%S")
    history_rows = signals.copy()
    history_rows.insert(0, "run_id", run_id)

    if HISTORY_PATH.exists():
        existing = pd.read_csv(HISTORY_PATH)
        combined = pd.concat([existing, history_rows], ignore_index=True)
    else:
        combined = history_rows

    combined = combined.drop_duplicates(subset=["run_id", "symbol"], keep="last")
    combined.to_csv(HISTORY_PATH, index=False)
    return combined


def load_signal_history() -> pd.DataFrame:
    if HISTORY_PATH.exists():
        return pd.read_csv(HISTORY_PATH)
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

    history["timestamp_utc"] = pd.to_datetime(history["timestamp_utc"], errors="coerce")
    history = history.sort_values(["timestamp_utc", "symbol"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Historical Rows", len(history))
    col2.metric("Unique Symbols", history["symbol"].nunique())
    col3.metric("Runs Captured", history["run_id"].nunique())

    symbols = sorted(history["symbol"].dropna().unique())
    selected_symbols = st.multiselect(
        "Select symbols for history view",
        options=symbols,
        default=symbols[: min(len(symbols), 4)],
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

    st.header("Watchlist")

    if watchlist_path.exists():
        watchlist = pd.read_csv(watchlist_path)
        st.dataframe(watchlist, width="stretch")
    else:
        st.error("Watchlist file not found.")

    latest_tab, history_tab = st.tabs(["Latest Signals", "Signal History"])

    with latest_tab:
        render_latest_signals(signals)

    with history_tab:
        render_signal_history()


if __name__ == "__main__":
    main()
