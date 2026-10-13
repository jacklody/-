import json
import subprocess
import sys

import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

WB = '/workspace/产品成本测算报价表.xlsx'
RECALC = '/data/user/plugins/trae-remote-official/office-plugin/0.1.0/skills/xlsx/scripts/recalc.py'
SRC = '/workspace/source_extract.json'

F_NAME = '微软雅黑'
BLUE = 'FF0000FF'
BLACK = 'FF000000'
GREEN = 'FF008000'
WHITE = 'FFFFFFFF'
GREY = 'FF808080'
FILL_TITLE = PatternFill('solid', fgColor='FF0F3B5D')
FILL_SEC = PatternFill('solid', fgColor='FF3288B9')
FILL_KPI = PatternFill('solid', fgColor='FFEAF2FF')
FILL_ZEBRA = PatternFill('solid', fgColor='FFF7F9FC')
FILL_NONE = PatternFill(fill_type=None)
THIN = Side(style='thin', color='FFD9DEE7')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

FMT_MONEY = '#,##0.0000'
FMT_MONEY2 = '#,##0.00'
FMT_PRICE = '#,##0.000000'
FMT_QTY = '#,##0.######'
FMT_PCT = '0.00%'


def font(size=10, bold=False, color=BLACK):
    return Font(name=F_NAME, size=size, bold=bold, color=color)


d = json.load(open(SRC))
bom = d['bom']
s3 = d['sheet3']

wb = openpyxl.load_workbook(WB)

# =====================================================================
# 1) 参数：新增商空专用参数 + 毛利率对齐源表
# =====================================================================
wp = wb['参数']
wp['B4'] = 0.3  # 目标毛利率（源表建议毛利率0.3）

param_rows = [
    (48, '五、商空大功率项目专用参数', None, 'sec'),
    (49, '散热器单价(未税,元)', 68, 'blue'),
    (50, '成本差异率(制造损耗缓冲)', 0.0135, 'blue'),
    (51, '运费费率(跨越不覆盖时备用)', 0.0116, 'blue'),
    (52, '成本内利润加成率(商空默认0)', 0, 'blue'),
    (53, 'EPS泡沫模具费(一次性,元)', 29499.1150442478, 'blue'),
    (54, '工装治具费(一次性,直接收取,元)', 48700, 'blue'),
    (55, '客供料合计(参考,不计入成本,元)', 554.3197, 'grey'),
]
for r, label, val, kind in param_rows:
    a = wp.cell(r, 1)
    a.value = label
    if kind == 'sec':
        a.font = font(10, True, WHITE)
        a.fill = FILL_SEC
        wp.cell(r, 2).fill = FILL_SEC
    else:
        a.font = font(10)
        a.border = BORDER
        b = wp.cell(r, 2)
        b.value = val
        b.border = BORDER
        if kind == 'blue':
            b.font = font(10, color=BLUE)
        else:
            b.font = font(10, color=GREY)
        if isinstance(val, float) and val < 1:
            b.number_format = FMT_PCT if 'rate' in label or '率' in label else FMT_MONEY
        else:
            b.number_format = FMT_MONEY2
# 修正百分比格式
wp['B50'].number_format = FMT_PCT
wp['B51'].number_format = FMT_PCT
wp['B52'].number_format = FMT_PCT
wp['B49'].number_format = FMT_MONEY2
wp['B53'].number_format = FMT_MONEY2
wp['B54'].number_format = FMT_MONEY2
wp['B55'].number_format = FMT_MONEY2

# =====================================================================
# 2) 物料明细：导入 硬件/结构件/散热器/包装材料/辅助材料/客供料
# =====================================================================
wm = wb['物料明细']
# 清除旧数据行
old_max = wm.max_row
for r in range(3, max(old_max, 340) + 1):
    for c in range(1, 11):
        cell = wm.cell(r, c)
        cell.value = None
        cell.fill = FILL_NONE
        cell.border = Border()
# 移除旧DV与autofilter，稍后重建
wm.data_validations.dataValidation = []
wm.auto_filter.ref = None

HDR = ['序号', '物料分类', '物料编码', '物料名称规格', '单机用量',
       '未税单价', '损耗率', '金额', '是否客供', '备注']
for c, h in enumerate(HDR, 1):
    cell = wm.cell(2, c)
    cell.value = h
    cell.font = font(10, True)
    cell.fill = FILL_KPI
    cell.border = BORDER
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

rows = []  # (分类, 编码, 名称, 用量, 单价, 损耗, 客供, 备注)

for it in bom['hardware']:
    sup = it.get('supplier')
    is_cust = not it.get('price')
    note = sup
    if is_cust:
        note = ('客供料(源BOM单价0，不计入成本)；' + str(sup or '')).strip('；')
    rows.append(('硬件', it.get('code'), it.get('name'), it.get('qty'),
                 it.get('price'), None, '是' if is_cust else '否', note))
for it in bom['structure']:
    rows.append(('结构件', it.get('code'), it.get('name'), it.get('qty'),
                 it.get('price'), None, '否', it.get('supplier')))
# 散热器（单独采购68元未税，源表未含）
rows.append(('散热器', 'HS-DRV26P', '散热器（商空大功率驱动板，单独采购，未税）',
             1, '=参数!$B$49', None, '否', '源表未含，按68元未税单列'))
for it in bom['packaging']:
    note = it.get('supplier') or ''
    if it.get('mold_w'):
        note = (note + '；含EPS泡沫模具(见一次性费用)').strip('；')
    rows.append(('包装材料', it.get('code'), it.get('name'), it.get('qty'),
                 it.get('price'), None, '否', note))
for it in bom['aux'][:-1]:  # 末行合计剔除
    note = ' '.join(x for x in [it.get('unit'), it.get('note')] if x)
    rows.append(('辅助材料', it.get('code'), it.get('name'), it.get('qty'),
                 it.get('price'), None, '否', note))
# 客供料（8颗，核算成本已扣除）
for cs in d['customer_supply']:
    if cs['row'] < 3 or cs['row'] > 10:
        continue
    v = cs['vals']
    name = ' '.join(x for x in [v[1], v[2]] if x)
    note = ' '.join(str(x) for x in [v[6], v[9], v[10]] if x)
    rows.append(('客供料', f"客供{v[0]}", name, v[4], v[8], None, '是',
                 f'客供不计入报价；{note}'))

r = 3
for (cat, code, name, qty, price, loss, cust, note) in rows:
    zebra = FILL_ZEBRA if (r % 2 == 0) else FILL_NONE
    vals = [f'=IF(C{r}<>"",ROW()-2,"")', cat, code, name, qty, price, loss,
            f'=IF(I{r}="是",0,IF(OR(E{r}="",F{r}=""),0,E{r}*F{r}*(1+IF(G{r}="",0,G{r}))))',
            cust, note]
    for c, val in enumerate(vals, 1):
        cell = wm.cell(r, c)
        cell.value = val
        cell.border = BORDER
        cell.fill = zebra
        cell.alignment = Alignment(vertical='center', wrap_text=(c in (4, 10)))
        if c == 1:
            cell.font = font(9, color=GREY)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        elif c == 2:
            cell.font = font(9)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        elif c in (5,):
            cell.font = font(9, color=BLUE)
            cell.number_format = FMT_QTY
        elif c in (6,):
            cell.font = font(9, color=BLUE) if not (isinstance(price, str)) else font(9, color=GREEN)
            cell.number_format = FMT_PRICE
        elif c == 7:
            cell.font = font(9, color=BLUE)
            cell.number_format = FMT_PCT
        elif c == 8:
            cell.font = font(9)
            cell.number_format = FMT_MONEY
        elif c == 9:
            cell.font = font(9)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        else:
            cell.font = font(9, color=GREY)
    wm.row_dimensions[r].height = 13.5
    r += 1
LAST = r - 1

wm.auto_filter.ref = f'A2:J{LAST}'
dv = DataValidation(type='list', formula1='"否,是"', allow_blank=True)
wm.add_data_validation(dv)
dv.add(f'I3:I{LAST}')

print('物料明细 rows written =', len(rows), 'last row =', LAST)

# =====================================================================
# 3) 制费明细：轻量修正（G3联动、P06/P07清零、加注释）
# =====================================================================
wz_fee = wb['制费明细']
wz_fee['G3'] = '=报价汇总!B8'
wz_fee['G3'].font = font(color=GREEN)
wz_fee['H3'] = '联动报价汇总年需求量(B8)；夹具一次性费用分摊分母'
wz_fee['H3'].font = font(9, color=GREY)
# P06 辅料用量清零（辅料已计入BOM辅助材料，避免重复）
for rr in range(66, 73):
    wz_fee.cell(rr, 5).value = 0
wz_fee['A64'] = ('P06 辅料费｜注：商空项目辅料用量已置0，辅料已导入BOM「辅助材料」，'
                 '此处避免与报价汇总重复计费')
wz_fee['A64'].font = font(9, color=GREY)
# P07 夹具张数清零（工装直接向客户收取，见报价汇总六、一次性费用）
for rr in range(77, 89):
    wz_fee.cell(rr, 5).value = 0
wz_fee['A75'] = ('P07 治具/夹具费｜注：商空项目夹具张数已置0，工装48700元直接向客户收取，'
                 '见报价汇总「六、一次性费用」，不计入单台成本')
wz_fee['A75'].font = font(9, color=GREY)
wz_fee['A1'] = ('制费明细（工程报价表格式 P01~P07：自下而上工序估算工具）'
                '｜注：商空项目加工成本以「加工成本明细」综合表为准')

# =====================================================================
# 4) 新表：加工成本明细（综合加工成本 + 人工定额 + 工装明细）
# =====================================================================
if '加工成本明细' in wb.sheetnames:
    del wb['加工成本明细']
idx = wb.sheetnames.index('制费明细') + 1
wg = wb.create_sheet('加工成本明细', idx)
for col, w in zip('ABCDEF', [8, 26, 16, 14, 14, 40]):
    wg.column_dimensions[col].width = w


def gput(cell, value, f=None, fill=None, fmt=None, align=None, border=True):
    c = wg[cell]
    if not isinstance(c, MergedCell):
        c.value = value
    c.font = f or font()
    if fill:
        c.fill = fill
    if fmt:
        c.number_format = fmt
    c.alignment = align or Alignment(vertical='center', wrap_text=True)
    if border:
        c.border = BORDER
    return c


def gtitle(row, text, span=6):
    wg.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    gput(f'A{row}', text, font(11, True, WHITE), FILL_SEC, border=False)


def gheader(row, headers):
    for i, h in enumerate(headers, 1):
        gput(f'{get_column_letter(i)}{row}', h, font(10, True), FILL_KPI,
             align=Alignment(horizontal='center', vertical='center', wrap_text=True))


wg.merge_cells('A1:F1')
gput('A1', '加工成本明细（商空大功率驱动板·综合加工成本构成）',
     font(14, True, WHITE), FILL_TITLE, border=False)
wg.row_dimensions[1].height = 26

# --- Block A: 综合加工成本构成 ---
gtitle(3, '一、加工成本构成（元/台，综合口径：人工+制费+SMT/机插）')
gheader(4, ['序号', '成本组成', '金额(元/台)', '', '', '说明'])
wg.merge_cells('C4:E4')
cost_items = [
    ('贴片加工成本', 6.1656, 'SMT贴片 1101.001点×0.0056'),
    ('机插加工成本', 0.2394, 'AI机插 14点×0.0171'),
    ('预烧写加工成本', 0, '本项目无'),
    ('人工成本', 82.0882, '插焊/测试/组装等直接人工（详见二）'),
    ('折旧（专用）', 0.8424, '专用设备折旧'),
    ('折旧（公共）', 2.2, '公共设备折旧分摊'),
    ('水电（专用）', 1.4745, '专用水电'),
    ('水电（公共）', 1.4776, '公共水电分摊'),
    ('工装', 0, '工装直接向客户收取（详见三），不计入单台'),
    ('低值易耗', 4.5477, '低值易耗品摊销'),
    ('管理人员工资', 21.3676, '制造管理费用分摊'),
    ('其他', 6.0253, '其他制造费用'),
    ('检验成本', 0, '本项目未单列'),
]
rr = 5
for i, (nm, val, note) in enumerate(cost_items, 1):
    gput(f'A{rr}', i, font(9, color=GREY), align=Alignment(horizontal='center', vertical='center'))
    gput(f'B{rr}', nm, font(10))
    wg.merge_cells(f'C{rr}:E{rr}')
    gput(f'C{rr}', val, font(10, color=BLUE), fmt=FMT_MONEY)
    for cc in ('D', 'E'):
        gput(f'{cc}{rr}', None)
    gput(f'F{rr}', note, font(9, color=GREY))
    rr += 1
COST_FIRST, COST_LAST = 5, rr - 1
gput(f'B{rr}', '加工成本合计(元/台)', font(11, True), FILL_KPI)
wg.merge_cells(f'C{rr}:E{rr}')
gput(f'C{rr}', f'=SUM(C{COST_FIRST}:C{COST_LAST})', font(11, True), FILL_KPI, FMT_MONEY)
gput(f'D{rr}', None, fill=FILL_KPI)
gput(f'E{rr}', None, fill=FILL_KPI)
gput(f'A{rr}', None, fill=FILL_KPI)
gput(f'F{rr}', '→ 报价汇总「四、成本构成」加工成本行', font(9, color=GREY), FILL_KPI)
COST_TOTAL_CELL = f'$C${rr}'
rr += 2

# --- Block B: 人工明细 ---
gtitle(rr, '二、人工工时定额明细（源表未提供逐行人工成本，人工成本合计82.0882元见上）')
rr += 1
gheader(rr, ['序号', '生产分段', '工序类别', '生产定额', '人数', '备注'])
rr += 1
labor = s3['labor']
LB_FIRST = rr
for i, lb in enumerate(labor, 1):
    gput(f'A{rr}', i, font(9, color=GREY), align=Alignment(horizontal='center', vertical='center'))
    gput(f'B{rr}', lb.get('seg'), font(9))
    gput(f'C{rr}', lb.get('cat'), font(9))
    gput(f'D{rr}', lb.get('quota'), font(9, color=BLUE), fmt='#,##0.##',
         align=Alignment(horizontal='center', vertical='center'))
    gput(f'E{rr}', lb.get('persons'), font(9, color=BLUE), fmt='#,##0.##',
         align=Alignment(horizontal='center', vertical='center'))
    gput(f'F{rr}', lb.get('proc') or None, font(9, color=GREY))
    rr += 1
LB_LAST = rr - 1
gput(f'C{rr}', '人工成本合计(元/台)', font(10, True), FILL_KPI)
gput(f'A{rr}', None, fill=FILL_KPI)
gput(f'B{rr}', None, fill=FILL_KPI)
wg.merge_cells(f'D{rr}:E{rr}')
gput(f'D{rr}', 82.0882, font(10, True), FILL_KPI, FMT_MONEY,
     align=Alignment(horizontal='center', vertical='center'))
gput(f'E{rr}', None, fill=FILL_KPI)
gput(f'F{rr}', '源表人工成本为汇总值，逐行成本不可拆分', font(9, color=GREY), FILL_KPI)
rr += 2

# --- Block C: 工装治具明细 ---
gtitle(rr, '三、工装治具明细（一次性，直接向客户收取，不计入单台成本）')
rr += 1
gheader(rr, ['序号', '工艺/名称', '数量', '单价(元)', '金额(元)', '年产能/单片分摊'])
rr += 1
TL_FIRST = rr
for i, t in enumerate(s3['tooling'][:-1], 1):  # 末行合计剔除
    gput(f'A{rr}', i, font(9, color=GREY), align=Alignment(horizontal='center', vertical='center'))
    gput(f'B{rr}', f"{t.get('tech','')}/{t.get('name','')}", font(9))
    gput(f'C{rr}', t.get('qty'), font(9, color=BLUE), fmt='#,##0',
         align=Alignment(horizontal='center', vertical='center'))
    gput(f'D{rr}', t.get('price'), font(9, color=BLUE), fmt=FMT_MONEY2)
    gput(f'E{rr}', t.get('amt'), font(9), fmt=FMT_MONEY2)
    gput(f'F{rr}', f"年{t.get('annual','')}/单片{t.get('unit_cost','')}", font(9, color=GREY))
    rr += 1
TL_LAST = rr - 1
gput(f'B{rr}', '工装治具合计(元)', font(11, True), FILL_KPI)
gput(f'A{rr}', None, fill=FILL_KPI)
gput(f'C{rr}', None, fill=FILL_KPI)
gput(f'D{rr}', None, fill=FILL_KPI)
gput(f'E{rr}', f'=SUM(E{TL_FIRST}:E{TL_LAST})', font(11, True), FILL_KPI, FMT_MONEY2)
gput(f'F{rr}', '直接向客户收取 → 报价汇总「六、一次性费用」', font(9, color=GREY), FILL_KPI)
rr += 1
gput(f'A{rr}', '制作：             审核：             核准：             批准日期：',
     font(9), border=False)

print('加工成本明细 built, 合计 cell =', COST_TOTAL_CELL, 'rows =', wg.max_row)

# =====================================================================
# 5) 报价汇总：回填输入 + 重建 四/五/六/七
# =====================================================================
wz = wb['报价汇总']
# --- 一、基础信息输入 ---
inputs = {
    'B4': 'N10305002124',
    'B5': 'DRV-26P-NJTJ(RoHS)中央式空调控制器驱动板组件',
    'B6': '青岛国创智能家电研究院有限公司',
    'B8': 5000,
    'B9': 50,
    'B10': '工装、模具费直接向客户收取；已扣除8颗客供料核算成本；散热器68元未税另计；N10305002124与N10305002125共用模具',
    'B13': 660, 'B14': 390, 'B15': 260, 'B16': 3.5, 'B17': 2,
    'B18': '是', 'B19': '是', 'B20': '是', 'E20': 12,
    'B22': '次日达', 'B23': '青岛市', 'B24': 20,
}
for k, v in inputs.items():
    wz[k] = v
    wz[k].font = font(10, color=BLUE)

# --- 清除旧 27~70 区块 ---
for m in list(wz.merged_cells.ranges):
    if m.min_row >= 27:
        wz.unmerge_cells(str(m))
for rr2 in range(27, 71):
    for cc2 in range(1, 7):
        cell = wz.cell(rr2, cc2)
        cell.value = None
        cell.fill = FILL_NONE
        cell.border = Border()


def wsec(row, text):
    wz.merge_cells(f'A{row}:E{row}')
    c = wz.cell(row, 1)
    c.value = text
    c.font = font(11, True, WHITE)
    c.fill = FILL_SEC
    c.alignment = Alignment(vertical='center')
    for cc3 in range(2, 6):
        wz.cell(row, cc3).fill = FILL_SEC


def whdr(row, headers):
    for i, h in enumerate(headers, 1):
        c = wz.cell(row, i)
        c.value = h
        c.font = font(10, True)
        c.fill = FILL_KPI
        c.border = BORDER
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)


def wline(row, name, formula, unit, note, fmt=FMT_MONEY, fcolor=GREEN):
    wz.cell(row, 1).value = name
    wz.cell(row, 1).font = font(10)
    wz.cell(row, 1).border = BORDER
    b = wz.cell(row, 2)
    b.value = formula
    b.font = font(10, color=fcolor)
    b.number_format = fmt
    b.border = BORDER
    b.alignment = Alignment(horizontal='right', vertical='center')
    c = wz.cell(row, 3)
    c.value = unit
    c.font = font(9, color=GREY)
    c.border = BORDER
    c.alignment = Alignment(horizontal='center', vertical='center')
    dd = wz.cell(row, 4)
    dd.value = note
    dd.font = font(9, color=GREY)
    dd.border = BORDER
    dd.alignment = Alignment(vertical='center', wrap_text=True)
    wz.merge_cells(start_row=row, start_column=4, end_row=row, end_column=5)
    wz.cell(row, 5).border = BORDER


CAT = lambda cat: f'=SUMIFS(物料明细!$H:$H,物料明细!$B:$B,"{cat}")'

# --- 四、成本构成 ---
wsec(27, '四、成本构成（未税/单台，自动计算）')
whdr(28, ['成本项目', '金额', '单位', '备注', '公式'])
wline(29, '硬件材料', CAT('硬件'), '元/台', '物料明细·硬件(272项)')
wline(30, '结构件', CAT('结构件'), '元/台', '物料明细·结构件(32项，含组装结构)')
wline(31, '散热器', CAT('散热器'), '元/台', '单独采购68元未税(参数B49)，源表未含')
wline(32, '包装材料', CAT('包装材料'), '元/台',
      '="包装BOM实际(商空方案8项)；包装计算模型估算="'
      '&TEXT(包装计算!$B$43,"0.00")&"元/件，可互校"')
wline(33, '辅助材料', CAT('辅助材料'), '元/台', '物料明细·辅料(锡丝/助焊剂等，16项)')
wline(34, '加工成本', f'=加工成本明细!{COST_TOTAL_CELL}', '元/台',
      '综合口径：人工+SMT+机插+折旧+水电+管理(加工成本明细)')
wline(35, '小计(料工费)', '=SUM(B29:B34)', '元/台', '材料+加工(源表口径+散热器68)', fcolor=BLACK)
wz['B35'].font = font(10, True)
wline(36, '成本差异', '=B35*参数!$B$50', '元/台', '制造损耗/差异缓冲(参数B50，默认1.35%)')
wline(37, '运费', '=IF(ISNUMBER(运费计算!$B$33),运费计算!$B$33,B35*参数!$B$51)',
      '元/台', '=IF(ISNUMBER(运费计算!$B$33),"跨越费率自动计算(运费计算表)",'
      '"跨越费率未覆盖该目的地，按参数B51运费率回退")')
wline(38, '利润加成', '=SUM(B35:B37)*参数!$B$52', '元/台', '成本内加成(参数B52，商空默认0)')
wline(39, '总成本未税', '=SUM(B35:B38)', '元/台', '主营业务成本(单台)', fcolor=BLACK)
wz['B39'].font = font(11, True)
wz['A39'].font = font(11, True)
for cc4 in range(1, 6):
    wz.cell(39, cc4).fill = FILL_KPI

# --- 五、自动报价结果 ---
wsec(41, '五、自动报价结果')
whdr(42, ['报价项目', '结果', '单位', '备注', '公式'])
wline(43, '目标毛利率', '=参数!B4', '%', '参数页可改(商空对齐源表0.3)', FMT_PCT, GREEN)
wline(44, '建议报价未税', '=IFERROR(B39/(1-B43),0)', '元/台', '总成本/(1-毛利率)')
wline(45, '税率', '=参数!B3', '%', '参数页可改', FMT_PCT, GREEN)
wline(46, '建议报价含税', '=B44*(1+B45)', '元/台', '未税价×(1+税率)')
wz['B44'].font = font(11, True)
wz['B46'].font = font(11, True)
for cc5 in (44, 46):
    for k in range(1, 6):
        wz.cell(cc5, k).fill = FILL_KPI
wline(47, '客户目标价', None, '元/台', '手工填写', FMT_MONEY, BLUE)
wline(48, '目标价差异', '=IF(B47="","",B44-B47)', '元/台', '建议价-目标价')
wline(49, '报价毛利率', '=IFERROR((B44-B39)/B44,0)', '%', '自动计算', FMT_PCT)
wline(50, '年销售额未税', '=B44*B8', '元/年', '自动计算', FMT_MONEY2)
wline(51, '年毛利额', '=IFERROR((B44-B39)*B8,0)', '元/年', '自动计算', FMT_MONEY2)

# --- 六、一次性费用 ---
wsec(53, '六、一次性费用（直接向客户收取，不计入单台成本）')
whdr(54, ['费用项目', '金额', '单位', '备注', '公式'])
wline(55, '工装治具费', '=参数!B54', '元', '装配/测试/波峰焊/ICT等工装(加工成本明细·三)', FMT_MONEY2)
wline(56, 'EPS泡沫模具费', '=参数!B53', '元', '左右侧泡沫模具，N10305002124/25共用', FMT_MONEY2)
wline(57, '一次性合计', '=SUM(B55:B56)', '元', '向客户单独收取', FMT_MONEY2, BLACK)
wz['B57'].font = font(11, True)
for cc6 in range(1, 6):
    wz.cell(57, cc6).fill = FILL_KPI

# --- 七、风险检查 ---
wsec(59, '七、风险检查与对账')
whdr(60, ['检查项', '数值', '单位', '备注', '公式'])
wline(61, '客供料品项(清单)', '=COUNTIF(物料明细!$B:$B,"客供料")', '项',
      '源表客供料清单8颗，金额不计入成本', '#,##0', BLACK)
wline(62, 'BOM内客供标记项', '=COUNTIFS(物料明细!$B:$B,"硬件",物料明细!$I:$I,"是")', '项',
      '硬件BOM中单价为0的国创客供料，应与上行一致', '#,##0', BLACK)
wline(63, '未报价物料(非客供)', '=COUNTIFS(物料明细!$H:$H,0,物料明细!$I:$I,"否")', '项',
      '金额为0且非客供的物料需补价，0为正常', '#,##0', BLACK)
wline(64, '客供料参考金额(导入清单)',
      f'=SUMPRODUCT((物料明细!$B$3:$B${LAST}="客供料")'
      f'*物料明细!$E$3:$E${LAST}*物料明细!$F$3:$F${LAST})', '元/台',
      '按导入清单用量×单价计算，仅供参考不计入成本', FMT_MONEY2, GREY)
wline(65, '源表客供合计(对照)', '=参数!B55', '元/台',
      '源表合计554.3197；与上行差异属源表口径差，不影响报价', FMT_MONEY2, GREY)

print('报价汇总 rebuilt. last row =', wz.max_row)

# =====================================================================
# 6) 使用说明 追加
# =====================================================================
wy = wb['使用说明']
existing = ' '.join(str(c.value) for row in wy.iter_rows() for c in row if c.value)
notes = [
    '商空大功率驱动板套表：物料明细已导入 硬件272/结构件32/散热器1/包装8/辅料16/客供料8 共337行；'
    '损耗率留空使金额=用量×单价，与源表精确对账（硬件358.4632/结构416.4798/包装63.7765/辅料37.9431）。',
    '加工成本明细：综合口径13项构成→126.4283元/台（含人工82.0882+SMT/机插+折旧+水电+管理），'
    '附52行人工工时定额、16行工装治具明细；报价汇总「加工成本」直接引用其合计。',
    '散热器：源表未含，按68元未税单列（参数B49），物料明细分类「散热器」，报价汇总独立成本行。',
    '一次性费用：工装48700+EPS泡沫模具29499.115=78199.115元，直接向客户收取，不计入单台成本（报价汇总六）。',
    '运费：目的地填「青岛市」时跨越费率未覆盖山东→自动按运费率(参数B51=1.16%)回退估算；'
    '覆盖城市则用跨越费率精算。毛利率(参数B4)已对齐源表0.3。',
    '制费明细P01~P07为自下而上工序估算工具（商空项目已置0辅料/工装避免重复）；'
    '商空加工成本以「加工成本明细」综合表为准。',
    '风险检查（报价汇总七）：客供料清单8项与硬件BOM内8项单价0的客供标记一一对应，'
    '均不计入成本；未报价物料(非客供)应为0。客供料参考金额按用量×单价=565.138元/台，'
    '源表合计554.3197（源表口径差10.82，不影响报价）。',
    '包装费双口径：报价汇总取包装BOM实际63.7765元/台；包装计算表按几何模型估算约43.67元/件，'
    '两者互为校验，BOM优先。EPS泡沫模具16667元×2已列入一次性费用。',
    '成本差异1.35%(参数B50)与运费率1.16%(参数B51)均取自源表比例；'
    '小计含散热器68元后，成本差异与运费随之联动放大，符合"全部成本因素入表"的口径。',
]
nr = wy.max_row + 1
for n in notes:
    if n[:12] not in existing:
        wy.cell(row=nr, column=1, value='• ' + n).font = font(10)
        wy.cell(row=nr, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        nr += 1

wb.save(WB)
print('SAVED. sheets =', wb.sheetnames)

subprocess.run([sys.executable, RECALC, WB], check=True)
print('RECALC DONE')
