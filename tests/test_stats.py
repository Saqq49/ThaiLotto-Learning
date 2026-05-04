import unittest
import pandas as pd
import numpy as np
from lotto.stats import compute_last2_heatmap_matrix, get_hot_cold_numbers, compute_max_drawdown_per_number

class TestStats(unittest.TestCase):
    def test_heatmap_matrix(self):
        freq = pd.Series({"00": 5, "12": 3, "99": 10})
        matrix = compute_last2_heatmap_matrix(freq)
        self.assertEqual(matrix[0][0], 5)
        self.assertEqual(matrix[1][2], 3)
        self.assertEqual(matrix[9][9], 10)
        self.assertEqual(matrix[5][5], 0)

    def test_hot_cold_numbers(self):
        freq = pd.Series({f"{i:02d}": i for i in range(100)})
        hot, cold = get_hot_cold_numbers(freq, top_n=5)
        self.assertEqual(hot.index[0], "99")
        self.assertEqual(cold.index[0], "00")
        self.assertEqual(len(hot), 5)

    def test_max_drawdown(self):
        data = {
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16", "2020-02-01", "2020-02-16"]),
            "Last_2": ["01", "02", "01", "03"]
        }
        df = pd.DataFrame(data)
        dd = compute_max_drawdown_per_number(df)
        
        # Number "01" appeared at index 0 and 2. 
        # Gap between them is index 1 (size 1).
        # Current gap after index 2 is index 3 (size 1).
        row_01 = dd[dd["Number"] == "01"].iloc[0]
        self.assertEqual(row_01["Max_Gap"], 1)
        self.assertEqual(row_01["Current_Gap"], 1)
        self.assertEqual(row_01["Total_Appearances"], 2)

    def test_never_seen_number_uses_dataset_length_as_gap(self):
        df = pd.DataFrame({
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16"]),
            "Last_2": ["01", "02"],
        })
        dd = compute_max_drawdown_per_number(df)
        row_99 = dd[dd["Number"] == "99"].iloc[0]
        self.assertEqual(row_99["Max_Gap"], 2)
        self.assertEqual(row_99["Current_Gap"], 2)
        self.assertEqual(row_99["Total_Appearances"], 0)

if __name__ == "__main__":
    unittest.main()
