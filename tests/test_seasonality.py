import unittest

import pandas as pd

from lotto.seasonality import (
    DOW_ORDER,
    chi_squared_dow,
    chi_squared_monthly,
    compute_dow_distribution,
    compute_monthly_frequency,
    monthly_number_summary,
)


class TestSeasonality(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "Draw_Date": pd.to_datetime(["2020-01-01", "2020-01-16", "2020-02-01", "2020-02-16"]),
            "Month": [1, 1, 2, 2],
            "Day_of_Week": ["Wednesday", "Thursday", "Saturday", "Sunday"],
            "Last_2": ["01", "02", "01", "99"],
        })

    def test_monthly_frequency_has_all_months_and_numbers(self):
        result = compute_monthly_frequency(self.df)
        self.assertEqual(result.shape, (12, 100))
        self.assertEqual(result.loc[1, "01"], 1)
        self.assertEqual(result.loc[2, "01"], 1)
        self.assertEqual(result.loc[12, "99"], 0)

    def test_dow_distribution_preserves_order(self):
        result = compute_dow_distribution(self.df)
        self.assertEqual(result.index.tolist(), DOW_ORDER)
        self.assertEqual(result["Wednesday"], 1)
        self.assertEqual(result["Monday"], 0)

    def test_chi_squared_empty_data_is_safe(self):
        empty = pd.DataFrame({"Month": [], "Day_of_Week": [], "Last_2": []})
        self.assertEqual(chi_squared_monthly(empty), (0.0, 1.0))
        self.assertEqual(chi_squared_dow(empty), (0.0, 1.0))

    def test_monthly_number_summary(self):
        summary = monthly_number_summary(self.df, "01")
        jan = summary.iloc[0]
        feb = summary.iloc[1]
        self.assertEqual(jan["Draws"], 2)
        self.assertEqual(jan["Hits"], 1)
        self.assertEqual(jan["Rate_%"], 50.0)
        self.assertEqual(feb["Hits"], 1)


if __name__ == "__main__":
    unittest.main()
