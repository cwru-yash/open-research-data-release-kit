from collections.abc import Callable
from pathlib import Path

import typer
from rich.console import Console

from ordk.adapters.noaa import (
    normalize_daily_summary,
    read_daily_summary_csv,
    records_to_dataframe,
)
from ordk.core.publish import publish_release


app = typer.Typer(help="Build validated research data release artifacts.")
console = Console()

BuildFunction = Callable[[Path, Path], dict[str, Path]]


def build_noaa_release(input_path: Path, output_dir: Path) -> dict[str, Path]:
    raw_df = read_daily_summary_csv(input_path)
    records = normalize_daily_summary(raw_df)
    normalized_df = records_to_dataframe(records)
    return publish_release(normalized_df, output_dir)


BUILDERS: dict[str, BuildFunction] = {
    "noaa": build_noaa_release,
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
            f"Unsupported source: {source}. "
            f"Supported sources: {supported_sources}"
        )
        raise typer.Exit(code=1)

    artifacts = builder(input_path, output_dir)

    console.print(f"Published release: {output_dir}")
    for name, path in artifacts.items():
        console.print(f"- {name}: {path}")


if __name__ == "__main__":
    app()