import pandas as pd
import pytest
from kpi_generator import validate_transactions


def test_boolean_amount_is_not_silently_counted_as_one():
    frame = pd.DataFrame({"date": ["2026-11-16"], "amount": [True], "type": ["revenue"]})
    with pytest.raises(ValueError, match="booleans"):
        validate_transactions(frame)
