import pandas as pd
import pytest
from kpi_generator import calculate_kpis


def frame(amounts):
    return pd.DataFrame({"date": ["2026-11-16"] * len(amounts), "amount": amounts, "type": ["revenue"] * len(amounts)})


def test_integer_totals_do_not_wrap_negative():
    assert calculate_kpis(frame([2**62, 2**62]))["total_revenue"] == float(2**63)


def test_float_total_overflow_is_a_validation_error():
    with pytest.raises(ValueError, match="numeric range"):
        calculate_kpis(frame([1e308, 1e308]))
