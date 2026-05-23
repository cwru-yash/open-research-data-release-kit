import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

from ordk.schema import CanonicalRecord


PTBXL_METADATA_COLUMNS = [
    "ecg_id",
    "patient_id",
    "age",
    "sex",
    "scp_codes",
    "filename_lr",
    "filename_hr",
    "strat_fold",
]
PTBXL_OPTIONAL_COLUMNS = ["recording_date"]
PLACEHOLDER_OBSERVED_AT = datetime(1970, 1, 1)


def read_metadata_csv(path: str | Path) -> pl.DataFrame:
    df = pl.read_csv(path)

    missing_columns = [
        column for column in PTBXL_METADATA_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required PTB-XL metadata columns: {missing}")

    columns = [
        column
        for column in [*PTBXL_METADATA_COLUMNS, *PTBXL_OPTIONAL_COLUMNS]
        if column in df.columns
    ]
    return df.select(columns)


def normalize_metadata(df: pl.DataFrame) -> list[CanonicalRecord]:
    records: list[CanonicalRecord] = []

    for row in df.iter_rows(named=True):
        observed_at, quality_flag, observed_at_source = _observed_at_from_row(row)
        ecg_id = row["ecg_id"]

        records.append(
            CanonicalRecord(
                source="PhysioNet",
                domain="ecg",
                dataset_id="ptb-xl",
                record_id=f"ptbxl-{ecg_id}",
                observed_at=observed_at,
                variable="ecg_metadata",
                value=None,
                unit=None,
                quality_flag=quality_flag,
                location_or_instrument=row.get("filename_lr"),
                metadata={
                    "ecg_id": ecg_id,
                    "patient_id": row.get("patient_id"),
                    "age": row.get("age"),
                    "sex": row.get("sex"),
                    "scp_codes": _parse_scp_codes(row.get("scp_codes")),
                    "filename_lr": row.get("filename_lr"),
                    "filename_hr": row.get("filename_hr"),
                    "strat_fold": row.get("strat_fold"),
                    "recording_date": row.get("recording_date"),
                    "observed_at_source": observed_at_source,
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


def _observed_at_from_row(row: dict[str, Any]) -> tuple[datetime, str | None, str]:
    recording_date = row.get("recording_date")
    if recording_date is None or str(recording_date).strip() == "":
        return (
            PLACEHOLDER_OBSERVED_AT,
            "missing_recording_date",
            "placeholder_missing_recording_date",
        )

    try:
        return datetime.fromisoformat(str(recording_date)), None, "recording_date"
    except ValueError:
        return (
            PLACEHOLDER_OBSERVED_AT,
            "invalid_recording_date",
            "placeholder_invalid_recording_date",
        )


def _parse_scp_codes(value: object) -> object:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return text
