import pandas as pd

from kpi_generator import calculate_kpis


def test_calculate_kpis_reports_average_revenue_and_expense_transactions():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "amount": [100.0, 300.0, 50.0],
        "type": ["revenue", "revenue", "expense"],
    })

    summary = calculate_kpis(transactions)

    assert summary["revenue_transaction_count"] == 2
    assert summary["expense_transaction_count"] == 1
    assert summary["average_revenue_transaction"] == 200.0
    assert summary["average_expense_transaction"] == 50.0


def test_average_transaction_values_are_zero_when_a_type_is_absent():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "amount": [50.0, 75.0],
        "type": ["expense", "expense"],
    })

    summary = calculate_kpis(transactions)

    assert summary["revenue_transaction_count"] == 0
    assert summary["average_revenue_transaction"] == 0.0
    assert summary["average_expense_transaction"] == 62.5
