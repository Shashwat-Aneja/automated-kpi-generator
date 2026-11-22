import pandas as pd
from kpi_generator import monthly_kpis
def test_monthly_grouping_preserves_rows_with_duplicate_indexes():
    data=pd.DataFrame({'date':['2026-02-01','2026-01-01','2026-02-03','2026-01-02'],'amount':[20,10,5,2],'type':['revenue','revenue','expense','expense']},index=[0,0,1,1])
    result=monthly_kpis(data)
    assert [r['month'] for r in result]==['2026-01','2026-02']
    assert [r['profit'] for r in result]==[8,15]
    assert sum(r['transaction_count'] for r in result)==len(data)
