import pandas as pd
from kpi_generator import calculate_kpis

def test_zero_revenue_ratios_are_unavailable(capsys):
    result=calculate_kpis(pd.DataFrame({"date":["2026-01-01"],"type":["expense"],"amount":[10]}))
    assert result["ratios_available"] is False
    assert "Profit Margin      : N/A" in capsys.readouterr().out
