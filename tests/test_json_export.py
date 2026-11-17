import json
import pytest
import kpi_generator as kpi


def test_json_export_contains_metrics_and_cannot_replace_input(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("date,type,amount\n2026-11-17,revenue,100\n")
    output = tmp_path / "metrics.json"
    assert kpi.main([str(source), "--json-output", str(output)]) == 0
    assert json.loads(output.read_text())["total_revenue"] == 100
    original = source.read_bytes()
    assert kpi.main([str(source), "--json-output", str(source)]) == 1
    assert source.read_bytes() == original


def test_json_replace_failure_preserves_previous_report(tmp_path, monkeypatch):
    output = tmp_path / "metrics.json"
    output.write_text("old")
    def fail(*args):
        raise OSError("disk error")
    monkeypatch.setattr(kpi.os, "replace", fail)
    with pytest.raises(OSError):
        kpi.export_json({"total_revenue": 100}, output)
    assert output.read_text() == "old"
    assert list(tmp_path.iterdir()) == [output]
