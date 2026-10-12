import pandas as pd

from kpi_generator import calculate_kpis


def test_calculate_kpis_reports_revenue_expenses_and_profit(capsys):
    data = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "amount": [5000, 1200, 3000],
            "type": ["revenue", "expense", "revenue"],
        }
    )

    calculate_kpis(data)

    output = capsys.readouterr().out
    assert "Total Revenue      : ₹8000" in output
    assert "Total Expenses     : ₹1200" in output
    assert "Profit             : ₹6800" in output
    assert "Profit Margin      : 85.00%" in output
    assert "Expense Ratio      : 15.00%" in output


def test_calculate_kpis_handles_zero_revenue_without_division_error(capsys):
    data = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "amount": [250],
            "type": ["expense"],
        }
    )

    calculate_kpis(data)

    output = capsys.readouterr().out
    assert "Profit Margin      : 0.00%" in output
    assert "Expense Ratio      : 0.00%" in output
    assert "Profit             : ₹-250" in output
