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


def test_calculate_kpis_returns_machine_readable_summary():
    data = pd.DataFrame(
        {
            "date": ["2026-02-03", "2026-02-01", "2026-02-03"],
            "amount": [5000, 1200, 3000],
            "type": ["revenue", "expense", "revenue"],
        }
    )

    summary = calculate_kpis(data)

    assert summary == {
        "total_revenue": 8000.0,
        "total_expenses": 1200.0,
        "profit": 6800.0,
        "profit_margin": 85.0,
        "expense_ratio": 15.0,
        "transaction_count": 3,
        "period_start": "2026-02-01",
        "period_end": "2026-02-03",
    }
