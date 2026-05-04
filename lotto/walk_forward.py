import pandas as pd
from lotto.predictors import frequency_predictor, overdue_predictor, recency_weighted_predictor, random_predictor


def walk_forward_validate(
    df: pd.DataFrame,
    train_window: int = 60,
    top_n: int = 5,
) -> pd.DataFrame:
    df = df.sort_values("Draw_Date").reset_index(drop=True)
    n = len(df)
    if n <= train_window:
        return pd.DataFrame()

    results = []
    for i in range(train_window, n):
        train = df.iloc[:i]
        actual = df.iloc[i]["Last_2"]
        draw_date = str(df.iloc[i]["Draw_Date"])[:10]

        for method_name, predictor in [
            ("Frequency", frequency_predictor),
            ("Overdue", overdue_predictor),
            ("Recency-Weighted", recency_weighted_predictor),
        ]:
            preds = predictor(train, top_n=top_n)
            predicted_nums = [p[0] for p in preds]
            hit = actual in predicted_nums
            results.append({
                "draw_date": draw_date,
                "method": method_name,
                "predicted": ",".join(predicted_nums),
                "actual": actual,
                "hit": hit,
                "top_n": top_n,
            })

        rand_preds = random_predictor(top_n=top_n, seed=i)
        rand_nums = [p[0] for p in rand_preds]
        results.append({
            "draw_date": draw_date,
            "method": "Random",
            "predicted": ",".join(rand_nums),
            "actual": actual,
            "hit": actual in rand_nums,
            "top_n": top_n,
        })

    return pd.DataFrame(results)
