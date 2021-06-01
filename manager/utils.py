def td(string='', td_id='', cls='', cs=1, rs=1):
    td_class = f' class="{cls}"' if cls else ''
    colspan = f' colspan={cs}' if cs > 1 else ''
    rowspan = f' rowspan={rs}' if rs > 1 else ''
    str_id = f' id="{td_id}"' if td_id else ''
    return f'<td{str_id}{td_class}{rowspan}{colspan}>{string}</td>'


def tr(string='', tr_id=''):
    return f'<tr>{string}</tr>' if tr_id == '' else f'<tr id="{tr_id}">{string}</tr>'


def table(string='', table_id='', cp=0):
    cellpadding = f' cellpadding = {cp}' if cp == 0 else ''
    table_id = f' id={table_id}' if table_id else ''
    return f'<table{table_id}{cellpadding}>{string}</table>'
