import polars as pl
from ordk.adapters.noaa import (
    fetch_daily_summary,
    normalize_daily_summary,
    records_to_dataframe,
    write_release_csv,
)


def test_normalize_daily_summary_maps_noaa_row_to_canonical_records():
    df = pl.DataFrame(
        {
            "STATION": ["USW00094728"],
            "DATE": ["2024-01-01"],
            "TMAX": [50],
            "TMIN": [32],
            "PRCP": [10],
        }
    )

    records = normalize_daily_summary(df)

    assert len(records) == 3
    assert {record.variable for record in records} == {"TMAX", "TMIN", "PRCP"}
    assert all(record.source == "NOAA/NCEI" for record in records)
    assert all(record.domain == "climate" for record in records)


def test_records_to_dataframe_returns_normalized_polars_dataframe():
    df = pl.DataFrame(
        {
            "STATION": ["USW00094728"],
            "DATE": ["2024-01-01"],
            "TMAX": [50],
            "TMIN": [32],
            "PRCP": [10],
        }
    )

    records = normalize_daily_summary(df)
    release_df = records_to_dataframe(records)

    assert release_df.shape == (3, 11)
    assert release_df.columns == [
        "source",
        "domain",
        "dataset_id",
        "record_id",
        "observed_at",
        "variable",
        "value",
        "unit",
        "quality_flag",
        "location_or_instrument",
        "metadata",
    ]

    tmax = release_df.filter(pl.col("variable") == "TMAX").row(0, named=True)

    assert tmax["source"] == "NOAA/NCEI"
    assert tmax["domain"] == "climate"
    assert tmax["value"] == 5.0
    assert tmax["unit"] == "C"


def test_write_release_csv_writes_normalized_artifact(tmp_path):
    df = pl.DataFrame(
        {
            "STATION": ["USW00094728"],
            "DATE": ["2024-01-01"],
            "TMAX": [50],
            "TMIN": [32],
            "PRCP": [10],
        }
    )

    records = normalize_daily_summary(df)
    release_df = records_to_dataframe(records)

    output_path = tmp_path / "releases" / "noaa_daily.csv"

    written_path = write_release_csv(release_df, output_path)

    assert written_path == output_path
    assert output_path.exists()

    loaded_df = pl.read_csv(output_path)

    assert loaded_df.shape == (3, 11)
    assert set(loaded_df["variable"].to_list()) == {"TMAX", "TMIN", "PRCP"}


class FakeNoaaResponse:
    text = "STATION,DATE,TMAX,TMIN,PRCP\nUSW00094728,2024-01-01,50,32,10\n"

    def raise_for_status(self):
        pass


class FakeNoaaSession:
    def __init__(self):
        self.url = None
        self.params = None
        self.timeout = None

    def get(self, url, params, timeout):
        self.url = url
        self.params = params
        self.timeout = timeout
        return FakeNoaaResponse()


def test_fetch_daily_summary_returns_polars_dataframe_from_api_response():
    session = FakeNoaaSession()

    df = fetch_daily_summary(
        station="USW00094728",
        start_date="2024-01-01",
        end_date="2024-01-01",
        session=session,
    )

    assert df.shape == (1, 5)
    assert df.columns == ["STATION", "DATE", "TMAX", "TMIN", "PRCP"]

    assert session.params["dataset"] == "daily-summaries"
    assert session.params["stations"] == "USW00094728"
    assert session.params["startDate"] == "2024-01-01"
    assert session.params["endDate"] == "2024-01-01"
    assert session.params["dataTypes"] == "TMAX,TMIN,PRCP"
    assert session.params["format"] == "csv"
