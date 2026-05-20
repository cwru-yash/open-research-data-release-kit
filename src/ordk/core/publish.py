import json
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from ordk.core.quality import summarize_quality


def publish_release(df: pl.DataFrame, output_dir: str | Path) -> dict[str, Path]:
    release_dir = Path(output_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    normalized_csv = release_dir / "normalized.csv"
    normalized_parquet = release_dir / "normalized.parquet"
    metadata_json = release_dir / "metadata.json"
    report_md = release_dir / "report.md"

    quality = summarize_quality(df)

    df.write_csv(normalized_csv)
    df.write_parquet(normalized_parquet)

    metadata = {
        "created_at": datetime.now(UTC).isoformat(),
        "quality": quality,
    }

    metadata_json.write_text(json.dumps(metadata, indent=2, sort_keys=True))
    report_md.write_text(_render_report(quality))

    return {
        "normalized_csv": normalized_csv,
        "normalized_parquet": normalized_parquet,
        "metadata_json": metadata_json,
        "report_md": report_md,
    }


def _render_report(quality: dict[str, object]) -> str:
    return f"""# Research Data Release Report

## Summary

- Source: {quality["source"]}
- Domain: {quality["domain"]}
- Dataset: {quality["dataset_id"]}
- Rows: {quality["row_count"]}
- Variables: {quality["variable_count"]}
- Missing values: {quality["missing_value_count"]}
- Observed range: {quality["min_observed_at"]} to {quality["max_observed_at"]}
- Units seen: {", ".join(quality["units_seen"])}
"""
