import json, openpyxl
d = json.load(open('/workspace/source_extract.json'))
print('=== packaging 8 rows ===')
for r in d['bom']['packaging']:
    print(' ', r)
print('=== aux 16 rows ===')
for r in d['bom']['aux']:
    print(' ', r)
print('=== tooling 16 rows === note:', d['sheet3'].get('tool_note'))
for r in d['sheet3']['tooling']:
    print(' ', r)
print('tooling_hdr', d['sheet3']['tooling_hdr'])
print('=== labor_hdr ===', d['sheet3']['labor_hdr'])
print('=== labor 52 ===')
for r in d['sheet3']['labor']:
    print(' ', r)
print('=== Sheet1 (source) rows 1-50 ===')
wb = openpyxl.load_workbook('/workspace/.uploads/cc030d46-2ad1-4732-b4d0-d438692ca0d0_成本分解-8-26.xlsx', data_only=True)
ws = wb['Sheet1']
print('max_row', ws.max_row, 'max_col', ws.max_column)
for r in range(1, min(ws.max_row, 50) + 1):
    vals = []
    for c in range(1, min(ws.max_column, 8) + 1):
        v = ws.cell(row=r, column=c).value
        if v not in (None, ''):
            vals.append(f'{ws.cell(row=r,column=c).coordinate}={v!r}')
    if vals:
        print(' ', ' | '.join(vals)[:400])
