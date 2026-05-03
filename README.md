# Tokenized Equity Strategy Agent

This is a first working version of a tokenized stock strategy agent. It is built as an alerting and paper trading system first. Live execution is intentionally not included in version one because the goal is to prove signal quality before placing real capital at risk.

## What it does

The agent monitors tokenized equity pairs such as `AAPLx/USD`, `TSLAx/USD`, and `NVDAx/USD`, compares them against the underlying public equity, and produces a daily signal report.

The agent focuses on four signal categories:

1. Tokenized equity premium or discount versus the underlying stock.
2. Order book imbalance on the tokenized market.
3. Liquidity depth and estimated slippage.
4. Simple risk controls, including max position size and stop thresholds.

## Why this approach

Tokenized equities are not just traditional stocks on a blockchain. They trade on different rails, may trade outside normal equity hours, and can show liquidity gaps. The edge is likely to come from dislocation and market structure inefficiency, not from ordinary stock picking.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp configs/config.example.yaml configs/config.yaml
python scripts/run_agent.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy configs\config.example.yaml configs\config.yaml
python scripts\run_agent.py
```

## Output

The agent creates:

```text
reports/latest_signals.csv
reports/latest_signals.html
reports/paper_trades.csv
```

## Signal interpretation

The final score ranges from negative to positive.

```text
score >= 70    strong long watch signal
score 40 to 69 positive watch signal
score -39 to 39 neutral
score -40 to -69 caution or possible exit
score <= -70   strong risk off or short watch signal
```

This is not a trading recommendation. It is a structured signal engine that you can refine with real performance data.
