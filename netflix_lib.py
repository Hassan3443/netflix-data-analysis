"""Cleaning and aggregation helpers for the Netflix titles dataset.

Kept free of plotting and file output so they can be unit tested.
"""
from __future__ import annotations

import re

import pandas as pd

LIST_COLUMNS = {"director": "directors", "cast": "cast", "country": "countries", "listed_in": "genres"}


def split_list(value) -> list[str]:
    """'A, B ,C' -> ['A', 'B', 'C']. Missing or empty values give []."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def clean_titles(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return a cleaned copy and a report of every fix that was applied."""
    df = raw.copy()
    report = {"rows": len(df), "duplicate_show_ids": int(df["show_id"].duplicated().sum())}

    # 3 rows have the duration in the rating column and an empty duration.
    shifted = df["rating"].fillna("").str.fullmatch(r"\d+ min") & df["duration"].isna()
    report["rating_duration_shifted"] = int(shifted.sum())
    df.loc[shifted, "duration"] = df.loc[shifted, "rating"]
    df.loc[shifted, "rating"] = pd.NA

    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), format="%B %d, %Y", errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    report["missing_date_added"] = int(df["date_added"].isna().sum())

    dur = df["duration"].fillna("").str.extract(r"(\d+)\s*(min|Seasons?)")
    df["duration_value"] = pd.to_numeric(dur[0], errors="coerce").astype("Int64")
    df["duration_unit"] = dur[1].str.replace("Seasons", "Season")
    report["missing_duration"] = int(df["duration_value"].isna().sum())

    for col, new in LIST_COLUMNS.items():
        df[new] = df[col].map(split_list)
    for col in ("director", "country", "rating"):
        report[f"missing_{col}"] = int(df[col].isna().sum())
    return df, report


def top_counts(df: pd.DataFrame, list_col: str, n: int = 10) -> pd.Series:
    """Count each item once per title for a list column such as genres."""
    return df[list_col].explode().dropna().value_counts().head(n)


def titles_added_per_year(df: pd.DataFrame) -> pd.DataFrame:
    """Titles added to the service per year, split by type (rows with a date only)."""
    return df.dropna(subset=["year_added"]).groupby(["year_added", "type"]).size().unstack(fill_value=0)


def movie_duration_stats(df: pd.DataFrame) -> dict:
    mins = df.loc[(df["type"] == "Movie") & (df["duration_unit"] == "min"), "duration_value"].dropna().astype(int)
    return {"count": int(len(mins)), "median": float(mins.median()), "mean": round(float(mins.mean()), 1),
            "min": int(mins.min()), "max": int(mins.max())}


def show_seasons(df: pd.DataFrame) -> pd.Series:
    s = df.loc[(df["type"] == "TV Show") & (df["duration_unit"] == "Season"), "duration_value"].dropna().astype(int)
    return s.value_counts().sort_index()


def explorer_rows(df: pd.DataFrame) -> list[list]:
    """Compact rows for the web explorer. Column order matches COLUMNS in docs/app.js."""
    rows = []
    for r in df.itertuples():
        rows.append([
            r.title, 0 if r.type == "Movie" else 1, int(r.release_year),
            None if pd.isna(r.year_added) else int(r.year_added),
            r.rating if isinstance(r.rating, str) else None,
            None if pd.isna(r.duration_value) else int(r.duration_value),
            r.countries, r.genres, r.directors[:2],
        ])
    return rows
