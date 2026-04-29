import pandas as pd
import numpy as np

def add_relative_strength(df, index_df):
    df = df.copy()

    index_aligned = index_df.reindex(df.index).ffill()

    df["RS"] = df["Close"] / index_aligned["Close"]
    df["RS_MA"] = df["RS"].rolling(20).mean()

    return df

def calculate_score(df, i):

    row = df.iloc[i]

    trend = row["Close"] / row["EMA50"]
    volume = row["Volume"] / row["VOL_AVG20"]
    proximity = row["Close"] / row["52W_HIGH"]
    rs = row["RS"]

    score = (
        trend * 0.3 +
        volume * 0.25 +
        proximity * 0.2 +
        rs * 0.25
    )
    print(f" → score: {score}")
    return round(score, 3)
