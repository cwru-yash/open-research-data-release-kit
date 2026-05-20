import polars as pl

from ordk.core.quality import summarize_quality


def test_summarize_quality_returns_release_metrics():
    df = pl.DataFrame(
        {
            "source": ["NOAA/NCEI", "NOAA/NCEI", "NOAA/NCEI"],
            "domain": ["climate", "climate", "climate"],
            "dataset_id": ["daily-summaries", "daily-summaries", "daily-summaries"],
            "record_id": [
                "USW00094728-2024-01-01-TMAX",
                "USW00094728-2024-01-01-TMIN",
                "USW00094728-2024-01-01-PRCP",
            ],
            "observed_at": [
                "2024-01-01T00:00:00",
                "2024-01-01T00:00:00",
                "2024-01-02T00:00:00",
            ],
            "variable": ["TMAX", "TMIN", "PRCP"],
            "value": [5.0, None, 1.0],
            "unit": ["C", "C", "mm"],
            "quality_flag": [None, None, None],
            "location_or_instrument": ["USW00094728", "USW00094728", "USW00094728"],
            "metadata": ["{}", "{}", "{}"],
        }
    )

    summary = summarize_quality(df)

    assert summary == {
        "row_count": 3,
        "variable_count": 3,
        "missing_value_count": 1,
        "min_observed_at": "2024-01-01T00:00:00",
        "max_observed_at": "2024-01-02T00:00:00",
        "source": "NOAA/NCEI",
        "domain": "climate",
        "dataset_id": "daily-summaries",
        "units_seen": ["C", "mm"],
    }
