import pandas as pd
import pytest
from kpi_generator import filter_transactions_by_period


@pytest.mark.parametrize("bound", ["NaT", "", float("nan")])
@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_missing_filter_bounds_are_invalid(bound, field):
    frame = pd.DataFrame({"date": ["2026-11-16"], "amount": [1], "type": ["revenue"]})
    with pytest.raises(ValueError, match="Date filters"):
        filter_transactions_by_period(frame, **{field: bound})
