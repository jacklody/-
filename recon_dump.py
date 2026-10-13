import json, openpyxl
wb = openpyxl.load_workbook('/workspace/产品成本测算报价表.xlsx')

out = []
ws = wb['制费明细']
out.append('=== 制费明细 A/H col rows 1-95 ===')
for r in range(1, 96):
    vals = []
    for c in range(1, 9):
        v = ws.cell(r, c).value
        if v is not None:
            vals.append(f'{openpyxl.utils.get_column_letter(c)}{r}={v!r}')
    if vals:
        out.append(' | '.join(vals))

ws = wb['报价汇总']
out.append('=== 报价汇总 rows 27-54 A-H ===')
for r in range(27, 55):
    vals = []
    for c in range(1, 9):
        v = ws.cell(r, c).value
        if v is not None:
            vals.append(f'{openpyxl.utils.get_column_letter(c)}{r}={v!r}')
    if vals:
        out.append(' | '.join(vals))

ws = wb['物料明细']
out.append('=== 物料明细 B col distinct (rows 3-110) ===')
seen = {}
for r in range(3, 111):
    v = ws.cell(r, 2).value
    if v is not None:
        seen[v] = seen.get(v, 0) + 1
out.append(repr(seen))
out.append(f'max_row={ws.max_row} max_col={ws.max_column}')
out.append('=== 物料明细 row2 header + row3 sample ===')
out.append(repr([ws.cell(2, c).value for c in range(1, 11)]))
out.append(repr([ws.cell(3, c).value for c in range(1, 11)]))
out.append(repr([ws.cell(4, c).value for c in range(1, 11)]))

ws = wb['参数']
out.append('=== 参数 rows 1-50 A-D ===')
for r in range(1, 51):
    vals = []
    for c in range(1, 5):
        v = ws.cell(r, c).value
        if v is not None:
            vals.append(f'{openpyxl.utils.get_column_letter(c)}{r}={v!r}')
    if vals:
        out.append(' | '.join(vals))
out.append(f'参数 max_row={ws.max_row}')

ws = wb['使用说明']
out.append(f'=== 使用说明 max_row={ws.max_row} max_col={ws.max_column} ===')
for r in range(1, min(ws.max_row, 60) + 1):
    v = ws.cell(r, 1).value
    if v is not None:
        out.append(f'A{r}={v!r}')

data = json.load(open('/workspace/source_extract.json'))
out.append('=== JSON keys ===')
out.append(repr(list(data.keys())))
out.append('bom keys: ' + repr(list(data['bom'].keys())))
out.append('sheet3 keys: ' + repr(list(data['sheet3'].keys())))
out.append('hardware[0]: ' + repr(data['bom']['hardware'][0]))
out.append('structure[0]: ' + repr(data['bom']['structure'][0]))
out.append('packaging[0]: ' + repr(data['bom']['packaging'][0]))
out.append('aux[0]: ' + repr(data['bom']['aux'][0]))
out.append('aux[-1]: ' + repr(data['bom']['aux'][-1]))
out.append('labor[0]: ' + repr(data['sheet3']['labor'][0]))
out.append('labor[-1]: ' + repr(data['sheet3']['labor'][-1]))
out.append('labor_total: ' + repr(data['sheet3'].get('labor_total')))
out.append('tooling[0]: ' + repr(data['sheet3']['tooling'][0]))
out.append('tooling[1]: ' + repr(data['sheet3']['tooling'][1]))
out.append('tool_total: ' + repr(data['sheet3'].get('tool_total')))
out.append('cost_sum[0]: ' + repr(data['sheet3']['cost_sum'][0]))
out.append('cost_sum all: ' + repr(data['sheet3']['cost_sum']))
out.append('mold: ' + repr(data['sheet3'].get('mold')))
out.append('customer_supply[0]: ' + repr(data['customer_supply'][0]))
out.append('smt: ' + repr(data['sheet3'].get('smt')))
out.append('soft/hard/exp: ' + repr([data['sheet3'].get(k) for k in ('soft', 'hard', 'exp')]))

with open('/workspace/recon_dump.txt', 'w') as f:
    f.write('\n'.join(out))
print('OK', len(out), 'lines')
