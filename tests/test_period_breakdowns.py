import pandas as pd,pytest
from kpi_generator import period_kpis

@pytest.mark.parametrize('frequency,labels,totals',[('quarter',['2025-Q4','2026-Q1','2026-Q2'],[5,30,40]),('year',['2025','2026'],[5,70])])
def test_period_breakdowns_reconcile_across_calendar_boundaries(frequency,labels,totals):
    frame=pd.DataFrame({'date':['2026-04-01','2026-01-01','2025-12-31','2026-03-31'],'type':['revenue']*4,'amount':[40,10,5,20]})
    result=period_kpis(frame,frequency)
    assert [row['period'] for row in result]==labels
    assert [row['total_revenue'] for row in result]==totals
    assert sum(row['transaction_count'] for row in result)==4
