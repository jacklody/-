#!/usr/bin/env python3
"""产品成本测算报价 agent（CLI + MCP server）。

与《产品成本测算报价表.xlsx》共用同一参数源：运行时直接读取工作簿的
《参数》《跨越费率》《包装计算》档位表，保证口径一致。

用法：
  python3 quote_cli.py quote --length 380 --width 320 --height 150 --weight 4 \
      --per-box 4 --heatsink 是 --pallet 是 --product 次日达 --dest 宁波 --per-ship 50
  python3 quote_cli.py quote ... --json          # JSON 输出（供程序调用）
  python3 quote_cli.py export ... --out 报价.xlsx # 把输入填进工作簿副本，Excel 打开自动重算
  python3 quote_cli.py serve                      # 以 MCP server 方式运行（stdio）
"""
import argparse
import bisect
import json
import shutil
import sys

WORKBOOK = '/workspace/产品成本测算报价表.xlsx'

BANDS = [(0, 200, 15, '单瓦楞3层'), (200, 350, 20, '双瓦楞5层'),
         (350, 550, 25, '双瓦楞5层'), (550, 10**9, 30, '重型7层')]
BAND_LO = [b[0] for b in BANDS]
SEG_BOUNDS = {
    '次日达': [1, 10, 30, 50, 100, 300, 500, 1000, 2000],
    '特惠普运': [1, 50, 100, 200, 300, 500, 1000, 2000],
}


def load_model(wb_path=WORKBOOK):
    import openpyxl
    wb = openpyxl.load_workbook(wb_path, data_only=True)
    wp = wb['参数']
    p = {wp.cell(r, 1).value: wp.cell(r, 2).value for r in range(2, 50)
         if wp.cell(r, 1).value}
    wk = wb['跨越费率']
    rates = []
    for r in range(4, wk.max_row + 1):
        row = [wk.cell(r, c).value for c in range(1, 18)]
        if row[0]:
            rates.append(row)
    return p, rates


def compute(inputs, wb_path=WORKBOOK):
    p, rates = load_model(wb_path)
    L = float(inputs['length']); W = float(inputs['width']); H = float(inputs['height'])
    weight = float(inputs['weight']); N = int(inputs['per_box'])
    M = int(inputs['per_ship'])
    pallet = inputs.get('pallet', '否') == '是'
    big = inputs.get('heatsink', '否') == '是' or inputs.get('assembly', '否') == '是'
    scheme = '大板' if big else '小板'

    t = BANDS[bisect.bisect_right(BAND_LO, max(L, W, H)) - 1][2]
    corr = BANDS[bisect.bisect_right(BAND_LO, max(L, W, H)) - 1][3]
    gap = float(p['箱内装配间隙'])
    box_l = L + 2 * t + gap
    box_w = W + 2 * t + gap
    box_h = N * (H + 2 * t) + gap
    box_vol_cm3 = box_l * box_w * box_h / 1000.0

    m = float(p['气泡袋单边余量'])
    bag_area = (L + H + 2 * m) * (W + H + 2 * m) / 1e6
    bag_fee = bag_area * float(p['防静电气泡袋单价'])
    divider_fee = float(p['隔板单价']) * max(N - 1, 0) / N if not big else 0.0
    epe_vol = (2 * L * W * t + 4 * t * t * H) / 1e9 if big else 0.0
    epe_fee = epe_vol * float(p['EPE珍珠棉单价'])
    inner_fee = (bag_fee + divider_fee) if not big else epe_fee

    loss = float(p['材料损耗率'])
    paper_area = (box_l + box_w) * 2 * (box_w + 2 * box_h) / 1e6 * (1 + loss)
    price_map = {'单瓦楞3层': p['单瓦楞3层纸板'], '双瓦楞5层': p['双瓦楞5层纸板'],
                 '重型7层': p['重型7层纸板']}
    carton_box_fee = paper_area * float(price_map[corr]) + float(p['纸箱制箱加工费'])
    carton_unit = carton_box_fee / N
    aux_unit = (float(p['封箱胶带']) + float(p['标签'])) / N

    box_foot = box_l * box_w / 1e6
    per_pallet = int(float(p['托盘有效面积']) / box_foot) * int(p['每托层数']) if box_foot else 0
    pallet_box_fee = (float(p['护角']) + float(p['托盘单价']) / float(p['托盘重复使用次数'])
                      + float(p['缠绕膜单价']) * float(p['缠绕膜用量'])
                      + (float(p['打包带']) if big else 0.0))
    pallet_unit = pallet_box_fee / per_pallet if (pallet and per_pallet) else 0.0

    if big:
        pack_added = epe_vol * float(p['EPE珍珠棉密度'])
    else:
        pack_added = bag_area * float(p['防静电气泡袋克重']) / 1000.0
    pack_added += paper_area * float(p['双瓦楞纸板克重']) / 1000.0 / N
    if not big:
        pack_added += float(p['隔板克重']) / 1000.0 * max(N - 1, 0) / N
    pack_added += 0.005

    pack_total = inner_fee + carton_unit + aux_unit + pallet_unit

    gross = weight + pack_added
    boxes = M / N
    real_w = gross * M
    vol_w = box_vol_cm3 * boxes / float(p['体积重系数'])
    billable = max(real_w, vol_w)

    freight = {'matched': False}
    product = inputs.get('product', ''); dest = inputs.get('dest', '')
    row = None
    if product and dest:
        for rr in rates:
            if rr[0] == product and rr[16] and dest in str(rr[16]):
                row = rr
                break
    if row:
        first_w = float(row[3]); first_p = float(row[4])
        lift = float(row[5] or 0); min_charge = float(row[6] or 0)
        billable2 = max(billable, lift)
        bounds = SEG_BOUNDS.get(product, SEG_BOUNDS['次日达'])
        idx = bisect.bisect_right(bounds, billable2) - 1
        idx = max(idx, 0)
        seg_price = float(row[7 + idx])
        ticket = max(first_p + (billable2 - first_w) * seg_price, min_charge)
        ins_on = str(p.get('是否计保费', '否')) == '是'
        declared = inputs.get('declared_value')
        insurance = 0.0
        if ins_on and declared is not None:
            insurance = max(float(p['保费费率']) * float(declared),
                            float(p['保费最低收费']))
        ticket_total = ticket + insurance
        freight = {
            'matched': True, 'rate_key': row[16], 'boxes': boxes,
            'real_weight_kg': round(real_w, 3), 'vol_weight_kg': round(vol_w, 3),
            'billable_weight_kg': round(billable2, 3), 'seg_index': idx + 1,
            'seg_price': seg_price, 'ticket_freight': round(ticket, 2),
            'insurance': round(insurance, 2),
            'ticket_total': round(ticket_total, 2),
            'per_unit': round(ticket_total / M, 4),
        }

    assembly_fee = 0.0
    if inputs.get('assembly') == '是':
        tact = float(inputs.get('assembly_tact', 0) or 0)
        labor = float(inputs.get('labor_rate', p['默认装配工时费']))
        assembly_fee = tact / 3600.0 * labor

    return {
        'scheme': scheme, 'buffer_t_mm': t, 'corrugated': corr,
        'box_inner_mm': [round(box_l), round(box_w), round(box_h)],
        'box_vol_cm3': round(box_vol_cm3, 1),
        'packaging': {
            'bag_fee': round(bag_fee, 4), 'divider_fee': round(divider_fee, 4),
            'epe_vol_m3': round(epe_vol, 6), 'epe_fee': round(epe_fee, 4),
            'inner_fee': round(inner_fee, 4),
            'carton_per_box': round(carton_box_fee, 4),
            'carton_per_unit': round(carton_unit, 4),
            'aux_per_unit': round(aux_unit, 4),
            'per_pallet_units': per_pallet,
            'pallet_per_unit': round(pallet_unit, 4),
            'added_weight_kg': round(pack_added, 4),
            'total_per_unit': round(pack_total, 4),
        },
        'freight': freight,
        'assembly_fee_per_unit': round(assembly_fee, 4),
        'pack_plus_freight_per_unit': round(
            pack_total + (freight.get('per_unit') or 0), 4),
    }


def render_text(res, inputs):
    pk = res['packaging']; fr = res['freight']
    lines = []
    lines.append(f"包装方案: {res['scheme']}  缓冲厚度: {res['buffer_t_mm']}mm  瓦楞: {res['corrugated']}")
    lines.append(f"箱内尺寸: {res['box_inner_mm'][0]}×{res['box_inner_mm'][1]}×{res['box_inner_mm'][2]} mm  单箱体积: {res['box_vol_cm3']} cm³")
    lines.append('--- 包装费（元/件） ---')
    if res['scheme'] == '小板':
        lines.append(f"  气泡袋 {pk['bag_fee']} + 隔板 {pk['divider_fee']}")
    else:
        lines.append(f"  EPE(垫片+护角) 体积 {pk['epe_vol_m3']} m³ → {pk['epe_fee']}")
    lines.append(f"  纸箱 {pk['carton_per_unit']}（{pk['carton_per_box']} 元/箱） + 辅料 {pk['aux_per_unit']}")
    if pk['pallet_per_unit']:
        lines.append(f"  整托分摊 {pk['pallet_per_unit']}（每托 {pk['per_pallet_units']} 件）")
    lines.append(f"  包装费合计: {pk['total_per_unit']} 元/件（包装增重 {pk['added_weight_kg']} kg/件）")
    lines.append('--- 运费 ---')
    if fr['matched']:
        lines.append(f"  费率行: {fr['rate_key']}")
        lines.append(f"  实重 {fr['real_weight_kg']}kg / 体积重 {fr['vol_weight_kg']}kg → 计费重 {fr['billable_weight_kg']}kg（段{fr['seg_index']} 单价 {fr['seg_price']}）")
        lines.append(f"  单票运费 {fr['ticket_freight']} + 保费 {fr['insurance']} = {fr['ticket_total']} 元/票")
        lines.append(f"  单台运费: {fr['per_unit']} 元/件")
    else:
        lines.append('  未匹配到费率（检查物流产品/目的地；特惠普运与次日达覆盖城市不同）')
    if res['assembly_fee_per_unit']:
        lines.append(f"--- 装配费: {res['assembly_fee_per_unit']} 元/件 ---")
    lines.append(f"包装+运费合计: {res['pack_plus_freight_per_unit']} 元/件")
    lines.append('注: 材料/加工/工装/利润/税需在完整工作簿中计算，可用 export 命令生成。')
    return '\n'.join(lines)


def do_export(res_inputs, out_path, wb_path=WORKBOOK):
    import openpyxl
    shutil.copy(wb_path, out_path)
    wb = openpyxl.load_workbook(out_path)
    ws = wb['报价汇总']
    mapping = {
        'code': 'B4', 'name': 'B5', 'customer': 'B6', 'annual_demand': 'B8', 'moq': 'B9',
        'length': 'B13', 'width': 'B14', 'height': 'B15', 'weight': 'B16',
        'per_box': 'B17', 'pallet': 'B18', 'heatsink': 'B19', 'assembly': 'B20',
        'assembly_tact': 'E20', 'labor_rate': 'G20',
        'product': 'B22', 'dest': 'B23', 'per_ship': 'B24', 'declared_value': 'B25',
    }
    for key, cell in mapping.items():
        if res_inputs.get(key) is not None:
            ws[cell] = res_inputs[key]
    wb.save(out_path)
    return out_path


def collect_inputs(a):
    return {
        'code': a.code, 'name': a.name, 'customer': a.customer,
        'annual_demand': a.annual_demand, 'moq': a.moq,
        'length': a.length, 'width': a.width, 'height': a.height,
        'weight': a.weight, 'per_box': a.per_box, 'pallet': a.pallet,
        'heatsink': a.heatsink, 'assembly': a.assembly,
        'assembly_tact': a.assembly_tact, 'labor_rate': a.labor_rate,
        'product': a.product, 'dest': a.dest, 'per_ship': a.per_ship,
        'declared_value': a.declared_value,
    }


def add_args(sp):
    sp.add_argument('--length', type=float, required=True, help='成品长mm')
    sp.add_argument('--width', type=float, required=True, help='成品宽mm')
    sp.add_argument('--height', type=float, required=True, help='成品高mm')
    sp.add_argument('--weight', type=float, required=True, help='单台净重kg')
    sp.add_argument('--per-box', dest='per_box', type=int, required=True, help='每箱件数N')
    sp.add_argument('--pallet', default='否', choices=['是', '否'], help='是否含整托分摊')
    sp.add_argument('--heatsink', default='否', choices=['是', '否'], help='是否带散热器')
    sp.add_argument('--assembly', default='否', choices=['是', '否'], help='是否带组装结构')
    sp.add_argument('--assembly-tact', dest='assembly_tact', type=float, default=None, help='装配节拍秒/台')
    sp.add_argument('--labor-rate', dest='labor_rate', type=float, default=None, help='装配工时费元/小时')
    sp.add_argument('--product', default=None, choices=['次日达', '特惠普运'], help='物流产品')
    sp.add_argument('--dest', default=None, help='目的地城市名，如 宁波')
    sp.add_argument('--per-ship', dest='per_ship', type=int, required=True, help='每票件数M')
    sp.add_argument('--declared-value', dest='declared_value', type=float, default=None, help='声明价值元/票')
    sp.add_argument('--code', default=None, help='产品代码')
    sp.add_argument('--name', default=None, help='产品名称')
    sp.add_argument('--customer', default=None, help='客户名称')
    sp.add_argument('--annual-demand', dest='annual_demand', type=int, default=None, help='年需求量')
    sp.add_argument('--moq', type=int, default=None, help='MOQ')
    sp.add_argument('--workbook', default=WORKBOOK, help='参数源工作簿路径')


def quote_from_dict(d):
    wb_path = d.pop('workbook', WORKBOOK)
    for k in ('length', 'width', 'height', 'weight', 'per_box', 'per_ship'):
        d[k] = float(d[k]) if k != 'per_box' and k != 'per_ship' else int(float(d[k]))
    return compute(d, wb_path)


def serve_mcp(wb_path=WORKBOOK):
    tool = {
        'name': 'quote',
        'description': '产品包装费/运费/装配费快速测算（与《产品成本测算报价表.xlsx》同参数源）。'
                       '输入成品尺寸(mm)、净重(kg)、每箱件数、每票件数、散热器/组装/整托选项、'
                       '物流产品(次日达/特惠普运)、目的地城市，返回包装与运费明细。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'length': {'type': 'number', 'description': '成品长mm'},
                'width': {'type': 'number', 'description': '成品宽mm'},
                'height': {'type': 'number', 'description': '成品高mm'},
                'weight': {'type': 'number', 'description': '单台净重kg'},
                'per_box': {'type': 'integer', 'description': '每箱件数N'},
                'per_ship': {'type': 'integer', 'description': '每票件数M'},
                'pallet': {'type': 'string', 'enum': ['是', '否'], 'description': '是否含整托分摊'},
                'heatsink': {'type': 'string', 'enum': ['是', '否'], 'description': '是否带散热器'},
                'assembly': {'type': 'string', 'enum': ['是', '否'], 'description': '是否带组装结构'},
                'assembly_tact': {'type': 'number', 'description': '装配节拍秒/台'},
                'labor_rate': {'type': 'number', 'description': '装配工时费元/小时'},
                'product': {'type': 'string', 'enum': ['次日达', '特惠普运'], 'description': '物流产品'},
                'dest': {'type': 'string', 'description': '目的地城市名'},
                'declared_value': {'type': 'number', 'description': '声明价值元/票'},
            },
            'required': ['length', 'width', 'height', 'weight', 'per_box', 'per_ship'],
        },
    }

    def send(msg):
        sys.stdout.write(json.dumps(msg, ensure_ascii=False) + '\n')
        sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = msg.get('id'); method = msg.get('method', '')
        if method == 'initialize':
            send({'jsonrpc': '2.0', 'id': mid, 'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {'tools': {}},
                'serverInfo': {'name': 'quote-agent', 'version': '1.0.0'}}})
        elif method == 'notifications/initialized':
            continue
        elif method == 'tools/list':
            send({'jsonrpc': '2.0', 'id': mid, 'result': {'tools': [tool]}})
        elif method == 'tools/call':
            name = msg.get('params', {}).get('name')
            args = dict(msg.get('params', {}).get('arguments', {}))
            if name != 'quote':
                send({'jsonrpc': '2.0', 'id': mid,
                      'error': {'code': -32601, 'message': f'unknown tool {name}'}})
                continue
            try:
                res = quote_from_dict(args)
                text = render_text(res, args) + '\n\nJSON:\n' + json.dumps(res, ensure_ascii=False, indent=1)
                send({'jsonrpc': '2.0', 'id': mid, 'result': {
                    'content': [{'type': 'text', 'text': text}], 'isError': False}})
            except Exception as e:
                send({'jsonrpc': '2.0', 'id': mid, 'result': {
                    'content': [{'type': 'text', 'text': f'计算失败: {e}'}], 'isError': True}})
        elif mid is not None:
            send({'jsonrpc': '2.0', 'id': mid,
                  'error': {'code': -32601, 'message': f'method not found: {method}'}})


def main():
    ap = argparse.ArgumentParser(description='产品成本测算报价 agent')
    sub = ap.add_subparsers(dest='cmd', required=True)

    pq = sub.add_parser('quote', help='计算包装费/运费并输出')
    add_args(pq)
    pq.add_argument('--json', action='store_true', help='JSON 输出')

    pe = sub.add_parser('export', help='把输入填进工作簿副本（Excel 打开自动重算全部报价）')
    add_args(pe)
    pe.add_argument('--out', default='/workspace/报价单-导出.xlsx', help='输出路径')

    ps = sub.add_parser('serve', help='以 MCP server 方式运行（stdio, JSON-RPC）')
    ps.add_argument('--workbook', default=WORKBOOK)

    a = ap.parse_args()
    if a.cmd == 'serve':
        serve_mcp(a.workbook)
        return
    inputs = collect_inputs(a)
    res = compute(inputs, a.workbook)
    if a.cmd == 'quote':
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            print(render_text(res, inputs))
    elif a.cmd == 'export':
        out = do_export(inputs, a.out, a.workbook)
        print(f'已导出: {out}（用 Excel/WPS 打开自动重算，含完整报价：材料/加工/利润/税）')


if __name__ == '__main__':
    main()
