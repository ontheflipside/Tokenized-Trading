# Agent Design

## Objective

Build a practical tokenized equity strategy agent that can identify pricing, liquidity, and demand dislocations between tokenized stocks and their underlying equities.

## Version one strategy

The first version is an alerting agent. It does not trade live. It scores market conditions and creates a paper trading log.

## Core signals

### 1. Premium or discount

```text
(tokenized price - underlying equity price) / underlying equity price
```

This identifies whether the tokenized version is trading rich or cheap.

### 2. Order book imbalance

```text
(bid depth - ask depth) / (bid depth + ask depth)
```

Positive imbalance means buyers are providing more depth than sellers near the current price. Negative imbalance means the opposite.

### 3. Liquidity depth

Measures how much dollar value sits within 1 percent of the midpoint price.

### 4. Spread

Measures the cost of entering and exiting.

## Monetization path

Phase one is an internal research system. Phase two is a paid signal product. Phase three is an advisory product. Phase four is strategy licensing or managed capital only after a documented performance record exists.

## Future modules

1. Dune on chain wallet flow tracking.
2. xStocks mint and burn monitoring.
3. Reddit and X sentiment scoring.
4. Macro volatility filter.
5. Earnings calendar awareness.
6. Sector rotation model.
7. Automated alerting through email or Teams.
8. Streamlit dashboard.
9. Backtesting engine.
10. Live execution with human confirmation.
