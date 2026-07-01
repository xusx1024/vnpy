# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VeighNa (vnpy) is a Python-based quantitative trading framework (v4.3.0). It provides a full stack for building trading systems: market data gateways, order management, strategy engines, backtesting, and a PySide6 GUI. The 4.0 release added `vnpy.alpha`, an AI/ML pipeline for factor-based strategy research inspired by Microsoft Qlib.

## Build & Development Commands

```bash
# Install (core only)
pip install .

# Install with AI/ML dependencies
pip install ".[alpha]"

# Install with dev tooling (stubs, build tools)
pip install ".[dev]"

# Run tests
pytest tests/

# Lint with ruff
ruff check .

# Type check with mypy
mypy
```

Python version: >=3.10 (project is tested on 3.10–3.13). The build backend is hatchling.

## Architecture

### Event Engine (`vnpy/event/`)

The foundational layer. `EventEngine` runs two daemon threads: one dispatches `Event` objects from a `Queue` to registered handlers by type string, the other emits a timer event (`eTimer`) every N seconds. All inter-component communication in the system flows through events.

### Trader Core (`vnpy/trader/`)

- **`engine.py`** — `MainEngine` is the central orchestrator. It holds references to all gateways, engines, and apps. It boots `EventEngine`, then initializes `LogEngine` and `OmsEngine` (order management). `OmsEngine` listens to trade events and maintains in-memory caches of ticks, orders, trades, positions, accounts, contracts, and quotes — keyed by `vt_symbol` or `vt_*id`.
- **`gateway.py`** — `BaseGateway` is the ABC for connecting to broker/exchange APIs (CTP, XTP, IB, etc.). Implementations live in separate `vnpy_<name>` packages. Gateways emit typed events (`EVENT_TICK`, `EVENT_ORDER`, `EVENT_TRADE`, etc.) that `OmsEngine` consumes.
- **`object.py`** — `@dataclass` data objects: `TickData`, `BarData`, `OrderData`, `TradeData`, `PositionData`, `AccountData`, `ContractData`, `OrderRequest`, `CancelRequest`, `SubscribeRequest`, `HistoryRequest`. All inherit from `BaseData` which carries `gateway_name`.
- **`constant.py`** — Enums for trading domain: `Direction` (LONG/SHORT), `Offset` (OPEN/CLOSE/CLOSETODAY/CLOSEYESTERDAY), `Status`, `Product`, `OrderType`, `Exchange`, `Interval`.
- **`converter.py`** — `OffsetConverter` manages position offset logic for Chinese futures markets (distinguishing 今仓/昨仓, handling 平今/平昨).
- **`database.py`** — `BaseDatabase` ABC with pluggable backends (SQLite default, loaded dynamically via `vnpy_<dbname>` module). Stores/loads bar and tick data.
- **`app.py`** — `BaseApp` ABC. Apps (CTA strategy, spread trading, etc.) are modular plugins that bundle an engine class + a GUI widget.
- **`optimize.py`** — Genetic algorithm strategy parameter optimization using DEAP.
- **`ui/`** — PySide6 GUI: `MainWindow`, chart widgets, Qt helpers.

### Alpha / AI Research (`vnpy/alpha/`)

- **`lab.py`** — `AlphaLab` orchestrates the research workflow: manages parquet-based data storage (daily/minute bars), factor dataset generation, model training, signal generation, and backtesting.
- **`dataset/`** — Factor/feature engineering. `AlphaDataset` with a symbolic expression engine (`calculate_by_expression`) supporting cross-sectional (`cs_*`) and time-series (`ts_*`) operators. Built-in datasets: Alpha158 (158 factors from Qlib), Alpha101 (101 WorldQuant-style alphas).
- **`model/`** — `AlphaModel` template and concrete implementations: `LassoModel`, `LgbModel`, `MLPModel`. Uniform API: `fit()` / `predict()`.
- **`strategy/`** — `AlphaStrategy` template for converting ML signals into trading strategies. `BacktestingEngine` for simulation.

### RPC (`vnpy/rpc/`)

ZeroMQ-based RPC for distributed deployments. `RpcServer` exposes functions over REQ/REP + PUB/SUB sockets. `RpcClient` calls remote functions and subscribes to topics. Used to separate gateway processes from strategy processes.

### Chart (`vnpy/chart/`)

PyQtGraph-based charting: candlestick charts, bar charts, and indicator overlays. `ChartManager` manages multiple chart widgets.

## Key Patterns

- **Event-driven communication**: Gateways push data as events → `OmsEngine` caches them → strategy/app engines read from cache. Components never call each other directly; they emit and listen to events.
- **Plugin discovery**: Gateways (`vnpy_ctp`, `vnpy_ib`, etc.), databases (`vnpy_sqlite`, etc.), and apps are separate pip packages. They're imported by name convention and registered with `MainEngine.add_gateway()` / `add_app()`.
- **vt_symbol convention**: All instruments are identified by `"symbol.exchange"` strings (e.g., `"IF2406.CFFEX"`). Utility functions `extract_vt_symbol()` / `generate_vt_symbol()` handle parsing and construction.
- **i18n**: Strings are wrapped in `_()` (from `vnpy.trader.locale`) for Chinese/English translation. MO files are compiled during build via a hatch hook.

## Project Configuration

- `~/.vntrader/` — Runtime directory (created in home or CWD). Stores settings, JSON data files, and logs.
- `SETTINGS` dict in `vnpy.trader.setting` — Global configuration loaded from `~/.vntrader/vt_setting.json`.
- Ruff config for linting, mypy config for type checking are both in `pyproject.toml`.
