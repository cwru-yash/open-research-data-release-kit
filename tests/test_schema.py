from datetime import datetime

import pytest
from pydantic import ValidationError

from ordk.schema import CanonicalRecord


def test_canonical_record_accepts_valid_data():
    record = CanonicalRecord(
        source="NOAA/NCEI",
        domain="climate",
        dataset_id="daily-summaries",
        record_id="USW00094728-2024-01-01-TMAX",
        observed_at="2024-01-01T00:00:00",
        variable="TMAX",
        value="12.5",
        unit="C",
        quality_flag=None,
        location_or_instrument="USW00094728",
    )

    assert record.source == "NOAA/NCEI"
    assert record.domain == "climate"
    assert record.value == 12.5
    assert isinstance(record.observed_at, datetime)
    assert record.metadata == {}


def test_canonical_record_rejects_invalid_datetime():
    with pytest.raises(ValidationError):
        CanonicalRecord(
            source="NOAA/NCEI",
            domain="climate",
            dataset_id="daily-summaries",
            record_id="bad-date",
            observed_at="not-a-date",
            variable="TMAX",
            value=12.5,
            unit="C",
        )


def test_canonical_record_accepts_date_only_observed_at():
    record = CanonicalRecord(
        source="NOAA/NCEI",
        domain="climate",
        dataset_id="daily-summaries",
        record_id="date-only",
        observed_at="2024-01-01",
        variable="TMAX",
        value=12.5,
    )

    assert isinstance(record.observed_at, datetime)
