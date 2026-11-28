from io import BytesIO
import gzip
import pytest
from kpi_generator import load_transactions

def test_explicit_legacy_encoding_in_header_body_and_compressed_path(tmp_path):
    raw="café,label\n1,café\n".encode('cp1252')
    frame=load_transactions(BytesIO(raw),encoding='cp1252')
    assert frame.columns.tolist()==['café','label'] and frame.label.tolist()==['café']
    path=tmp_path/'input.csv.gz';path.write_bytes(gzip.compress(raw))
    assert load_transactions(path,encoding='cp1252').label.tolist()==['café']

def test_duplicate_non_ascii_headers_are_still_rejected():
    with pytest.raises(ValueError,match='duplicate'):
        load_transactions(BytesIO("café,café\n1,2\n".encode('cp1252')),encoding='cp1252')

def test_bad_encoding_precedes_open():
    with pytest.raises(ValueError,match='encoding'):
        load_transactions('missing.csv',encoding='not-a-codec')
