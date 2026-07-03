# Contributing

Thanks for your interest in contributing to Tokenized Securities Research.

This project is an early research prototype. The best contributions are practical, testable, and focused on improving signal quality, data integrity, documentation, or the research workflow.

## Good contribution areas

- Tokenized securities market data provider integrations.
- Market data validation and stale data checks.
- Premium and discount calculation improvements.
- Liquidity, spread, and slippage scoring.
- Backtesting and signal performance measurement.
- Dashboard improvements.
- Documentation and examples.
- Test coverage for the signal engine.

## Before opening a pull request

1. Open or review an issue describing the proposed change.
2. Keep the change focused.
3. Do not commit credentials, API keys, environment files, local config files, or personal financial data.
4. Do not commit generated report files from the reports directory.
5. Include a brief explanation of why the change improves the project.

## Local setup

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

To run the dashboard:

```bash
streamlit run app.py
```

## Pull request checklist

- [ ] The change does not add secrets or private data.
- [ ] The change does not add generated report files.
- [ ] The README or roadmap was updated if behavior changed.
- [ ] The change is consistent with the project disclaimer.
- [ ] The change keeps automated execution out of scope.

## Project scope

This project is for research and education. It is not designed to place orders, connect to brokerage accounts, or execute transactions.
