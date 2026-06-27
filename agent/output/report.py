from pathlib import Path
import pandas as pd


def write_reports(rows: list[dict], report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)

    # --- CURRENT SNAPSHOT (no change) ---
    csv_path = report_dir / "latest_signals.csv"
    html_path = report_dir / "latest_signals.html"
    df.to_csv(csv_path, index=False)

    # --- NEW: HISTORY FILE ---
    history_path = report_dir / "signal_history.csv"

    if history_path.exists():
        existing_df = pd.read_csv(history_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        combined_df = df

    combined_df.to_csv(history_path, index=False)

    # --- HTML OUTPUT (no change) ---
    html = df.to_html(index=False, border=0)
    html_doc = f"""
    <html>
      <head>
        <title>Tokenized Equity Strategy Agent</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 30px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: right; }}
          th:first-child, td:first-child {{ text-align: left; }}
          th {{ background: #f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>Tokenized Equity Strategy Agent</h1>
        <p>Latest signal output. Version one is alerting and paper trading only.</p>
        {html}
      </body>
    </html>
    """

    html_path.write_text(html_doc, encoding="utf-8")

    return csv_path, html_path
