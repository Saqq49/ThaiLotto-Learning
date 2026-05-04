import unittest
import pandas as pd
from lotto.backtest import PRIZE_PAYOUTS, TICKET_PRICE, run_backtest

class TestBacktest(unittest.TestCase):
    def setUp(self):
        # 5 draws, all have Last_2 = "01"
        self.df = pd.DataFrame({
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16", "2020-02-01", "2020-02-16", "2020-03-01"]),
            "Last_2": ["01", "01", "01", "01", "01"]
        })

    def test_fixed_strategy_win(self):
        # Buying "01" every draw, 1 ticket each.
        # Cost 80, Payout 2000, PnL 1920.
        # 5 draws * 1920 = 9600 profit.
        res = run_backtest(self.df, strategy="fixed", target_numbers=["01"], initial_capital=1000)
        self.assertEqual(len(res.records), 5)
        self.assertEqual(res.win_rate, 1.0)
        self.assertEqual(res.total_payout, 10000)
        self.assertEqual(res.total_spent, 400)
        self.assertEqual(res.net_pnl, 9600)
        self.assertEqual(res.final_equity, 10600)

    def test_fixed_strategy_loss(self):
        res = run_backtest(self.df, strategy="fixed", target_numbers=["02"], initial_capital=1000)
        self.assertEqual(res.win_rate, 0.0)
        self.assertEqual(res.total_payout, 0)
        self.assertEqual(res.total_spent, 400)
        self.assertEqual(res.net_pnl, -400)

    def test_bankruptcy(self):
        # Capital 50, but cost is 80. Should bankrupt immediately.
        res = run_backtest(self.df, strategy="fixed", target_numbers=["02"], initial_capital=50)
        self.assertTrue(res.bankrupt)
        self.assertEqual(res.final_equity, 0)
        self.assertEqual(len(res.records), 1)

    def test_official_last2_payout_constant(self):
        self.assertEqual(TICKET_PRICE, 80)
        self.assertEqual(PRIZE_PAYOUTS["Last_2"], 2000)

    def test_multi_number_strategy_spends_each_number(self):
        res = run_backtest(
            self.df.head(1),
            strategy="fixed",
            target_numbers=["01", "02", "03"],
            initial_capital=1000,
        )
        self.assertEqual(res.total_spent, 240)
        self.assertEqual(res.total_payout, 2000)
        self.assertEqual(res.net_pnl, 1760)
        self.assertEqual(res.records[0].numbers_bet, ["01", "02", "03"])

    def test_martingale_doubles_after_loss_and_resets_after_win(self):
        df = pd.DataFrame({
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16", "2020-02-01"]),
            "Last_2": ["99", "99", "01"],
        })
        res = run_backtest(df, strategy="martingale", target_numbers=["01"], initial_capital=10000)
        self.assertEqual([r.bet_per_number for r in res.records], [80, 160, 320])
        self.assertEqual(res.records[-1].gross_payout, 8000)
        self.assertEqual(res.longest_losing_streak, 2)

    def test_anti_martingale_doubles_after_win_and_resets_after_loss(self):
        df = pd.DataFrame({
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16", "2020-02-01"]),
            "Last_2": ["01", "01", "99"],
        })
        res = run_backtest(df, strategy="anti_martingale", target_numbers=["01"], initial_capital=10000)
        self.assertEqual([r.bet_per_number for r in res.records], [80, 160, 320])
        self.assertEqual(res.longest_losing_streak, 1)

    def test_random_strategy_is_reproducible_with_seed(self):
        res1 = run_backtest(self.df, strategy="random", target_numbers=["00", "01"], random_seed=7)
        res2 = run_backtest(self.df, strategy="random", target_numbers=["00", "01"], random_seed=7)
        self.assertEqual([r.numbers_bet for r in res1.records], [r.numbers_bet for r in res2.records])

if __name__ == "__main__":
    unittest.main()
