import pandas as pd
from kpi_generator import monthly_kpis
def test_calendar_months_are_sorted_and_totals_reconcile(capsys):
    data=pd.DataFrame({'date':['2026-02-01','2026-01-01','2026-01-10'],'type':['revenue','revenue','expense'],'amount':[20,10,3]})
    result=monthly_kpis(data)
    assert [r['month'] for r in result]==['2026-01','2026-02']
    assert sum(r['total_revenue'] for r in result)==30
    assert result[0]['profit']==7 and sum(r['transaction_count'] for r in result)==3
    assert capsys.readouterr().out==''
