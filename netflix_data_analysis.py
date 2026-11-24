"""Exploratory analysis of the Netflix titles dataset.

Run:  python netflix_data_analysis.py
Writes charts to figures/ and prints the numbers used in the README.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

raw = pd.read_csv(HERE / "netflix_titles.csv")
print(f"Titles: {len(raw):,}  |  duplicate show_ids: {raw['show_id'].duplicated().sum()}")
print("Missing values per column:\n", raw.isna().sum()[raw.isna().sum() > 0].to_string())

# ---- Movies vs TV shows (all titles) -------------------------------------
types = raw["type"].value_counts()
print("\nTitles by type:\n", types.to_string())
print(f"Movie share: {types['Movie'] / types.sum():.1%}")

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(types.index, types.values, color=["#E50914", "#564d4d"])
ax.bar_label(bars, fmt="{:,.0f}")
ax.set_title("Movies vs TV shows", fontsize=14, weight="bold")
ax.set_ylabel("Titles")
fig.tight_layout()
fig.savefig(FIG / "movies_vs_tv_shows.png", dpi=150)
plt.close(fig)

# ---- Top countries ---------------------------------------------------------
# A title can list several countries; each country counts once per title.
# Titles with no country listed are left out of this part.
with_country = raw.dropna(subset=["country"]).copy()
print(f"\nTitles with a country listed: {len(with_country):,} ({len(raw) - len(with_country):,} without)")
countries = (
    with_country.assign(country=with_country["country"].str.split(","))
    .explode("country")
    .assign(country=lambda d: d["country"].str.strip())
)
countries = countries[countries["country"] != ""]
top = countries["country"].value_counts().head(10)
print("\nTop 10 countries (titles):\n", top.to_string())

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top.index[::-1], top.values[::-1], color="#E50914")
ax.bar_label(bars, fmt="{:,.0f}", padding=3)
ax.set_title("Top 10 countries by number of titles", fontsize=14, weight="bold")
ax.set_xlabel("Titles")
fig.tight_layout()
fig.savefig(FIG / "top_countries.png", dpi=150)
plt.close(fig)

# ---- Titles by release year ------------------------------------------------
per_year = raw["release_year"].value_counts().sort_index()
peak_year = per_year.idxmax()
print(f"\nRelease years: {per_year.index.min()} to {per_year.index.max()}")
print(f"Peak release year: {peak_year} ({per_year.max():,} titles)")
print(f"Titles released 2015 or later: {(raw['release_year'] >= 2015).mean():.1%}")

fig, ax = plt.subplots(figsize=(10, 6))
per_year[per_year.index >= 1990].plot(ax=ax, color="#E50914", linewidth=2)
ax.set_title("Titles by release year (1990 onward)", fontsize=14, weight="bold")
ax.set_xlabel("Release year")
ax.set_ylabel("Titles")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "titles_by_release_year.png", dpi=150)
plt.close(fig)
print("\nCharts saved to figures/")
