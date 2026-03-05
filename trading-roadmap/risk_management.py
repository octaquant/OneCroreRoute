"""Risk management utilities for the trading dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskRules:
    risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03
    risk_reward_ratio: str = "1:2"
    max_trades_per_day: int = 3

    def validate(self) -> None:
        if not (0 < self.risk_per_trade <= 0.05):
            raise ValueError("risk_per_trade must be between 0 and 0.05")
        if not (0 < self.max_daily_loss <= 0.1):
            raise ValueError("max_daily_loss must be between 0 and 0.10")
        if self.max_trades_per_day < 1:
            raise ValueError("max_trades_per_day must be at least 1")


def max_risk_allowed(capital: float, risk_per_trade: float) -> float:
    return capital * risk_per_trade


def daily_loss_limit(capital: float, max_daily_loss: float) -> float:
    return capital * max_daily_loss
