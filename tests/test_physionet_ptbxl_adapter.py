import json
from datetime import datetime

import polars as pl

from ordk.adapters.physionet_ptbxl import (
    normalize_metadata,
    read_metadata_csv,
    records_to_dataframe,
)


def test_read_metadata_csv_selects_supported_columns(tmp_path):
    csv_path = tmp_path / "ptbxl_database.csv"
    csv_path.write_text(
        "ecg_id,patient_id,age,sex,scp_codes,filename_lr,filename_hr,"
        "strat_fold,recording_date,UNUSED\n"
        "1,100,63,M,\"{'NORM': 100.0}\",records100/00000/00001_lr,"
        "records500/00000/00001_hr,1,2020-01-01 12:00:00,ignore-me\n"
    )

    df = read_metadata_csv(csv_path)

    assert df.columns == [
        "ecg_id",
        "patient_id",
        "age",
        "sex",
        "scp_codes",
        "filename_lr",
        "filename_hr",
        "strat_fold",
        "recording_date",
    ]
    assert df.shape == (1, 9)


def test_normalize_metadata_maps_ptbxl_row_to_canonical_metadata_record():
    df = pl.DataFrame(
        {
            "ecg_id": [1],
            "patient_id": [100],
            "age": [63],
            "sex": ["M"],
            "scp_codes": ["{'NORM': 100.0}"],
            "filename_lr": ["records100/00000/00001_lr"],
            "filename_hr": ["records500/00000/00001_hr"],
            "strat_fold": [1],
        }
    )

    records = normalize_metadata(df)

    assert len(records) == 1
    record = records[0]
    assert record.source == "PhysioNet"
    assert record.domain == "ecg"
    assert record.dataset_id == "ptb-xl"
    assert record.record_id == "ptbxl-1"
    assert record.variable == "ecg_metadata"
    assert record.value is None
    assert record.unit is None
    assert record.quality_flag == "missing_recording_date"
    assert record.observed_at == datetime(1970, 1, 1)
    assert record.location_or_instrument == "records100/00000/00001_lr"
    assert record.metadata["scp_codes"] == {"NORM": 100.0}
    assert record.metadata["observed_at_source"] == (
        "placeholder_missing_recording_date"
    )


def test_records_to_dataframe_returns_normalized_polars_dataframe():
    df = pl.DataFrame(
        {
            "ecg_id": [1],
            "patient_id": [100],
            "age": [63],
            "sex": ["M"],
            "scp_codes": ["{'NORM': 100.0}"],
            "filename_lr": ["records100/00000/00001_lr"],
            "filename_hr": ["records500/00000/00001_hr"],
            "strat_fold": [1],
            "recording_date": ["2020-01-01 12:00:00"],
        }
    )

    records = normalize_metadata(df)
    release_df = records_to_dataframe(records)

    assert release_df.shape == (1, 11)
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

    row = release_df.row(0, named=True)
    metadata = json.loads(row["metadata"])

    assert row["source"] == "PhysioNet"
    assert row["domain"] == "ecg"
    assert row["dataset_id"] == "ptb-xl"
    assert row["variable"] == "ecg_metadata"
    assert row["quality_flag"] is None
    assert metadata["ecg_id"] == 1
    assert metadata["scp_codes"] == {"NORM": 100.0}
    assert metadata["observed_at_source"] == "recording_date"
