from typer.testing import CliRunner

from ordk.cli import app


runner = CliRunner()


def test_build_noaa_publishes_release_artifacts(tmp_path):
    input_path = tmp_path / "noaa_daily.csv"
    output_dir = tmp_path / "release"

    input_path.write_text(
        "STATION,DATE,TMAX,TMIN,PRCP\n"
        "USW00094728,2024-01-01,50,32,10\n"
    )

    result = runner.invoke(
        app,
        ["build", "noaa", str(input_path), str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "normalized.csv").exists()
    assert (output_dir / "normalized.parquet").exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "report.md").exists()
    assert "Published release" in result.stdout


def test_build_rejects_unsupported_source(tmp_path):
    input_path = tmp_path / "input.csv"
    output_dir = tmp_path / "release"

    input_path.write_text("x\n1\n")

    result = runner.invoke(
        app,
        ["build", "nasa", str(input_path), str(output_dir)],
    )

    assert result.exit_code != 0
    assert "Unsupported source" in result.stdout