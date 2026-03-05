"""Core capital compounding simulator and reporting tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from risk_management import RiskRules, daily_loss_limit, max_risk_allowed


@dataclass
class SimulationConfig:
    initial_capital: float = 100_000
    target_capital: float = 10_000_000
    trading_days: int = 252
    daily_return: float | None = None
    risk_per_trade: float = 0.02
    daily_loss_limit_pct: float = 0.03

    def required_daily_return(self) -> float:
        return (self.target_capital / self.initial_capital) ** (1 / self.trading_days) - 1


class TradingGrowthSimulator:
    def __init__(self, config: SimulationConfig, risk_rules: RiskRules):
        self.config = config
        self.risk_rules = risk_rules
        self.risk_rules.validate()

        if self.config.daily_return is None:
            self.config.daily_return = self.config.required_daily_return()

    def run(self) -> Dict[str, pd.DataFrame]:
        daily = self._daily_progress()
        weekly = self._weekly_summary(daily)
        monthly = self._monthly_summary(daily)
        return {"daily": daily, "weekly": weekly, "monthly": monthly}

    def analytics(self, daily_df: pd.DataFrame) -> Dict[str, float | str]:
        max_drawdown = abs(float(daily_df["Drawdown %"].min()))
        gross_profit = float(daily_df.loc[daily_df["Daily Profit"] > 0, "Daily Profit"].sum())
        gross_loss = abs(float(daily_df.loc[daily_df["Daily Profit"] < 0, "Daily Profit"].sum()))
        profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

        return {
            "Maximum Drawdown": max_drawdown,
            "Risk per Trade": self.risk_rules.risk_per_trade * 100,
            "Daily Loss Limit": self.risk_rules.max_daily_loss * 100,
            "Risk-Reward Ratio": self.risk_rules.risk_reward_ratio,
            "Profit Factor": "∞" if profit_factor == float("inf") else round(profit_factor, 2),
        }

    def _daily_progress(self) -> pd.DataFrame:
        rows = []
        ending_capital = self.config.initial_capital
        running_peak = ending_capital

        for day in range(1, self.config.trading_days + 1):
            starting_capital = ending_capital
            daily_profit = starting_capital * self.config.daily_return
            ending_capital = starting_capital + daily_profit

            running_peak = max(running_peak, ending_capital)
            drawdown_pct = ((ending_capital - running_peak) / running_peak) * 100

            rows.append(
                {
                    "Day": day,
                    "Starting Capital": starting_capital,
                    "Daily Profit": daily_profit,
                    "Ending Capital": ending_capital,
                    "Risk Limit (2%)": max_risk_allowed(starting_capital, self.config.risk_per_trade),
                    "Daily Loss Limit": daily_loss_limit(starting_capital, self.config.daily_loss_limit_pct),
                    "Drawdown %": drawdown_pct,
                    "Daily Return %": self.config.daily_return * 100,
                }
            )

        return pd.DataFrame(rows)

    def _weekly_summary(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        data = daily_df.copy()
        data["Week Number"] = ((data["Day"] - 1) // 5) + 1

        weekly = (
            data.groupby("Week Number", as_index=False)
            .agg(
                **{
                    "Opening Balance": ("Starting Capital", "first"),
                    "Weekly Profit": ("Daily Profit", "sum"),
                    "Ending Balance": ("Ending Capital", "last"),
                }
            )
        )
        return weekly

    def _monthly_summary(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        data = daily_df.copy()
        data["Month"] = ((data["Day"] - 1) // 21) + 1

        monthly = (
            data.groupby("Month", as_index=False)
            .agg(
                **{
                    "Opening Capital": ("Starting Capital", "first"),
                    "Monthly Profit": ("Daily Profit", "sum"),
                    "Ending Capital": ("Ending Capital", "last"),
                    "Max Drawdown %": ("Drawdown %", "min"),
                }
            )
        )
        monthly["Month"] = monthly["Month"].apply(lambda month: f"Month {month}")
        return monthly
