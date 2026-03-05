"""Premium Streamlit app for Trading Roadmap Pro."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from charts import capital_growth_chart, drawdown_chart, monthly_performance_chart
from growth_simulator import SimulationConfig, TradingGrowthSimulator
from risk_management import RiskRules

st.set_page_config(page_title="Trading Roadmap Pro", page_icon="💹", layout="wide")

JOURNEY_FILE = Path(__file__).with_name("journey_tracker_data.json")
JOURNEY_INITIAL_CAPITAL = 100_000.0
JOURNEY_TARGET_CAPITAL = 10_000_000.0


def load_journey_state() -> dict:
    if not JOURNEY_FILE.exists():
        return {"started": False, "history": []}
    try:
        return json.loads(JOURNEY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"started": False, "history": []}


def save_journey_state(state: dict) -> None:
    JOURNEY_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def build_day_record(day_number: int, starting_capital: float, daily_target_return: float) -> dict:
    target_profit = starting_capital * daily_target_return
    return {
        "day": day_number,
        "date": date.today().isoformat(),
        "starting_capital": round(starting_capital, 2),
        "target_profit": round(target_profit, 2),
        "target_capital": round(starting_capital + target_profit, 2),
        "actual_profit": None,
        "ending_capital": None,
    }

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        .stApp {
            background: radial-gradient(circle at 15% 15%, #111827 0%, #0b0f19 55%, #060913 100%);
            color: #e5e7eb;
            font-family: 'Inter', sans-serif;
        }
        #MainMenu,
        header,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0;
            position: fixed;
        }
        .stApp > header {
            display: none;
        }
        [data-testid="stAppViewContainer"] {
            padding-top: 0;
            margin-top: 0;
        }
        .block-container {
            padding-top: 0;
            margin-top: 0;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(11,15,25,0.95));
            border-right: 1px solid rgba(59,130,246,0.2);
        }
        .hero-card, .glass-card {
            background: rgba(17, 24, 39, 0.65);
            border: 1px solid rgba(0, 245, 212, 0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
            backdrop-filter: blur(10px);
            border-radius: 18px;
            padding: 1rem 1.2rem;
            transition: all 0.3s ease;
        }
        .hero-card:hover, .glass-card:hover {
            transform: translateY(-3px);
            border-color: rgba(0,245,212,0.6);
            box-shadow: 0 0 20px rgba(0,245,212,0.2);
        }
        .hero-title {font-size: 2.1rem; font-weight: 800; margin: 0;}
        .hero-sub {margin: .2rem 0 0 0; color: #94a3b8;}
        .live-badge {
            display: inline-block;
            margin-top: .6rem;
            padding: .25rem .7rem;
            border-radius: 999px;
            border: 1px solid rgba(0,245,212,0.8);
            color: #00f5d4;
            font-size: .78rem;
            letter-spacing: .08em;
            font-weight: 700;
            animation: pulse 1.8s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0,245,212,0.5); }
            100% { box-shadow: 0 0 0 14px rgba(0,245,212,0); }
        }
        .kpi {
            background: rgba(17,24,39,0.65);
            border: 1px solid rgba(59,130,246,0.35);
            border-radius: 16px;
            padding: .8rem 1rem;
            min-height: 120px;
            transition: all .25s ease;
        }
        .kpi:hover { box-shadow: 0 0 18px rgba(59,130,246,0.35); transform: translateY(-3px); }
        .kpi-icon {font-size: 1.2rem;}
        .kpi-value {font-size: 1.5rem; font-weight: 700; margin: .3rem 0;}
        .kpi-label {font-size: .8rem; color: #94a3b8;}
        .section-title {font-size: 1.2rem; font-weight: 700; margin: .3rem 0 .7rem 0;}
        .metric-box {border-left: 3px solid #00f5d4;}
        .warn-card {border: 1px solid rgba(251,113,133,0.5); background: rgba(127,29,29,0.22);}
        .rule-item {margin: .35rem 0;}
        .scroll-table {max-height: 380px; overflow-y: auto; border-radius: 14px; border: 1px solid rgba(59,130,246,0.3);}
        table {width: 100%; border-collapse: collapse; font-size: .9rem;}
        th {position: sticky; top: 0; background: #111827; z-index: 2;}
        th, td {padding: .65rem; text-align: left; border-bottom: 1px solid rgba(148,163,184,0.15);}
        tr:nth-child(even) {background: rgba(30,41,59,0.38);}
        tr:nth-child(odd) {background: rgba(15,23,42,0.3);}
        .timeline-step {padding: .7rem .9rem; border-left: 3px solid #3b82f6; margin: .6rem 0; background: rgba(17,24,39,0.6); border-radius: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Simulation Controls")
    initial_capital = st.number_input("Initial Capital", min_value=10_000, value=100_000, step=10_000)
    target_capital = st.number_input("Target Capital", min_value=100_000, value=10_000_000, step=100_000)
    daily_return_pct = st.slider("Daily Return %", min_value=0.1, max_value=5.0, value=1.85, step=0.05)
    trading_days = st.slider("Trading Days", min_value=100, max_value=365, value=252)
    risk_per_trade_pct = st.slider("Risk per Trade %", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

config = SimulationConfig(
    initial_capital=float(initial_capital),
    target_capital=float(target_capital),
    trading_days=int(trading_days),
    daily_return=daily_return_pct / 100,
    risk_per_trade=risk_per_trade_pct / 100,
)
risk_rules = RiskRules(risk_per_trade=risk_per_trade_pct / 100)
simulator = TradingGrowthSimulator(config, risk_rules)
reports = simulator.run()
daily_df = reports["daily"]
monthly_df = reports["monthly"]
analytics = simulator.analytics(daily_df)

st.markdown(
    """
    <div class="hero-card">
        <p class="hero-title">💠 Trading Roadmap Pro</p>
        <p class="hero-sub">Premium compounding intelligence dashboard built for disciplined traders.</p>
        <span class="live-badge">LIVE SIMULATION</span>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi_cols = st.columns(4)
kpis = [
    ("💰", f"₹{initial_capital:,.0f}", "Starting Capital"),
    ("🎯", f"₹{target_capital:,.0f}", "Target Capital"),
    ("📈", f"{config.required_daily_return() * 100:.2f}%", "Required Daily Return"),
    ("🗓️", f"{trading_days}", "Total Trading Days"),
]
for col, (icon, value, label) in zip(kpi_cols, kpis):
    col.markdown(
        f"<div class='kpi'><div class='kpi-icon'>{icon}</div><div class='kpi-value'>{value}</div><div class='kpi-label'>{label}</div></div>",
        unsafe_allow_html=True,
    )

main_tab, discipline_tab = st.tabs(["📊 Dashboard", "🧭 Trading Discipline Guide"])

with main_tab:
    st.markdown("<p class='section-title'>🚀 Start Your Trading Journey</p>", unsafe_allow_html=True)

    if "journey_state" not in st.session_state:
        st.session_state.journey_state = load_journey_state()

    journey_state = st.session_state.journey_state
    journey_state.setdefault("started", False)
    journey_state.setdefault("history", [])

    if st.button("Start My ₹1L → ₹1Cr Journey", use_container_width=True):
        daily_target_return = daily_return_pct / 100
        day_one = build_day_record(1, JOURNEY_INITIAL_CAPITAL, daily_target_return)
        journey_state = {
            "started": True,
            "start_date": date.today().isoformat(),
            "daily_target_return": daily_target_return,
            "target_capital": JOURNEY_TARGET_CAPITAL,
            "history": [day_one],
            "current_day": 1,
            "current_capital": JOURNEY_INITIAL_CAPITAL,
        }
        st.session_state.journey_state = journey_state
        save_journey_state(journey_state)

    if journey_state["started"] and journey_state["history"]:
        current_day_data = journey_state["history"][-1]
        current_capital = float(journey_state["current_capital"])
        remaining_target = max(float(journey_state["target_capital"]) - current_capital, 0)
        completion_pct = min((current_capital / JOURNEY_TARGET_CAPITAL) * 100, 100.0)

        st.progress(completion_pct / 100)
        st.caption(f"Journey Progress: ₹1,00,000 → ₹1,00,00,000 ({completion_pct:.2f}% complete)")

        day_cols = st.columns(4)
        day_cols[0].markdown(
            f"<div class='glass-card'><div class='kpi-label'>Current Day</div><div class='kpi-value'>Day {current_day_data['day']}</div></div>",
            unsafe_allow_html=True,
        )
        day_cols[1].markdown(
            f"<div class='glass-card'><div class='kpi-label'>Current Capital</div><div class='kpi-value'>₹{current_capital:,.0f}</div></div>",
            unsafe_allow_html=True,
        )
        day_cols[2].markdown(
            f"<div class='glass-card'><div class='kpi-label'>Today's Profit Target</div><div class='kpi-value'>₹{current_day_data['target_profit']:,.0f}</div></div>",
            unsafe_allow_html=True,
        )
        day_cols[3].markdown(
            f"<div class='glass-card'><div class='kpi-label'>Remaining Target</div><div class='kpi-value'>₹{remaining_target:,.0f}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class='glass-card'>
                <div class='rule-item'><strong>Day {current_day_data['day']}</strong></div>
                <div class='rule-item'>Starting Capital: ₹{current_day_data['starting_capital']:,.0f}</div>
                <div class='rule-item'>Today's Profit Target: ₹{current_day_data['target_profit']:,.0f}</div>
                <div class='rule-item'>Today's Target Capital: ₹{current_day_data['target_capital']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("journey_update_form", clear_on_submit=True):
            today_result = st.number_input("Today's Profit / Loss", value=0.0, step=100.0)
            submitted = st.form_submit_button("Update Today's Result", use_container_width=True)

        if submitted:
            active_day = journey_state["history"][-1]
            ending_capital = max(active_day["starting_capital"] + today_result, 0)
            active_day["actual_profit"] = round(today_result, 2)
            active_day["ending_capital"] = round(ending_capital, 2)

            next_day = active_day["day"] + 1
            next_record = build_day_record(next_day, ending_capital, journey_state["daily_target_return"])
            journey_state["history"].append(next_record)
            journey_state["current_day"] = next_day
            journey_state["current_capital"] = round(ending_capital, 2)

            st.session_state.journey_state = journey_state
            save_journey_state(journey_state)
            st.success("Journey updated. Stay consistent and execute your plan.")
            st.rerun()

        timeline_df = pd.DataFrame(journey_state["history"])
        timeline_df["profit"] = timeline_df["actual_profit"].fillna(0)
        timeline_df["capital"] = timeline_df["ending_capital"].fillna(timeline_df["starting_capital"])
        timeline_display = timeline_df[["day", "capital", "profit", "target_capital"]].copy()
        timeline_display.columns = ["Day", "Capital", "Profit", "Target"]
        timeline_display["Capital"] = timeline_display["Capital"].map(lambda x: f"₹{x:,.0f}")
        timeline_display["Profit"] = timeline_display["Profit"].map(lambda x: f"₹{x:,.0f}")
        timeline_display["Target"] = timeline_display["Target"].map(lambda x: f"₹{x:,.0f}")
        st.markdown("<p class='section-title'>Trading Journey Timeline</p>", unsafe_allow_html=True)
        st.dataframe(timeline_display, use_container_width=True, hide_index=True)

        viz_col_1, viz_col_2 = st.columns(2)
        with viz_col_1:
            capital_fig = px.line(timeline_df, x="day", y="capital", markers=True, title="Capital Growth")
            capital_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.4)")
            st.plotly_chart(capital_fig, use_container_width=True)
        with viz_col_2:
            remaining_df = timeline_df.copy()
            remaining_df["remaining"] = JOURNEY_TARGET_CAPITAL - remaining_df["capital"]
            remaining_fig = px.area(remaining_df, x="day", y="remaining", title="Remaining Distance to ₹1Cr")
            remaining_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.4)")
            st.plotly_chart(remaining_fig, use_container_width=True)

        gauge_fig = px.bar(
            x=["Progress to ₹1Cr", "Remaining"],
            y=[current_capital, max(JOURNEY_TARGET_CAPITAL - current_capital, 0)],
            color=["Progress to ₹1Cr", "Remaining"],
            title="Goal Completion Split",
        )
        gauge_fig.update_layout(showlegend=False, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.4)")
        st.plotly_chart(gauge_fig, use_container_width=True)

        motivation_quotes = [
            "Consistency beats luck.",
            "Protect capital first.",
            "Follow your trading plan.",
        ]
        quote = motivation_quotes[current_day_data["day"] % len(motivation_quotes)]
        rule_text = "".join(
            [
                "<div class='rule-item'>Max risk per trade: 2%</div>",
                "<div class='rule-item'>Max daily loss: 3%</div>",
                "<div class='rule-item'>Maximum trades: 3</div>",
                "<div class='rule-item'>Risk reward: 1:2</div>",
            ]
        )
        panel_left, panel_right = st.columns(2)
        panel_left.markdown(
            f"<div class='glass-card'><div class='section-title'>Motivation Panel</div><div class='rule-item'>✨ {quote}</div></div>",
            unsafe_allow_html=True,
        )
        panel_right.markdown(
            f"<div class='glass-card warn-card'><div class='section-title'>Discipline Reminder</div>{rule_text}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='glass-card'><div class='rule-item'>Click the start button to begin tracking your real journey from ₹1,00,000 to ₹1,00,00,000.</div></div>",
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(capital_growth_chart(daily_df), use_container_width=True)
    with c2:
        st.plotly_chart(monthly_performance_chart(monthly_df), use_container_width=True)

    st.markdown("<p class='section-title'>Professional Analytics</p>", unsafe_allow_html=True)
    metric_cols = st.columns(5)
    metrics = [
        ("Maximum Drawdown", f"{analytics['Maximum Drawdown']:.2f}%"),
        ("Risk per Trade", f"{analytics['Risk per Trade']:.1f}%"),
        ("Daily Loss Limit", f"{analytics['Daily Loss Limit']:.1f}%"),
        ("Risk-Reward Ratio", f"{analytics['Risk-Reward Ratio']}"),
        ("Profit Factor", f"{analytics['Profit Factor']}"),
    ]
    for col, (label, value) in zip(metric_cols, metrics):
        col.markdown(
            f"<div class='glass-card metric-box'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>",
            unsafe_allow_html=True,
        )

    st.plotly_chart(drawdown_chart(daily_df), use_container_width=True)

    display_table = daily_df[["Day", "Starting Capital", "Daily Profit", "Ending Capital"]].copy()
    display_table["Starting Capital"] = display_table["Starting Capital"].map(lambda x: f"₹{x:,.0f}")
    display_table["Daily Profit"] = display_table["Daily Profit"].map(lambda x: f"₹{x:,.0f}")
    display_table["Ending Capital"] = display_table["Ending Capital"].map(lambda x: f"₹{x:,.0f}")
    st.markdown("<p class='section-title'>Execution Ledger</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='scroll-table'>{display_table.to_html(index=False, escape=False)}</div>", unsafe_allow_html=True)

with discipline_tab:
    st.markdown("<p class='section-title'>Trader Discipline & Execution Playbook</p>", unsafe_allow_html=True)

    premarket_items = [
        "Check overall market trend",
        "Mark support and resistance levels",
        "Identify high-volume zones",
        "Check important news events",
        "Define risk per trade",
        "Define maximum daily loss",
    ]
    during_trade_rules = [
        "Always use stop loss",
        "Follow predefined risk",
        "Never move stop loss emotionally",
        "Avoid overtrading",
        "Follow planned entry only",
        "Limit maximum trades per day",
    ]
    avoid_list = [
        "Revenge trading",
        "Over-leveraging",
        "Trading without a plan",
        "FOMO entries",
        "Doubling position after losses",
        "Ignoring stop loss",
    ]

    col_a, col_b = st.columns(2)
    with col_a:
        checklist_html = "".join([f"<div class='rule-item'>☑️ {item}</div>" for item in premarket_items])
        st.markdown(f"<div class='glass-card'><div class='section-title'>1) Pre-Market Checklist</div>{checklist_html}</div>", unsafe_allow_html=True)

        rules_html = "".join([f"<div class='rule-item'>📌 {item}</div>" for item in during_trade_rules])
        st.markdown(f"<div class='glass-card'><div class='section-title'>2) During Trade Rules</div>{rules_html}</div>", unsafe_allow_html=True)

    with col_b:
        warning_html = "".join([f"<div class='rule-item'>🚫 {item}</div>" for item in avoid_list])
        st.markdown(f"<div class='glass-card warn-card'><div class='section-title'>3) What Traders Should NOT Do</div>{warning_html}</div>", unsafe_allow_html=True)

        rm_cols = st.columns(2)
        framework = [
            ("Risk / Trade", "1-2%"),
            ("Daily Loss", "3-5%"),
            ("R:R", "Min 1:2"),
            ("Max Trades", "3"),
            ("Priority", "Capital Preservation"),
        ]
        for idx, (k, v) in enumerate(framework):
            rm_cols[idx % 2].markdown(
                f"<div class='glass-card'><div class='kpi-label'>{k}</div><div class='kpi-value'>{v}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='section-title'>5) Trading Routine</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='timeline-step'><strong>🌅 Morning:</strong> Market analysis, level marking, watchlist preparation.</div>
        <div class='timeline-step'><strong>🕒 Trading Session:</strong> Execute planned setups, follow risk rules, avoid emotional trades.</div>
        <div class='timeline-step'><strong>🌙 Evening:</strong> Review trades, journal performance, improve strategy.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='glass-card'>
            <div class='section-title'>6) Trader Psychology</div>
            <div class='rule-item'>🧠 Patience wins over impulse.</div>
            <div class='rule-item'>🔁 Consistency compounds results.</div>
            <div class='rule-item'>⚖️ Avoid greed; protect downside.</div>
            <div class='rule-item'>✅ Accept losses as business expenses.</div>
            <div class='rule-item'>🎯 Focus on process quality, not short-term profits.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("Educational simulation only. Real trading outcomes vary and can include significant losses.", icon="⚠️")
