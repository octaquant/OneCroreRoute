# Trading Roadmap: ₹1 Lakh to ₹1 Crore (Theoretical Simulator)

This project provides a **professional financial roadmap and trading growth simulator** to evaluate whether capital can theoretically compound from **₹100,000** to **₹10,000,000** within **365 days**.

> ⚠️ This is a mathematical discipline model, not a promise of outcomes. Real markets are volatile and uncertain.

## Project structure

```text
trading-roadmap/
├── main.py
├── growth_simulator.py
├── risk_management.py
├── charts.py
├── data/
├── output/
└── README.md
```

## Compounding math

To compute required daily compounded return:

\[
\text{required daily return} = \left(\frac{\text{target capital}}{\text{initial capital}}\right)^{1/N} - 1
\]

For this roadmap:

- Initial capital = ₹100,000
- Target capital = ₹10,000,000
- Trading days (N) = 365

So the simulator calculates the daily rate required to multiply capital by 100× in one year.

## Professional trading discipline rules included

- Maximum risk per trade: **1–2%** of capital
- Maximum daily loss: **3%**
- Minimum risk:reward ratio: **1:2**
- Maximum trades per day: **3**
- Stop trading after hitting daily loss limit or daily target

## Outputs generated

The simulator exports:

1. **Daily progression table**
   - Day
   - Starting Capital
   - Daily Return %
   - Profit/Loss
   - Ending Capital
   - Max Risk Allowed (2% rule)

2. **Weekly summary**
   - Week number
   - Opening balance
   - Weekly profit
   - Weekly growth %
   - Ending balance

3. **Monthly summary**
   - Month
   - Opening capital
   - Total monthly profit
   - Monthly growth %
   - Ending capital
   - Drawdown statistics

4. **Year-end projection**
   - Initial capital
   - Projected year-end capital
   - Total profit
   - Total growth %
   - Target hit (True/False)

5. **Charts**
   - Capital growth curve
   - Monthly performance chart
   - Drawdown chart
   - Compounding curve (log scale)

## Run the simulator

Install dependencies:

```bash
pip install pandas numpy matplotlib openpyxl
```

Run with defaults:

```bash
cd trading-roadmap
python main.py
```

Run with custom parameters:

```bash
python main.py \
  --initial-capital 100000 \
  --target-capital 10000000 \
  --number-of-trading-days 365 \
  --daily-return-target 0.0127 \
  --risk-per-trade 0.02 \
  --max-daily-loss 0.03
```

## Customizable parameters

- `initial_capital`
- `daily_return_target` (optional: computed automatically if omitted)
- `risk_per_trade`
- `max_daily_loss`
- `number_of_trading_days`

## Export formats

- Clean console tables
- CSV export (`output/*_summary.csv`)
- Optional Excel export (`output/trading_growth_report.xlsx`)
- Optional dashboard view can be built using these CSV outputs (e.g., Streamlit/Power BI)

## Realistic vs unrealistic perspective

- **Mathematically possible**: yes, if a stable daily edge is achieved and losses are strictly controlled.
- **Practically difficult**: extremely. Consistent daily returns with low drawdowns over 365 sessions is rare.
- **Use case**: planning, discipline modeling, and scenario analysis—not guaranteed performance forecasting.

## Disclaimer

This repository is for educational and analytical purposes only and is not investment advice.
