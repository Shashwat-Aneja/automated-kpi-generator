import pandas as pd,pytest
from kpi_generator import load_transactions
@pytest.mark.parametrize('delimiter',[';', '\t', '|'])
def test_alternate_delimiter_preserves_quoted_fields(tmp_path,delimiter):
    source=tmp_path/'input.csv';data=pd.DataFrame({'name':['first'+delimiter+'second'],'amount':[12]});data.to_csv(source,index=False,sep=delimiter)
    result=load_transactions(source,delimiter=delimiter)
    assert result['name'].tolist()==data['name'].tolist() and result['amount'].tolist()==[12]
def test_duplicate_headers_are_checked_with_selected_delimiter(tmp_path):
    p=tmp_path/'input.csv';p.write_text('amount;amount\n1;999\n')
    with pytest.raises(ValueError,match='unique'):load_transactions(p,delimiter=';')

def test_selected_delimiter_reaches_the_cli_workflow(tmp_path):
    from kpi_generator import main
    source=tmp_path/'input.csv';source.write_text('date;amount;type\\n2026-01-01;10;revenue\\n'.replace('\\n','\n'))
    arguments=[str(source),'--delimiter',';']+['--json']
    assert main(arguments)==0
