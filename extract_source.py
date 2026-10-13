import json
from openpyxl import load_workbook

SRC = '/workspace/.uploads/cc030d46-2ad1-4732-b4d0-d438692ca0d0_成本分解-8-26.xlsx'
wb = load_workbook(SRC, data_only=True)

out = {}

# ---------- Sheet2 BOM ----------
s2 = wb['Sheet2']
def g(ws, r, c):
    v = ws.cell(row=r, column=c).value
    if v is None:
        return None
    if isinstance(v, float):
        return round(v, 10)
    return v

# 硬件 rows 16-287, 结构 rows 289-320 (A序号 B类型 C编码 D名称 G用量 L供应商 M单价 N损耗)
hw = []
for r in range(16, 288):
    row = dict(seq=g(s2,r,1), code=g(s2,r,3), name=g(s2,r,4), level=g(s2,r,5), form=g(s2,r,6),
               qty=g(s2,r,7), supplier=g(s2,r,12), price=g(s2,r,13), loss=g(s2,r,14), amt=g(s2,r,15))
    if row['code'] is None and row['name'] is None:
        continue
    hw.append(row)
st = []
for r in range(289, 321):
    row = dict(seq=g(s2,r,1), code=g(s2,r,3), name=g(s2,r,4), level=g(s2,r,5), form=g(s2,r,6),
               qty=g(s2,r,7), supplier=g(s2,r,12), price=g(s2,r,13), loss=g(s2,r,14), amt=g(s2,r,15))
    if row['code'] is None and row['name'] is None:
        continue
    st.append(row)
# 新包装 rows 347-354; header row 346; W351/W352=16667 (EPS模具含税)
pk = []
for r in range(347, 356):
    row = dict(code=g(s2,r,3), name=g(s2,r,4), qty=g(s2,r,7), supplier=g(s2,r,12),
               price=g(s2,r,13), loss=g(s2,r,14), amt=g(s2,r,15), mold_w=g(s2,r,23))
    if row['code'] is None and row['name'] is None:
        continue
    pk.append(row)
# 新辅料 rows 359-374: H代码 I名称 J数量 K单位 L单价 M金额 N备注
fl = []
for r in range(359, 376):
    row = dict(code=g(s2,r,8), name=g(s2,r,9), qty=g(s2,r,10), unit=g(s2,r,11),
               price=g(s2,r,12), amt=g(s2,r,13), note=g(s2,r,14))
    if row['code'] is None and row['name'] is None:
        continue
    fl.append(row)
out['bom'] = dict(hardware=hw, structure=st, packaging=pk, aux=fl)

# ---------- Sheet3 J-O blocks ----------
s3 = wb['Sheet3']
def gj(r, c):  # columns J=10..O=15, P=16
    return g(s3, r, c)

smt = []
for r in range(3, 8):
    smt.append(dict(name=gj(r,10), spec=gj(r,11), qty=gj(r,12), price=gj(r,13), amt=gj(r,14)))
labor_hdr = dict(cols=[gj(11,c) for c in range(10,16)])
labor = []
for r in range(12, 64):
    labor.append(dict(seg=gj(r,10), cat=gj(r,11), quota=gj(r,12), proc=gj(r,13),
                      persons=gj(r,14), cost=gj(r,15)))
labor_total = gj(64,15)
tooling_hdr = [gj(69,c) for c in range(10,17)]
tooling = []
for r in range(70, 87):
    tooling.append(dict(tech=gj(r,10), name=gj(r,11), qty=gj(r,12), price=gj(r,13),
                        annual=gj(r,14), unit_cost=gj(r,15), amt=gj(r,16)))
tool_total = gj(86,16)
tool_note = gj(86,10) or gj(87,10)
cost_sum = []
for r in range(88, 104):
    cost_sum.append(dict(name=gj(r,10), unit=gj(r,11), qty=gj(r,12), val=gj(r,13), note=gj(r,14)))
mold = []
for r in range(106, 112):
    mold.append(dict(name=gj(r,10), qty=gj(r,11), unit=gj(r,12), price=gj(r,13), amt=gj(r,14), note=gj(r,15)))
soft = []
for r in range(113, 119):
    soft.append([gj(r,c) for c in range(10,16)])
hard = []
for r in range(120, 126):
    hard.append([gj(r,c) for c in range(10,16)])
exp = []
for r in range(127, 133):
    exp.append([gj(r,c) for c in range(10,16)])
out['sheet3'] = dict(smt=smt, labor_hdr=labor_hdr, labor=labor, labor_total=labor_total,
                     tooling_hdr=tooling_hdr, tooling=tooling, tool_total=tool_total, tool_note=tool_note,
                     cost_sum=cost_sum, mold=mold, soft=soft, hard=hard, exp=exp)

# ---------- 客供料 (full dump rows 1-12, all cols) ----------
sk = wb['客供料']
cust = []
for r in range(1, 13):
    row = [g(sk, r, c) for c in range(1, 12)]
    if any(v is not None for v in row):
        cust.append(dict(row=r, vals=row))
out['customer_supply'] = cust

# ---------- Sheet1 E-column anchors for reconciliation ----------
s1 = wb['Sheet1']
e = {}
for r in range(10, 46):
    v = s1.cell(row=r, column=5).value
    label = s1.cell(row=r, column=1).value or s1.cell(row=r, column=3).value
    if v is not None:
        e[r] = dict(label=str(label)[:30] if label else '', val=round(v,8) if isinstance(v,float) else v)
out['sheet1_e'] = e

with open('/workspace/source_extract.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)

print('hardware', len(hw), 'structure', len(st), 'packaging', len(pk), 'aux', len(fl))
print('labor rows', len(labor), 'total', labor_total, 'tool_total', tool_total)
print('smt', smt)
print('mold', mold)
print('cost_sum sample', cost_sum[:3], cost_sum[-2:])
print('cust', cust)
print('E-col', e)
