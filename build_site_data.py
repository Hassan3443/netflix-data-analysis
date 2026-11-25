"""Writes docs/data.json (cleaned rows) and docs/summary.json (headline numbers).

Run:  python build_site_data.py
The web explorer in docs/ reads these files; every chart is computed from them.
"""
import json
from pathlib import Path

import pandas as pd

import netflix_lib as nl

HERE = Path(__file__).parent
DOCS = HERE / "docs"
DOCS.mkdir(exist_ok=True)

raw = pd.read_csv(HERE / "netflix_titles.csv")
df, report = nl.clean_titles(raw)

summary = {
    "cleaning_report": report,
    "titles": len(df),
    "movies": int((df["type"] == "Movie").sum()),
    "tv_shows": int((df["type"] == "TV Show").sum()),
    "top_genres": nl.top_counts(df, "genres", 10).to_dict(),
    "top_countries": nl.top_counts(df, "countries", 10).to_dict(),
    "top_directors": nl.top_counts(df, "directors", 10).to_dict(),
    "movie_duration": nl.movie_duration_stats(df),
    "tv_seasons": {int(k): int(v) for k, v in nl.show_seasons(df).items()},
    "added_per_year": {int(y): row.to_dict() for y, row in nl.titles_added_per_year(df).iterrows()},
    "ratings": df["rating"].value_counts().to_dict(),
}
(DOCS / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
(DOCS / "data.json").write_text(
    json.dumps({"columns": ["title", "type", "release_year", "year_added", "rating", "duration", "countries", "genres", "directors"],
                "rows": nl.explorer_rows(df)}, separators=(",", ":"), ensure_ascii=False),
    encoding="utf-8")
print(json.dumps(summary, indent=1)[:2500])
