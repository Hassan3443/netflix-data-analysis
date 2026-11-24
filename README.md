# Netflix Data Analysis

Exploratory analysis of the Netflix titles dataset (`netflix_titles.csv`, 8,807 titles up to 2021) with Python and pandas. It looks at the movie and TV show split, which countries produce the most titles, and how the catalog is spread across release years.

## Key findings

All numbers come from `netflix_data_analysis.py` and can be reproduced by running it.

- **Movies make up 69.6% of the catalog.** 6,131 movies and 2,676 TV shows.
- **The United States leads by a wide margin** with 3,690 titles, then India (1,046), the United Kingdom (806), Canada (445) and France (393).
- **Most titles are recent.** 70.6% were released in 2015 or later. Titles per release year rose from 352 in 2014 to a peak of 1,147 in 2018, then fell to 592 in 2021 (the dataset ends in 2021, so the last year is partial).

## Charts

| Movies vs TV shows | Top 10 countries |
|---|---|
| ![Movies vs TV shows](figures/movies_vs_tv_shows.png) | ![Top countries](figures/top_countries.png) |

![Titles by release year](figures/titles_by_release_year.png)

## Method and caveats

- A title can list several countries. Each country gets one count per title, so country totals add up to more than the number of titles.
- 831 titles (9.4%) have no country listed. They are left out of the country ranking and kept in the other charts.
- The release-year chart starts at 1990 so recent years are readable. The dataset goes back to 1925.
- The dataset has no duplicate `show_id` values. `director`, `cast` and `country` have the most missing values.

## Project structure

```
netflix_titles.csv           Dataset (8,807 rows)
netflix_data_analysis.py     Analysis, writes charts to figures/
figures/                     Generated charts
requirements.txt             pandas, matplotlib
```

## How to run

```bash
pip install -r requirements.txt
python netflix_data_analysis.py
```

## Tools

Python, pandas, Matplotlib.

## Author

Hassan Ashraf. [Portfolio](https://hassan3443.github.io/) | [LinkedIn](https://www.linkedin.com/in/hassan1000/)
