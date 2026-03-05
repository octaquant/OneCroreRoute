"""Chart generation for trading roadmap outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def generate_charts(daily: pd.DataFrame, monthly: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    _capital_growth_curve(daily, out_dir / "capital_growth_curve.png")
    _monthly_performance_chart(monthly, out_dir / "monthly_performance_chart.png")
    _drawdown_chart(daily, out_dir / "drawdown_chart.png")
    _compounding_curve(daily, out_dir / "compounding_curve.png")


def _capital_growth_curve(daily: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(daily["Day"], daily["Ending Capital"], color="#1f77b4", linewidth=2)
    plt.title("Capital Growth Curve")
    plt.xlabel("Day")
    plt.ylabel("Capital (₹)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def _monthly_performance_chart(monthly: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(monthly["Month"], monthly["Monthly_growth_%"], color="#2ca02c")
    plt.title("Monthly Performance (Growth %)")
    plt.xlabel("Month")
    plt.ylabel("Growth %")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def _drawdown_chart(daily: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(daily["Day"], daily["Drawdown %"], color="#d62728")
    plt.fill_between(daily["Day"], daily["Drawdown %"], 0, color="#d62728", alpha=0.2)
    plt.title("Drawdown Chart")
    plt.xlabel("Day")
    plt.ylabel("Drawdown %")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def _compounding_curve(daily: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.semilogy(daily["Day"], daily["Ending Capital"], color="#9467bd", linewidth=2)
    plt.title("Compounding Curve (Log Scale)")
    plt.xlabel("Day")
    plt.ylabel("Capital (₹, log scale)")
    plt.grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()
