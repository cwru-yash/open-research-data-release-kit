import json

import polars as pl

from ordk.adapters.nasa_omni import (
    normalize_omni,
    read_omni_csv,
    records_to_dataframe,
)


def test_read_omni_csv_selects_supported_columns(tmp_path):
    csv_path = tmp_path / "omni_sample.csv"
    csv_path.write_text(
        "timestamp,BZ_GSM,FLOW_SPEED,PROTON_DENSITY,UNUSED\n"
        "2024-01-01T00:00:00,-2.5,420.0,5.1,ignore-me\n"
    )

    df = read_omni_csv(csv_path)

    assert df.columns == [
        "timestamp",
        "BZ_GSM",
        "FLOW_SPEED",
        "PROTON_DENSITY",
    ]
    assert df.shape == (1, 4)


def test_normalize_omni_maps_row_to_canonical_records():
    df = pl.DataFrame(
        {
            "timestamp": ["2024-01-01T00:00:00"],
            "BZ_GSM": [-2.5],
            "FLOW_SPEED": [420.0],
            "PROTON_DENSITY": [5.1],
        }
    )

    records = normalize_omni(df)

    assert len(records) == 3
    assert {record.variable for record in records} == {
        "BZ_GSM",
        "FLOW_SPEED",
        "PROTON_DENSITY",
    }
    assert all(record.source == "NASA/SPDF" for record in records)
    assert all(record.domain == "space_physics" for record in records)
    assert all(record.dataset_id == "omni" for record in records)

    bz = next(record for record in records if record.variable == "BZ_GSM")
    assert bz.value == -2.5
    assert bz.unit == "nT"
    assert bz.location_or_instrument == "OMNI"


def test_records_to_dataframe_returns_normalized_polars_dataframe():
    df = pl.DataFrame(
        {
            "timestamp": ["2024-01-01T00:00:00"],
            "BZ_GSM": [-2.5],
            "FLOW_SPEED": [420.0],
            "PROTON_DENSITY": [5.1],
        }
    )

    records = normalize_omni(df)
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

    bz = release_df.filter(pl.col("variable") == "BZ_GSM").row(0, named=True)
    metadata = json.loads(bz["metadata"])

    assert bz["source"] == "NASA/SPDF"
    assert bz["domain"] == "space_physics"
    assert bz["value"] == -2.5
    assert bz["unit"] == "nT"
    assert metadata["raw_column"] == "BZ_GSM"
