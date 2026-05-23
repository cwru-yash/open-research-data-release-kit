import json
from datetime import datetime
from pathlib import Path

import polars as pl

from ordk.schema import CanonicalRecord


OMNI_TIME_COLUMN = "timestamp"
OMNI_VARIABLES = {
    "BZ_GSM": {"unit": "nT"},
    "FLOW_SPEED": {"unit": "km/s"},
    "PROTON_DENSITY": {"unit": "1/cm^3"},
}


def read_omni_csv(path: str | Path) -> pl.DataFrame:
    df = pl.read_csv(path)
    columns = [OMNI_TIME_COLUMN, *OMNI_VARIABLES.keys()]

    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required NASA OMNI columns: {missing}")

    return df.select(columns)


def normalize_omni(df: pl.DataFrame) -> list[CanonicalRecord]:
    records: list[CanonicalRecord] = []

    for row in df.iter_rows(named=True):
        observed_at = _parse_timestamp(row[OMNI_TIME_COLUMN])

        for variable, spec in OMNI_VARIABLES.items():
            raw_value = row.get(variable)
            if raw_value is None:
                continue

            records.append(
                CanonicalRecord(
                    source="NASA/SPDF",
                    domain="space_physics",
                    dataset_id="omni",
                    record_id=f"omni-{row[OMNI_TIME_COLUMN]}-{variable}",
                    observed_at=observed_at,
                    variable=variable,
                    value=float(raw_value),
                    unit=spec["unit"],
                    quality_flag=None,
                    location_or_instrument="OMNI",
                    metadata={
                        "raw_column": variable,
                        "raw_value": raw_value,
                    },
                )
            )

    return records


def records_to_dataframe(records: list[CanonicalRecord]) -> pl.DataFrame:
    rows = []

    for record in records:
        row = record.model_dump(mode="json")
        row["metadata"] = json.dumps(row["metadata"], sort_keys=True)
        rows.append(row)

    return pl.DataFrame(rows)


def _parse_timestamp(value: object) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"

    return datetime.fromisoformat(text)
