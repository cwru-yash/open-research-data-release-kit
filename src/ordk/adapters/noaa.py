import json
from datetime import datetime
from io import StringIO
from pathlib import Path

import polars as pl
import requests

from ordk.schema import CanonicalRecord


NOAA_DAILY_VARIABLES = {
    "TMAX": {"unit": "C", "scale": 0.1},
    "TMIN": {"unit": "C", "scale": 0.1},
    "PRCP": {"unit": "mm", "scale": 0.1},
}

NOAA_ACCESS_DATA_URL = "https://www.ncei.noaa.gov/access/services/data/v1"


def fetch_daily_summary(
    station: str,
    start_date: str,
    end_date: str,
    session: requests.Session | None = None,
) -> pl.DataFrame:
    client = session if session is not None else requests

    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": ",".join(NOAA_DAILY_VARIABLES.keys()),
        "format": "csv",
        "units": "metric",
        "includeAttributes": "false",
    }

    response = client.get(NOAA_ACCESS_DATA_URL, params=params, timeout=30)
    response.raise_for_status()

    columns = ["STATION", "DATE", *NOAA_DAILY_VARIABLES.keys()]

    return pl.read_csv(StringIO(response.text), columns=columns)


def normalize_daily_summary(df: pl.DataFrame) -> list[CanonicalRecord]:
    records: list[CanonicalRecord] = []

    for row in df.iter_rows(named=True):
        station = row["STATION"]
        observed_at = datetime.fromisoformat(str(row["DATE"]))

        for variable, spec in NOAA_DAILY_VARIABLES.items():
            raw_value = row.get(variable)
            if raw_value is None:
                continue

            value = float(raw_value) * spec["scale"]

            records.append(
                CanonicalRecord(
                    source="NOAA/NCEI",
                    domain="climate",
                    dataset_id="daily-summaries",
                    record_id=f"{station}-{row['DATE']}-{variable}",
                    observed_at=observed_at,
                    variable=variable,
                    value=value,
                    unit=spec["unit"],
                    quality_flag=None,
                    location_or_instrument=station,
                    metadata={
                        "raw_column": variable,
                        "raw_value": raw_value,
                    },
                )
            )

    return records


def read_daily_summary_csv(path: str | Path) -> pl.DataFrame:
    columns = ["STATION", "DATE", *NOAA_DAILY_VARIABLES.keys()]
    return pl.read_csv(path, columns=columns)


def records_to_dataframe(records: list[CanonicalRecord]) -> pl.DataFrame:
    rows = []

    for record in records:
        row = record.model_dump(mode="json")
        row["metadata"] = json.dumps(row["metadata"], sort_keys=True)
        rows.append(row)

    return pl.DataFrame(rows)


def write_release_csv(df: pl.DataFrame, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.write_csv(output_path)

    return output_path
