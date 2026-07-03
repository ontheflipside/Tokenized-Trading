# Roadmap

This roadmap frames the Tokenized Equity Strategy Agent as an open research project. The priorities are ordered to make the project more credible, testable, and useful to outside contributors.

## v0.1.0: Public prototype

Status: current public launch baseline.

- Local command line signal runner.
- Streamlit dashboard.
- Configurable watchlist.
- CSV and HTML signal reports.
- Paper event logging.
- Signal history table and trend view.
- Simulated tokenized market metrics.

## v0.2.0: Real tokenized market data

Goal: replace simulated tokenized market metrics with provider-based market data.

Planned work:

- Evaluate tokenized equity data providers.
- Add provider configuration with safe local credential handling.
- Pull tokenized bid, ask, last price, volume, and liquidity data.
- Preserve raw market snapshots for auditability.
- Clearly label stale, missing, or low-confidence market data.

## v0.3.0: Signal quality and backtesting

Goal: make the signal engine measurable instead of merely descriptive.

Planned work:

- Add historical signal replay.
- Track signal outcomes over defined time windows.
- Add hit rate, average return, drawdown, and false positive metrics.
- Compare signal performance by symbol, category, and signal type.
- Separate scoring weights into a documented configuration section.

## v0.4.0: Dashboard and research workflow

Goal: make the tool easier for researchers and finance professionals to use.

Planned work:

- Add dashboard pages for signal performance, symbol detail, and market data quality.
- Add exportable research summaries.
- Add user-editable scoring assumptions.
- Add clearer explanation of each signal component.
- Add visual indicators for liquidity, spread risk, and premium/discount behavior.

## v0.5.0: Production hardening

Goal: improve reliability, test coverage, and public contributor readiness.

Planned work:

- Add automated tests for core scoring logic.
- Add GitHub Actions checks.
- Add typed interfaces for market data inputs.
- Add error handling for provider downtime and malformed market data.
- Add sample datasets that do not expose personal or proprietary information.

## Future research areas

- Multi-provider tokenized equity data comparison.
- Arbitrage alerting research without automated execution.
- Stablecoin settlement implications.
- After-hours dislocation studies.
- Liquidity risk scoring.
- Regulatory and market structure notes.

## Non-goals for the current phase

The current project will not include live trade execution, brokerage integration, exchange account integration, or automated order placement. Those features should not be considered until the research signal quality, data integrity, and risk controls are substantially more mature.
