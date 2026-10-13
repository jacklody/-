import openpyxl
wb = openpyxl.load_workbook('/workspace/产品成本测算报价表.xlsx')
print('sheets:', wb.sheetnames)
for nm in ['包装计算', '运费计算']:
    ws = wb[nm]
    print(f'=== {nm} max_row={ws.max_row} merges={sorted(str(m) for m in ws.merged_cells.ranges)}')
    for r in range(1, ws.max_row + 1):
        vals = []
        for c in range(1, 9):
            v = ws.cell(row=r, column=c).value
            if v is not None and v != '':
                vals.append(f'{ws.cell(row=r,column=c).coordinate}={v!r}')
        if vals:
            print(' ', ' | '.join(vals)[:300])
ws = wb['报价汇总']
print('=== 报价汇总 A/B rows1-26')
for r in range(1, 27):
    a = ws.cell(row=r, column=1).value
    b = ws.cell(row=r, column=2).value
    print(f'  {r}: A={a!r} B={b!r}')
print('=== 物料明细 all rows A-D,I,J')
ws = wb['物料明细']
for r in range(1, ws.max_row + 1):
    row = [ws.cell(row=r, column=c).value for c in (1, 2, 3, 4, 5, 6, 7, 9, 10)]
    if any(v not in (None, '') for v in row):
        print(' ', r, row)
print('=== DVs 物料明细', [ (dv.sqref, dv.formula1) for dv in ws.data_validations.dataValidation])
