import unittest

import pandas as pd

import scripts.check_data_quality as dq


class TestDataQualityScript(unittest.TestCase):
    def test_main_passes_for_clean_dataset(self):
        df = pd.DataFrame({
            "Draw_Date": ["2020-01-01"],
            "Day_of_Week": ["Wednesday"],
            "Month": [1],
            "Prize_1": ["123456"],
            "Last_2": ["56"],
            "First_3": [""],
            "Last_3": ["123,456"],
            "Source_URL": ["unit-test"],
        })
        status, lines = dq.validate_dataframe(df)
        self.assertEqual(status, 0)
        self.assertIn("Rows: 1", lines)

    def test_main_fails_for_invalid_numbers(self):
        df = pd.DataFrame({
            "Draw_Date": ["2020-01-01"],
            "Day_of_Week": ["Wednesday"],
            "Month": [1],
            "Prize_1": ["12345"],
            "Last_2": ["x6"],
            "First_3": [""],
            "Last_3": [""],
            "Source_URL": ["unit-test"],
        })
        status, lines = dq.validate_dataframe(df)
        self.assertEqual(status, 1)
        self.assertIn("Invalid Last_2 rows: 1", lines)
        self.assertIn("Invalid Prize_1 rows: 1", lines)


if __name__ == "__main__":
    unittest.main()
