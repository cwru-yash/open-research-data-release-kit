import json

import polars as pl

from ordk.core.publish import publish_release


def test_publish_release_writes_release_artifacts(tmp_path):
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
            "value": [5.0, 3.2, 1.0],
            "unit": ["C", "C", "mm"],
            "quality_flag": [None, None, None],
            "location_or_instrument": ["USW00094728", "USW00094728", "USW00094728"],
            "metadata": ["{}", "{}", "{}"],
        }
    )

    output_dir = tmp_path / "noaa-release"

    artifacts = publish_release(df, output_dir)

    assert artifacts["normalized_csv"] == output_dir / "normalized.csv"
    assert artifacts["normalized_parquet"] == output_dir / "normalized.parquet"
    assert artifacts["metadata_json"] == output_dir / "metadata.json"
    assert artifacts["report_md"] == output_dir / "report.md"

    assert artifacts["normalized_csv"].exists()
    assert artifacts["normalized_parquet"].exists()
    assert artifacts["metadata_json"].exists()
    assert artifacts["report_md"].exists()

    metadata = json.loads(artifacts["metadata_json"].read_text())

    assert metadata["quality"]["row_count"] == 3
    assert metadata["quality"]["variable_count"] == 3
    assert metadata["quality"]["units_seen"] == ["C", "mm"]

    report = artifacts["report_md"].read_text()

    assert "# Research Data Release Report" in report
    assert "NOAA/NCEI" in report
    assert "daily-summaries" in report
