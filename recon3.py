import json, collections
d = json.load(open('/workspace/source_extract.json'))
b = d['bom']
for k in ['hardware', 'structure', 'packaging', 'aux']:
    rows = b[k]
    tot = sum((r.get('amt') or 0) for r in rows)
    print(f'--- {k}: n={len(rows)} amt_sum={tot!r}')
    print('   keys:', sorted(rows[0].keys()))
    print('   first:', rows[0])
    print('   last:', rows[-1])
aux_real = [r for r in b['aux'] if r.get('code') != '合计']
print('aux_real n=', len(aux_real), 'sum=', sum((r.get('amt') or 0) for r in aux_real))
print()
print('=== customer_supply raw ===')
for r in d['customer_supply']:
    print(r)
print()
print('=== sheet1_e ===')
for r in d['sheet1_e']:
    print(r)
