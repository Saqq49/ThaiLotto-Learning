import unittest
import pandas as pd
from lotto.walk_forward import walk_forward_validate

class TestWalkForward(unittest.TestCase):
    def setUp(self):
        # 10 draws
        self.df = pd.DataFrame({
            "Draw_Date": pd.to_datetime([f"2020-01-{i:02d}" for i in range(1, 11)]),
            "Last_2": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        })

    def test_walk_forward_shape(self):
        # Train window 5. 
        # Total 10. 
        # Should test index 5, 6, 7, 8, 9 (5 draws).
        res = walk_forward_validate(self.df, train_window=5, top_n=3)
        self.assertEqual(len(res), 5 * 4) # 5 draws * 4 methods (Freq, Overdue, RW, Random)
        
        # Check first draw tested (index 5, which is 2020-01-06)
        first_draw = res[res["draw_date"] == "2020-01-06"]
        self.assertEqual(len(first_draw), 4)
        self.assertEqual(first_draw.iloc[0]["actual"], "06")

    def test_insufficient_data(self):
        res = walk_forward_validate(self.df, train_window=10)
        self.assertTrue(res.empty)

    def test_first_target_is_not_in_training_window(self):
        res = walk_forward_validate(self.df, train_window=5, top_n=10)
        first_rows = res[res["draw_date"] == "2020-01-06"]
        frequency_predicted = first_rows[first_rows["method"] == "Frequency"].iloc[0]["predicted"].split(",")
        self.assertEqual(first_rows.iloc[0]["actual"], "06")
        self.assertNotIn("06", frequency_predicted[:5])

    def test_result_contains_expected_methods(self):
        res = walk_forward_validate(self.df, train_window=5, top_n=3)
        self.assertEqual(set(res["method"]), {"Frequency", "Overdue", "Recency-Weighted", "Random"})
        self.assertTrue((res["top_n"] == 3).all())

if __name__ == "__main__":
    unittest.main()
