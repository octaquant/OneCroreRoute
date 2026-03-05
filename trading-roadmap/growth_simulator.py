"""Core capital compounding simulator and reporting tables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from risk_management import RiskRules, daily_loss_limit, max_risk_allowed


@dataclass
class SimulationConfig:
    initial_capital: float = 100_000
    target_capital: float = 10_000_000
    number_of_trading_days: int = 365
    daily_return_target: float | None = None
    risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03

    def required_daily_return(self) -> float:
        """Return daily compounded rate needed to hit target in N days."""
        return (self.target_capital / self.initial_capital) ** (1 / self.number_of_trading_days) - 1


class TradingGrowthSimulator:
    def __init__(self, config: SimulationConfig, risk_rules: RiskRules):
        self.config = config
        self.risk_rules = risk_rules
        self.risk_rules.validate()

        if self.config.daily_return_target is None:
            self.config.daily_return_target = self.config.required_daily_return()

    def run(self) -> Dict[str, pd.DataFrame]:
        daily_df = self._daily_projection()
        weekly_df = self._weekly_summary(daily_df)
        monthly_df = self._monthly_summary(daily_df)
        year_end_df = self._year_end_projection(daily_df)

        return {
            "daily": daily_df,
            "weekly": weekly_df,
            "monthly": monthly_df,
            "year_end": year_end_df,
        }

    def _daily_projection(self) -> pd.DataFrame:
        records = []
        ending_capital = self.config.initial_capital
        peak_capital = ending_capital

        for day in range(1, self.config.number_of_trading_days + 1):
            start_capital = ending_capital
            profit_loss = start_capital * self.config.daily_return_target
            ending_capital = start_capital + profit_loss

            peak_capital = max(peak_capital, ending_capital)
            drawdown_pct = ((ending_capital - peak_capital) / peak_capital) * 100 if peak_capital else 0

            records.append(
                {
                    "Day": day,
                    "Starting Capital": start_capital,
                    "Daily Return %": self.config.daily_return_target * 100,
                    "Profit/Loss": profit_loss,
                    "Ending Capital": ending_capital,
                    "Max Risk Allowed (2% rule)": max_risk_allowed(start_capital, self.config.risk_per_trade),
                    "Max Daily Loss (3% rule)": daily_loss_limit(start_capital, self.config.max_daily_loss),
                    "Drawdown %": drawdown_pct,
                }
            )

        return pd.DataFrame(records)

    def _weekly_summary(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        data = daily_df.copy()
        data["Week"] = ((data["Day"] - 1) // 7) + 1

        weekly = (
            data.groupby("Week", as_index=False)
            .agg(
                Opening_balance=("Starting Capital", "first"),
                Weekly_profit=("Profit/Loss", "sum"),
                Ending_balance=("Ending Capital", "last"),
            )
        )
        weekly["Weekly_growth_%"] = (weekly["Ending_balance"] / weekly["Opening_balance"] - 1) * 100
        return weekly.rename(columns={"Week": "Week number"})

    def _monthly_summary(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        data = daily_df.copy()
        data["Month"] = ((data["Day"] - 1) // 30) + 1

        monthly = (
            data.groupby("Month", as_index=False)
            .agg(
                Opening_capital=("Starting Capital", "first"),
                Total_monthly_profit=("Profit/Loss", "sum"),
                Ending_capital=("Ending Capital", "last"),
                Worst_drawdown_pct=("Drawdown %", "min"),
            )
        )
        monthly["Monthly_growth_%"] = (monthly["Ending_capital"] / monthly["Opening_capital"] - 1) * 100

        monthly["Drawdown statistics"] = monthly["Worst_drawdown_pct"].apply(
            lambda x: f"Worst peak-to-trough: {x:.2f}%"
        )

        return monthly[
            [
                "Month",
                "Opening_capital",
                "Total_monthly_profit",
                "Monthly_growth_%",
                "Ending_capital",
                "Drawdown statistics",
            ]
        ]

    def _year_end_projection(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        start = self.config.initial_capital
        end = daily_df["Ending Capital"].iloc[-1]
        total_profit = end - start
        total_growth = (end / start - 1) * 100

        return pd.DataFrame(
            [
                {
                    "Initial Capital": start,
                    "Projected Year-End Capital": end,
                    "Total Profit": total_profit,
                    "Total Growth %": total_growth,
                    "Target Hit": end >= self.config.target_capital,
                }
            ]
        )


def export_reports(dataframes: Dict[str, pd.DataFrame], out_dir: Path, excel: bool = True) -> Tuple[Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, df in dataframes.items():
        df.to_csv(out_dir / f"{name}_summary.csv", index=False)

    excel_path = None
    if excel:
        excel_path = out_dir / "trading_growth_report.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for name, df in dataframes.items():
                df.to_excel(writer, sheet_name=name[:31], index=False)

    return out_dir, excel_path


def format_inr(value: float) -> str:
    return f"₹{value:,.2f}"


def console_snapshot(dataframes: Dict[str, pd.DataFrame]) -> str:
    daily_preview = dataframes["daily"].head(10)
    weekly_preview = dataframes["weekly"].head(8)
    monthly_preview = dataframes["monthly"]
    year_end = dataframes["year_end"]

    sections = [
        "\n=== DAILY PROGRESSION (first 10 rows) ===\n" + daily_preview.to_string(index=False),
        "\n=== WEEKLY SUMMARY (first 8 rows) ===\n" + weekly_preview.to_string(index=False),
        "\n=== MONTHLY SUMMARY ===\n" + monthly_preview.to_string(index=False),
        "\n=== YEAR-END PROJECTION ===\n" + year_end.to_string(index=False),
    ]
    return "\n".join(sections)
