import pandas as pd
import pytest

from kpi_generator import filter_transactions_by_period


def test_period_filter_includes_both_calendar_date_boundaries():
    frame = pd.DataFrame(
        {
            "date": ["2026-02-01", "2026-02-02 09:30:00", "2026-02-02 17:45:00", "2026-02-03"],
            "amount": [10, 20, 30, 40],
            "type": ["revenue", "expense", "revenue", "expense"],
        }
    )

    filtered = filter_transactions_by_period(
        frame, start_date="2026-02-02", end_date="2026-02-02"
    )

    assert filtered["amount"].tolist() == [20, 30]
    assert len(filtered) == 2


def test_period_filter_rejects_reversed_dates():
    frame = pd.DataFrame(
        {"date": ["2026-02-01"], "amount": [10], "type": ["revenue"]}
    )

    with pytest.raises(ValueError, match="on or before"):
        filter_transactions_by_period(
            frame, start_date="2026-02-02", end_date="2026-02-01"
        )


def test_period_filter_rejects_empty_result():
    frame = pd.DataFrame(
        {"date": ["2026-02-01"], "amount": [10], "type": ["revenue"]}
    )

    with pytest.raises(ValueError, match="No transactions"):
        filter_transactions_by_period(frame, start_date="2026-03-01")
