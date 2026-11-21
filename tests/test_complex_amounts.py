import pandas as pd,pytest
from kpi_generator import calculate_kpis
@pytest.mark.parametrize("object_dtype",[False,True])
def test_complex_amounts_do_not_discard_imaginary_values(object_dtype):
    with pytest.raises(ValueError,match='real numbers'):calculate_kpis(pd.DataFrame({'date':['2026-01-01'],'amount':pd.Series([10+20j],dtype=object if object_dtype else complex),'type':['revenue']}))
