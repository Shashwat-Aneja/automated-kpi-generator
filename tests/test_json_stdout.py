import json
from kpi_generator import main
def test_json_stdout_includes_comparison_without_human_reports(tmp_path,capsys):
    p=tmp_path/'in.csv';p.write_text('date,type,amount\n2026-01-01,revenue,10\n')
    assert main([str(p),'--compare-csv',str(p),'--json'])==0
    data=json.loads(capsys.readouterr().out)
    assert data['total_revenue']==10 and data['comparison']['profit']['change']==0
