from io import StringIO
import pytest
from kpi_generator import load_transactions

def test_literal_ledger_ids():
    frame=load_transactions(StringIO("id,date,amount,type\n001,2026-01-01,1,revenue\nNA,2026-01-02,2,expense\n"), id_column="id")
    assert frame.id.tolist()==["001", "NA"]

@pytest.mark.parametrize("ids", ["a,a", "a, a ", "a, "])
def test_bad_ledger_ids(ids):
    a,b=ids.split(',')
    with pytest.raises(ValueError, match="Ledger IDs"):
        load_transactions(StringIO(f"id,date,amount,type\n{a},2026-01-01,1,revenue\n{b},2026-01-02,2,expense\n"), id_column="id")
