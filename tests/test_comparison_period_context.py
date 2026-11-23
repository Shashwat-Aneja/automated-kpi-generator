import json
from kpi_generator import main
def test_json_discloses_comparison_dates_and_overlap(tmp_path,capsys):
    current=tmp_path/'current.csv';current.write_text('date,type,amount\n2026-01-01,revenue,10\n2026-01-10,revenue,20\n')
    previous=tmp_path/'previous.csv';previous.write_text('date,type,amount\n2026-01-05,revenue,5\n')
    assert main([str(current),'--compare-csv',str(previous),'--json'])==0
    data=json.loads(capsys.readouterr().out)
    assert data['comparison_period']=={'period_start':'2026-01-05','period_end':'2026-01-05','overlaps_current':True}
def test_disjoint_comparison_period_is_identified(tmp_path,capsys):
    current=tmp_path/'current.csv';current.write_text('date,type,amount\n2026-02-01,revenue,10\n')
    previous=tmp_path/'previous.csv';previous.write_text('date,type,amount\n2026-01-01,revenue,5\n')
    assert main([str(current),'--compare-csv',str(previous),'--json'])==0
    assert json.loads(capsys.readouterr().out)['comparison_period']['overlaps_current'] is False
