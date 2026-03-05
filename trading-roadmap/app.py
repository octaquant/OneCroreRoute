"""Streamlit app for interactive trading roadmap dashboard."""

from __future__ import annotations

import streamlit as st

from charts import capital_growth_chart, drawdown_chart, monthly_performance_chart
from growth_simulator import SimulationConfig, TradingGrowthSimulator
from risk_management import RiskRules


st.set_page_config(page_title="Trading Roadmap Dashboard", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0E1117;
            color: #E6EDF3;
        }
        div[data-testid="metric-container"] {
            border: 1px solid #30363D;
            border-radius: 12px;
            padding: 10px;
            background: #161B22;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Trading Roadmap Dashboard")
st.caption("Theoretical compounding path from ₹1,00,000 to ₹1,00,00,000 in one year.")

with st.sidebar:
    st.header("Controls")
    initial_capital = st.number_input("Initial Capital", min_value=10_000, value=100_000, step=10_000)
    target_capital = st.number_input("Target Capital", min_value=100_000, value=10_000_000, step=100_000)
    trading_days = st.slider("Trading Days", min_value=100, max_value=365, value=252)
    use_manual = st.toggle("Set Daily Return % manually", value=False)
    manual_daily_return = st.slider("Daily Return %", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    risk_per_trade_pct = st.slider("Risk per trade %", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

config = SimulationConfig(
    initial_capital=float(initial_capital),
    target_capital=float(target_capital),
    trading_days=int(trading_days),
    daily_return=(manual_daily_return / 100) if use_manual else None,
    risk_per_trade=risk_per_trade_pct / 100,
)
risk_rules = RiskRules(risk_per_trade=risk_per_trade_pct / 100)
simulator = TradingGrowthSimulator(config, risk_rules)
reports = simulator.run()

daily_df = reports["daily"]
weekly_df = reports["weekly"]
monthly_df = reports["monthly"]

required_daily_return = config.required_daily_return() * 100

st.subheader("1) Overview Panel")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Starting Capital", f"₹{initial_capital:,.0f}")
col2.metric("Target Capital", f"₹{target_capital:,.0f}")
col3.metric("Required Daily Return %", f"{required_daily_return:.2f}%")
col4.metric("Total Trading Days", f"{trading_days}")

st.subheader("2) Capital Growth Chart")
st.plotly_chart(capital_growth_chart(daily_df), use_container_width=True)

st.subheader("3) Daily Progress Table")
daily_table = daily_df[["Day", "Starting Capital", "Daily Profit", "Ending Capital", "Risk Limit (2%)"]]
st.dataframe(daily_table, use_container_width=True)
st.download_button(
    "Export Daily Progress CSV",
    daily_table.to_csv(index=False).encode("utf-8"),
    file_name="daily_progress.csv",
    mime="text/csv",
)

st.subheader("4) Weekly Summary")
st.dataframe(weekly_df, use_container_width=True)
st.download_button(
    "Export Weekly Summary CSV",
    weekly_df.to_csv(index=False).encode("utf-8"),
    file_name="weekly_summary.csv",
    mime="text/csv",
)

st.subheader("5) Monthly Summary")
monthly_view = monthly_df[["Month", "Opening Capital", "Monthly Profit", "Ending Capital"]]
st.dataframe(monthly_view, use_container_width=True)
st.download_button(
    "Export Monthly Summary CSV",
    monthly_view.to_csv(index=False).encode("utf-8"),
    file_name="monthly_summary.csv",
    mime="text/csv",
)

st.subheader("6) Risk Dashboard")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Max risk per trade", f"{risk_per_trade_pct:.1f}%")
r2.metric("Daily loss limit", "3%")
r3.metric("Risk Reward Ratio", "1:2")
r4.metric("Maximum trades per day", "3")

st.subheader("7) Charts")
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(monthly_performance_chart(monthly_df), use_container_width=True)
with chart_col2:
    st.plotly_chart(drawdown_chart(daily_df), use_container_width=True)

st.info(
    "Educational simulation only. Real trading outcomes vary and can include significant losses.",
    icon="⚠️",
)
