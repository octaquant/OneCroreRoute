"""Risk management utilities for the trading growth simulator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskRules:
    """Professional trading discipline constraints used by the simulator."""

    risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03
    min_risk_reward: float = 2.0
    max_trades_per_day: int = 3
    stop_after_daily_target: bool = True

    def validate(self) -> None:
        if not (0 < self.risk_per_trade <= 0.02):
            raise ValueError("risk_per_trade must be between 0 and 0.02 (1-2% recommended)")
        if not (0 < self.max_daily_loss <= 0.05):
            raise ValueError("max_daily_loss must be between 0 and 0.05")
        if self.min_risk_reward < 2:
            raise ValueError("min_risk_reward must be at least 2.0")
        if not (1 <= self.max_trades_per_day <= 10):
            raise ValueError("max_trades_per_day should be between 1 and 10")


def max_risk_allowed(capital: float, risk_per_trade: float) -> float:
    """Absolute max rupee risk per trade under the selected percent rule."""
    return capital * risk_per_trade


def daily_loss_limit(capital: float, max_daily_loss: float) -> float:
    """Absolute max rupee loss allowed per day under discipline rules."""
    return capital * max_daily_loss
