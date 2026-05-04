from dataclasses import dataclass, field
from typing import Literal
import pandas as pd
import numpy as np

PrizeType = Literal["Last_2", "First_3", "Last_3", "Prize_1"]
Strategy = Literal["fixed", "martingale", "anti_martingale", "random"]

# Official Thai Government Lottery payouts per winning ticket (THB)
# Ticket price is officially 80 THB
PRIZE_PAYOUTS: dict[str, float] = {
    "Last_2": 2_000,       # 2,000 THB per winning ticket
    "First_3": 4_000,      # 4,000 THB per winning ticket
    "Last_3": 4_000,       # 4,000 THB per winning ticket
    "Prize_1": 6_000_000,  # 6,000,000 THB per winning ticket
}

TICKET_PRICE = 80  # THB per ticket


@dataclass
class BetRecord:
    draw_date: str
    numbers_bet: list[str]
    bet_per_number: float
    tickets_per_number: int
    actual: str
    won: bool
    gross_payout: float
    pnl: float
    equity: float


@dataclass
class BacktestResult:
    records: list[BetRecord] = field(default_factory=list)
    final_equity: float = 0.0
    net_pnl: float = 0.0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    longest_losing_streak: int = 0
    total_spent: float = 0.0
    total_payout: float = 0.0
    bankrupt: bool = False


def run_backtest(
    df: pd.DataFrame,
    prize_type: PrizeType = "Last_2",
    strategy: Strategy = "fixed",
    initial_capital: float = 10_000,
    base_bet: float = 80,
    tickets_per_number: int = 1,
    target_numbers: list[str] | None = None,
    max_stake_per_draw: float = 5_000,
    random_seed: int = 42,
) -> BacktestResult:
    df = df.sort_values("Draw_Date").reset_index(drop=True)
    rng = np.random.default_rng(random_seed)

    if target_numbers is None:
        target_numbers = ["07"]

    prize_per_ticket = PRIZE_PAYOUTS[prize_type]
    equity = initial_capital
    current_bet_per_num = base_bet
    records: list[BetRecord] = []
    streak = 0
    max_streak = 0
    peak_equity = initial_capital

    for _, row in df.iterrows():
        actual = str(row.get(prize_type, "")).strip()
        if not actual:
            continue

        if strategy == "random":
            # Pick 'n' random numbers where 'n' is len(target_numbers)
            num_to_pick = len(target_numbers)
            chosen_list = rng.choice([f"{i:02d}" for i in range(100)], size=num_to_pick, replace=False).tolist()
        else:
            chosen_list = target_numbers

        # Cost is (bet per number * tickets per number * count of numbers)
        # However, base_bet usually refers to the price of one ticket set (80 THB)
        # If strategy is martingale, current_bet_per_num doubles
        cost = current_bet_per_num * tickets_per_number * len(chosen_list)
        
        # Enforce max stake
        if cost > max_stake_per_draw:
            cost = max_stake_per_draw
            # Adjust current_bet_per_num for this draw only to fit max_stake
            # (Simplification: we just cap the total cost)

        if cost > equity:
            # Bankruptcy or insufficient funds to fulfill the strategy
            records.append(BetRecord(
                draw_date=str(row["Draw_Date"])[:10],
                numbers_bet=chosen_list, bet_per_number=current_bet_per_num,
                tickets_per_number=tickets_per_number, actual=actual,
                won=False, gross_payout=0, pnl=-equity, equity=0,
            ))
            equity = 0
            break

        # Check if ANY of chosen numbers hit ANY of the actual values
        actual_values = [v.strip() for v in actual.split(",")]
        winners = [c for c in chosen_list if c in actual_values]
        won = len(winners) > 0

        # Payout calculation: sum of payouts for each winning number
        # Note: If multiple numbers hit (rare for Last_2, possible for First_3), they all pay out.
        # actual_tickets_per_num assumes we spend current_bet_per_num on each number
        # If cost was capped, we proportionally reduce tickets.
        actual_total_tickets = int(cost / TICKET_PRICE)
        tickets_per_num_adj = actual_total_tickets / len(chosen_list) if len(chosen_list) > 0 else 0
        
        gross_payout = (prize_per_ticket * tickets_per_num_adj * len(winners)) if won else 0
        pnl = gross_payout - cost
        equity += pnl

        rec = BetRecord(
            draw_date=str(row["Draw_Date"])[:10],
            numbers_bet=chosen_list, bet_per_number=current_bet_per_num,
            tickets_per_number=tickets_per_number, actual=actual,
            won=won, gross_payout=gross_payout,
            pnl=pnl, equity=equity,
        )
        records.append(rec)

        if equity > peak_equity:
            peak_equity = equity

        if won:
            streak = 0
            if strategy == "anti_martingale":
                current_bet_per_num = min(current_bet_per_num * 2, max_stake_per_draw / (tickets_per_number * len(chosen_list)))
            else:
                current_bet_per_num = base_bet
        else:
            streak += 1
            max_streak = max(max_streak, streak)
            if strategy == "martingale":
                current_bet_per_num = min(current_bet_per_num * 2, max_stake_per_draw / (tickets_per_number * len(chosen_list)))
            elif strategy == "anti_martingale":
                current_bet_per_num = base_bet

    if not records:
        return BacktestResult()

    equities = [r.equity for r in records]
    peak = initial_capital
    max_dd = 0.0
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0
        max_dd = max(max_dd, dd)

    total_spent = sum((r.gross_payout - r.pnl) for r in records)
    total_payout = sum(r.gross_payout for r in records)
    wins = sum(1 for r in records if r.won)

    return BacktestResult(
        records=records,
        final_equity=equities[-1],
        net_pnl=equities[-1] - initial_capital,
        win_rate=wins / len(records) if records else 0,
        max_drawdown=max_dd,
        longest_losing_streak=max_streak,
        total_spent=total_spent,
        total_payout=total_payout,
        bankrupt=equities[-1] <= 0,
    )
