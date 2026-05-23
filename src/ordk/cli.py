from collections.abc import Callable
from pathlib import Path

import typer
from rich.console import Console

from ordk.adapters import nasa_omni, noaa, physionet_ptbxl
from ordk.core.publish import publish_release


app = typer.Typer(help="Build validated research data release artifacts.")
console = Console()

BuildFunction = Callable[[Path, Path], dict[str, Path]]


def build_noaa_release(input_path: Path, output_dir: Path) -> dict[str, Path]:
    raw_df = noaa.read_daily_summary_csv(input_path)
    records = noaa.normalize_daily_summary(raw_df)
    normalized_df = noaa.records_to_dataframe(records)
    return publish_release(normalized_df, output_dir)


def build_physionet_release(input_path: Path, output_dir: Path) -> dict[str, Path]:
    raw_df = physionet_ptbxl.read_metadata_csv(input_path)
    records = physionet_ptbxl.normalize_metadata(raw_df)
    normalized_df = physionet_ptbxl.records_to_dataframe(records)
    return publish_release(normalized_df, output_dir)


def build_nasa_release(input_path: Path, output_dir: Path) -> dict[str, Path]:
    raw_df = nasa_omni.read_omni_csv(input_path)
    records = nasa_omni.normalize_omni(raw_df)
    normalized_df = nasa_omni.records_to_dataframe(records)
    return publish_release(normalized_df, output_dir)


BUILDERS: dict[str, BuildFunction] = {
    "nasa": build_nasa_release,
    "noaa": build_noaa_release,
    "physionet": build_physionet_release,
}


@app.callback()
def main() -> None:
    """Open Research Data Release Kit."""


@app.command()
def build(source: str, input_path: Path, output_dir: Path) -> None:
    """Build a release from a supported source adapter."""
    builder = BUILDERS.get(source)

    if builder is None:
        supported_sources = ", ".join(sorted(BUILDERS))
        console.print(
            f"Unsupported source: {source}. Supported sources: {supported_sources}"
        )
        raise typer.Exit(code=1)

    artifacts = builder(input_path, output_dir)

    console.print(f"Published release: {output_dir}")
    for name, path in artifacts.items():
        console.print(f"- {name}: {path}")


if __name__ == "__main__":
    app()
