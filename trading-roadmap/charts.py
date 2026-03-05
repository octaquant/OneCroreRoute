"""Plotly chart builders for the Trading Roadmap Pro dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


PLOT_BG = "rgba(17, 24, 39, 0.65)"
PAPER_BG = "rgba(0,0,0,0)"
TEXT_COLOR = "#e5e7eb"
GRID_COLOR = "rgba(148, 163, 184, 0.15)"


def _base_layout(fig: go.Figure, title: str, xaxis_title: str, yaxis_title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font={"family": "Inter, Segoe UI, sans-serif", "color": TEXT_COLOR},
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
        hovermode="x unified",
        transition={"duration": 700, "easing": "cubic-in-out"},
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig


def capital_growth_chart(daily_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_df["Day"],
            y=daily_df["Ending Capital"],
            mode="lines",
            name="Ending Capital",
            line={"color": "#00f5d4", "width": 4, "shape": "spline", "smoothing": 1.2},
            fill="tozeroy",
            fillcolor="rgba(0, 245, 212, 0.12)",
            hovertemplate="Day %{x}<br>Capital ₹%{y:,.0f}<extra></extra>",
        )
    )
    return _base_layout(fig, "Capital Growth Curve", "Trading Day", "Capital (₹)")


def monthly_performance_chart(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_df["Month"],
            y=monthly_df["Monthly Profit"],
            name="Monthly Profit",
            marker={
                "color": monthly_df["Monthly Profit"],
                "colorscale": [[0, "#3b82f6"], [1, "#00f5d4"]],
                "line": {"color": "rgba(255,255,255,0.2)", "width": 1},
            },
            hovertemplate="%{x}<br>Profit ₹%{y:,.0f}<extra></extra>",
        )
    )
    return _base_layout(fig, "Monthly Performance", "Month", "Profit (₹)")


def drawdown_chart(daily_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_df["Day"],
            y=daily_df["Drawdown %"],
            mode="lines",
            name="Drawdown",
            line={"color": "#fb7185", "width": 3, "shape": "spline", "smoothing": 1.2},
            fill="tozeroy",
            fillcolor="rgba(251, 113, 133, 0.18)",
            hovertemplate="Day %{x}<br>Drawdown %{y:.2f}%<extra></extra>",
        )
    )
    return _base_layout(fig, "Drawdown Monitoring", "Trading Day", "Drawdown %")
