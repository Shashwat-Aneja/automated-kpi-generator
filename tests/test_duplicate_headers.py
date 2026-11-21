import pandas as pd,pytest
from kpi_generator import main,validate_transactions
def test_duplicate_amount_csv_fails_before_export(tmp_path):
    p=tmp_path/'in.csv';p.write_text('date,type,amount,amount\n2026-01-01,revenue,10,999\n')
    out=tmp_path/'out.json';out.write_text('keep')
    assert main([str(p),'--json-output',str(out)])==1
    assert out.read_text()=='keep'
def test_duplicate_dataframe_columns_raise_validation_error():
    with pytest.raises(ValueError,match='unique'):validate_transactions(pd.DataFrame([['2026-01-01',1,2,'revenue']],columns=['date','amount','amount','type']))
