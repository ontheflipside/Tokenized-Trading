from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def write_csv(signals: pd.DataFrame, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    signals.to_csv(output_path, index=False)


def write_html(signals: pd.DataFrame, path: str | Path, config: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    title = config.get("agent", {}).get("name", "Tokenized Equity Strategy Agent")
    generated_at = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    table = signals.to_html(index=False, classes="signals", border=0)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
    h1 {{ margin-bottom: 4px; }}
    .meta {{ color: #666; margin-bottom: 20px; }}
    table.signals {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    table.signals th, table.signals td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
    table.signals th {{ background: #f1f1f1; }}
    table.signals td:nth-child(1), table.signals td:nth-child(2), table.signals td:nth-child(3), table.signals td:nth-child(4), table.signals td:nth-child(15), table.signals td:nth-child(16), table.signals td:nth-child(17) {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">Generated: {generated_at}</div>
  {table}
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
