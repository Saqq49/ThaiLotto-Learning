import unittest
import pandas as pd
from lotto.predictors import frequency_predictor, overdue_predictor, recency_weighted_predictor, random_predictor

class TestPredictors(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "Last_2": ["01", "02", "01", "03", "01"]
        })

    def test_frequency_predictor(self):
        preds = frequency_predictor(self.df, top_n=1)
        # "01" appeared 3 times, others 1.
        self.assertEqual(preds[0][0], "01")

    def test_overdue_predictor(self):
        preds = overdue_predictor(self.df, top_n=1)
        # Numbers like "00", "04" to "99" never seen.
        # All have max gap of 5.
        # "00" is among the top results due to sorting.
        expected_candidates = [f"{i:02d}" for i in range(100) if f"{i:02d}" not in ["01", "02", "03"]]
        self.assertIn(preds[0][0], expected_candidates)

    def test_recency_weighted_predictor(self):
        # Weighted towards recent: "01" is most recent, "03" is second most.
        preds = recency_weighted_predictor(self.df, top_n=2)
        self.assertEqual(preds[0][0], "01")
        self.assertEqual(preds[1][0], "03")

    def test_frequency_predictor_returns_zero_padded_numbers(self):
        preds = frequency_predictor(pd.DataFrame({"Last_2": []}), top_n=3)
        self.assertEqual([num for num, _ in preds], ["00", "01", "02"])

    def test_random_predictor_has_unique_numbers_and_seeded_output(self):
        preds1 = random_predictor(top_n=10, seed=123)
        preds2 = random_predictor(top_n=10, seed=123)
        nums = [num for num, _ in preds1]
        self.assertEqual(preds1, preds2)
        self.assertEqual(len(nums), len(set(nums)))
        self.assertTrue(all(len(num) == 2 for num in nums))

if __name__ == "__main__":
    unittest.main()
