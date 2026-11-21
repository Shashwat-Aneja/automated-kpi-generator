import pandas as pd,pytest
from kpi_generator import calculate_kpis
@pytest.mark.parametrize('date',[20260101,1.5,True])
def test_numeric_dates_cannot_silently_become_1970_transactions(date):
    with pytest.raises(ValueError,match='calendar dates'):calculate_kpis(pd.DataFrame({'date':[date],'amount':[10],'type':['revenue']}))
