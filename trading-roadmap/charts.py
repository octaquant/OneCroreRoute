"""Plotly chart builders for the trading dashboard."""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def capital_growth_chart(daily_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_df["Day"],
            y=daily_df["Ending Capital"],
            mode="lines",
            name="Ending Capital",
            line={"color": "#00D4FF", "width": 3},
        )
    )
    fig.update_layout(
        title="Capital Growth Curve",
        xaxis_title="Trading Day",
        yaxis_title="Capital (₹)",
        template="plotly_dark",
        hovermode="x unified",
    )
    return fig


def monthly_performance_chart(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_df["Month"],
            y=monthly_df["Monthly Profit"],
            name="Monthly Profit",
            marker_color="#00E676",
        )
    )
    fig.update_layout(
        title="Monthly Performance",
        xaxis_title="Month",
        yaxis_title="Profit (₹)",
        template="plotly_dark",
    )
    return fig


def drawdown_chart(daily_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_df["Day"],
            y=daily_df["Drawdown %"],
            mode="lines",
            name="Drawdown %",
            line={"color": "#FF5252", "width": 2},
            fill="tozeroy",
        )
    )
    fig.update_layout(
        title="Drawdown Chart",
        xaxis_title="Trading Day",
        yaxis_title="Drawdown %",
        template="plotly_dark",
    )
    return fig
