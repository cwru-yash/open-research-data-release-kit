from typer.testing import CliRunner

from ordk.cli import app


runner = CliRunner()


def test_build_noaa_publishes_release_artifacts(tmp_path):
    input_path = tmp_path / "noaa_daily.csv"
    output_dir = tmp_path / "release"

    input_path.write_text(
        "STATION,DATE,TMAX,TMIN,PRCP\nUSW00094728,2024-01-01,50,32,10\n"
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


def test_build_physionet_publishes_release_artifacts(tmp_path):
    input_path = tmp_path / "ptbxl_database.csv"
    output_dir = tmp_path / "physionet-release"

    input_path.write_text(
        "ecg_id,patient_id,age,sex,scp_codes,filename_lr,filename_hr,"
        "strat_fold,recording_date\n"
        "1,100,63,M,\"{'NORM': 100.0}\",records100/00000/00001_lr,"
        "records500/00000/00001_hr,1,2020-01-01 12:00:00\n"
    )

    result = runner.invoke(
        app,
        ["build", "physionet", str(input_path), str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "normalized.csv").exists()
    assert (output_dir / "normalized.parquet").exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "report.md").exists()
    assert "Published release" in result.stdout


def test_build_nasa_publishes_release_artifacts(tmp_path):
    input_path = tmp_path / "omni_sample.csv"
    output_dir = tmp_path / "nasa-release"

    input_path.write_text(
        "timestamp,BZ_GSM,FLOW_SPEED,PROTON_DENSITY\n"
        "2024-01-01T00:00:00,-2.5,420.0,5.1\n"
    )

    result = runner.invoke(
        app,
        ["build", "nasa", str(input_path), str(output_dir)],
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
        ["build", "unknown", str(input_path), str(output_dir)],
    )

    assert result.exit_code != 0
    assert "Unsupported source" in result.stdout
