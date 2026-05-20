import polars as pl


def summarize_quality(df: pl.DataFrame) -> dict[str, object]:
    return {
        "row_count": df.height,
        "variable_count": df["variable"].n_unique(),
        "missing_value_count": df["value"].null_count(),
        "min_observed_at": df["observed_at"].min(),
        "max_observed_at": df["observed_at"].max(),
        "source": _single_value(df, "source"),
        "domain": _single_value(df, "domain"),
        "dataset_id": _single_value(df, "dataset_id"),
        "units_seen": sorted(df["unit"].drop_nulls().unique().to_list()),
    }


def _single_value(df: pl.DataFrame, column: str) -> object:
    values = df[column].drop_nulls().unique().to_list()

    if len(values) == 1:
        return values[0]

    return values
