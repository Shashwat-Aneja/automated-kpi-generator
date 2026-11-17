from kpi_generator import compare_periods


def test_comparison_reports_changes_and_undefined_growth():
    previous = {"total_revenue": 100, "total_expenses": 0, "profit": -10}
    current = {"total_revenue": 120, "total_expenses": 5, "profit": 115}
    result = compare_periods(current, previous)
    assert result["total_revenue"] == {"change": 20, "growth_percent": 20}
    assert result["total_expenses"]["growth_percent"] is None
    assert result["profit"]["growth_percent"] is None
    assert result["profit"]["change"] == 125
