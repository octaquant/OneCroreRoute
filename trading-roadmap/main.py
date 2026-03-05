"""Entry point for trading roadmap and growth simulator."""

from __future__ import annotations

import argparse
from pathlib import Path

from charts import generate_charts
from growth_simulator import (
    SimulationConfig,
    TradingGrowthSimulator,
    console_snapshot,
    export_reports,
)
from risk_management import RiskRules


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Professional trading growth roadmap simulator")
    parser.add_argument("--initial-capital", type=float, default=100000)
    parser.add_argument("--target-capital", type=float, default=10000000)
    parser.add_argument("--daily-return-target", type=float, default=None, help="Decimal format (e.g., 0.012)")
    parser.add_argument("--risk-per-trade", type=float, default=0.02)
    parser.add_argument("--max-daily-loss", type=float, default=0.03)
    parser.add_argument("--number-of-trading-days", type=int, default=365)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--no-excel", action="store_true", help="Disable optional Excel export")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = SimulationConfig(
        initial_capital=args.initial_capital,
        target_capital=args.target_capital,
        daily_return_target=args.daily_return_target,
        risk_per_trade=args.risk_per_trade,
        max_daily_loss=args.max_daily_loss,
        number_of_trading_days=args.number_of_trading_days,
    )
    risk_rules = RiskRules(
        risk_per_trade=args.risk_per_trade,
        max_daily_loss=args.max_daily_loss,
        min_risk_reward=2,
        max_trades_per_day=3,
        stop_after_daily_target=True,
    )

    simulator = TradingGrowthSimulator(config=config, risk_rules=risk_rules)
    reports = simulator.run()

    required_daily = config.required_daily_return() * 100
    print(f"Required daily compounded return to reach target: {required_daily:.4f}%")
    print(
        "Risk rules: 1-2% max risk/trade, 3% max daily loss, min 1:2 R:R, max 3 trades/day, stop at limit/target"
    )
    print(console_snapshot(reports))

    output_dir, excel_path = export_reports(reports, args.output_dir, excel=not args.no_excel)
    generate_charts(reports["daily"], reports["monthly"], args.output_dir)

    print(f"\nCSV reports exported to: {output_dir.resolve()}")
    if excel_path:
        print(f"Excel report exported to: {excel_path.resolve()}")
    print("Charts exported (capital growth, monthly performance, drawdown, compounding curve).")


if __name__ == "__main__":
    main()
