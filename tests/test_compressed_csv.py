import gzip,bz2,lzma,pytest
from kpi_generator import load_transactions
@pytest.mark.parametrize('suffix,opener',[('.gz',gzip.open),('.bz2',bz2.open),('.xz',lzma.open)])
def test_compressed_csv_keeps_header_validation_and_delimiters(tmp_path,suffix,opener):
    path=tmp_path/('input.csv'+suffix)
    with opener(path,'wt',encoding='utf-8') as f:f.write('\ufeff"name";amount\n"first;second";12\n')
    assert load_transactions(path,delimiter=';')['name'].tolist()==['first;second']
    with opener(path,'wt',encoding='utf-8') as f:f.write('amount;amount\n1;999\n')
    with pytest.raises(ValueError,match='unique'):load_transactions(path,delimiter=';')
