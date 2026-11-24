import json,pytest
from kpi_generator import main

def test_comparison_range_is_independent_of_current_range(tmp_path,capsys):
    a=tmp_path/'a.csv';a.write_text('date,type,amount\n2026-02-01,revenue,20\n')
    b=tmp_path/'b.csv';b.write_text('date,type,amount\n2026-01-01,revenue,10\n2025-01-01,revenue,1000\n')
    assert main([str(a),'--compare-csv',str(b),'--compare-start-date','2026-01-01','--compare-end-date','2026-01-31','--json'])==0
    data=json.loads(capsys.readouterr().out)
    assert data['comparison']['total_revenue']['growth_percent']==100
    assert data['comparison_period']['period_start']=='2026-01-01'

def test_comparison_dates_require_comparison_input():
    with pytest.raises(SystemExit):main(['missing.csv','--compare-start-date','2026-01-01'])
