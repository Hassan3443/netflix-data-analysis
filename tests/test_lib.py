import pandas as pd

import netflix_lib as nl


def sample():
    return pd.DataFrame({
        "show_id": ["s1", "s2", "s3", "s4"],
        "type": ["Movie", "TV Show", "Movie", "Movie"],
        "title": ["A", "B", "C", "D"],
        "director": ["X, Y", None, "X", None],
        "cast": [None, "P, Q", None, None],
        "country": ["United States, India", "India", None, "United States"],
        "date_added": [" September 25, 2021", "January 1, 2020", None, "March 3, 2020"],
        "release_year": [2020, 2019, 2000, 2018],
        "rating": ["PG-13", "TV-MA", "74 min", "R"],
        "duration": ["90 min", "2 Seasons", None, "100 min"],
        "listed_in": ["Dramas, Comedies", "TV Dramas", "Dramas", "Comedies"],
        "description": ["", "", "", ""],
    })


def test_split_list_handles_missing_and_spaces():
    assert nl.split_list(" A , B,,C ") == ["A", "B", "C"]
    assert nl.split_list(None) == []
    assert nl.split_list(float("nan")) == []


def test_clean_fixes_shifted_rating_and_duration():
    df, report = nl.clean_titles(sample())
    row = df[df.show_id == "s3"].iloc[0]
    assert row["duration"] == "74 min" and pd.isna(row["rating"])
    assert report["rating_duration_shifted"] == 1


def test_clean_parses_dates_and_durations():
    df, report = nl.clean_titles(sample())
    assert df.loc[0, "year_added"] == 2021
    assert report["missing_date_added"] == 1
    assert df.loc[1, "duration_value"] == 2 and df.loc[1, "duration_unit"] == "Season"
    assert df.loc[3, "duration_value"] == 100 and df.loc[3, "duration_unit"] == "min"


def test_report_counts_missing_columns():
    _, report = nl.clean_titles(sample())
    assert report["missing_director"] == 2
    assert report["missing_country"] == 1
    assert report["duplicate_show_ids"] == 0


def test_top_counts_counts_each_item_once_per_title():
    df, _ = nl.clean_titles(sample())
    countries = nl.top_counts(df, "countries")
    assert countries["United States"] == 2 and countries["India"] == 2
    genres = nl.top_counts(df, "genres")
    assert genres["Dramas"] == 2 and genres["Comedies"] == 2


def test_titles_added_per_year_ignores_missing_dates():
    df, _ = nl.clean_titles(sample())
    per = nl.titles_added_per_year(df)
    assert per.loc[2020, "Movie"] == 1 and per.loc[2020, "TV Show"] == 1
    assert per.loc[2021, "Movie"] == 1
    assert per.to_numpy().sum() == 3


def test_movie_duration_stats_uses_minutes_only():
    df, _ = nl.clean_titles(sample())
    stats = nl.movie_duration_stats(df)
    assert stats == {"count": 3, "median": 90.0, "mean": 88.0, "min": 74, "max": 100}


def test_show_seasons():
    df, _ = nl.clean_titles(sample())
    assert nl.show_seasons(df).to_dict() == {2: 1}


def test_explorer_rows_shape():
    df, _ = nl.clean_titles(sample())
    rows = nl.explorer_rows(df)
    assert len(rows) == 4 and rows[0][:3] == ["A", 0, 2020]
    assert rows[0][6] == ["United States", "India"] and rows[0][8] == ["X", "Y"]
    assert rows[1][1] == 1
