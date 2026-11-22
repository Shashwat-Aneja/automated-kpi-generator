import numpy as np,pandas as pd,pytest
from kpi_generator import calculate_kpis
def test_object_numpy_boolean_cannot_become_one_unit_of_revenue():
    data=pd.DataFrame({'date':['2026-01-01'],'amount':pd.Series([np.bool_(True)],dtype=object),'type':['revenue']})
    with pytest.raises(ValueError,match='booleans'):calculate_kpis(data,print_report=False)
