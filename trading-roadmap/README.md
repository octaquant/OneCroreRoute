# Trading Roadmap Dashboard (Streamlit)

A professional interactive Streamlit dashboard that models a **theoretical compounding journey** from **₹1,00,000 to ₹1,00,00,000** within one year.

## Project Structure

```text
trading-roadmap/
├── app.py
├── growth_simulator.py
├── risk_management.py
├── charts.py
├── requirements.txt
└── README.md
```

## Features

- Overview panel (starting capital, target, required daily return, trading days)
- Interactive Plotly capital growth chart
- Daily progress table with risk limit (2%)
- Weekly and monthly summaries
- Professional risk dashboard metrics
- Monthly performance and drawdown charts
- Sidebar controls for simulation inputs
- CSV export for daily, weekly, and monthly tables
- Dark trading dashboard style with wide layout

## Install

```bash
cd trading-roadmap
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Disclaimer

This is an educational simulator for planning and analytics. It is **not** investment advice or a guarantee of returns.
