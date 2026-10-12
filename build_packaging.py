import shutil
import subprocess
import sys
import zipfile

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

SRC = '/workspace/.uploads/515f2b04-e179-4784-97f1-ed2324f7b971_产品成本测算报价表.xlsx'
OUT = '/workspace/产品成本测算报价表.xlsx'
RECALC = '/data/user/plugins/trae-remote-official/office-plugin/0.1.0/skills/xlsx/scripts/recalc.py'

wb = openpyxl.load_workbook(SRC)

F_NAME = '微软雅黑'
WHITE = 'FFFFFFFF'
BLUE = 'FF0000FF'
GREEN = 'FF008000'
BLACK = 'FF000000'
FILL_TITLE = PatternFill('solid', fgColor='FF0F3B5D')
FILL_SEC = PatternFill('solid', fgColor='FF3288B9')
FILL_EMPTY = PatternFill('solid', fgColor='FFFFFF00')
FILL_DONE = PatternFill('solid', fgColor='FFC6EFCE')

def font(size=10, bold=False, color=BLACK):
    return Font(name=F_NAME, size=size, bold=bold, color=color)

# ---------------- 报价汇总 ----------------
ws = wb['报价汇总']
ws.insert_rows(20)
ws.insert_rows(34)
for rng in list(ws.merged_cells.ranges):
    if rng.min_row <= 54 and rng.max_row >= 19:
        ws.merged_cells.remove(rng)
ws['A19'] = '是否带散热器(是/否)'
ws['A20'] = '是否带组装结构(是/否)'
ws['B19'] = '否'
ws['B20'] = '否'
ws['D19'] = '=IF(OR(B19="是",B20="是"),"自动→大板：EPE珍珠棉+纸箱+护角+托盘+缠绕膜+打包带","自动→小板：防静电气泡袋+隔板+纸箱+护角+托盘+缠绕膜")'
ws['D20'] = '装配节拍(秒/台)'
ws['E20'] = 0
ws['F20'] = '工时费(元/小时)'
ws['G20'] = '=参数!$B$46'
for ref in ['A19', 'A20', 'D20', 'F20']:
    ws[ref].font = font()
for ref in ['B19', 'B20', 'E20']:
    ws[ref].font = font(color=BLUE)
    ws[ref].alignment = Alignment(horizontal='left')
ws['B20'] = '否'
ws['D19'].font = font(color=GREEN)
ws['G20'].font = font(color=GREEN)
ws['E20'].number_format = '0.0'
ws['G20'].number_format = '0.00'
dv = DataValidation(type='list', formula1='"否,是"', allow_blank=False)
ws.add_data_validation(dv)
dv.add('B19:B20')
ws['A27'] = '四、成本构成（未税/单台，自动计算）'
ws['A28'] = '成本项目'
ws['B28'] = '金额'
ws['C28'] = '单位'
ws['D28'] = '备注'
ws['E28'] = '公式'
cost_rows = [
    (29, '硬件材料', '=SUMIFS(物料明细!$H:$H,物料明细!$B:$B,"硬件")', '元/台', '物料明细'),
    (30, '结构件', '=SUMIFS(物料明细!$H:$H,物料明细!$B:$B,"结构件")', '元/台', '物料明细'),
    (31, '包装材料', '=包装计算!$B$43', '元/台', '包装计算（自动）'),
    (32, '辅助材料', '=SUMIFS(物料明细!$H:$H,物料明细!$B:$B,"辅助材料")', '元/台', '物料明细'),
    (33, '加工费', '=加工及工装!F13-加工及工装!F8', '元/台', '加工及工装（不含装配人工）'),
    (34, '装配费用', '=加工及工装!F8', '元/台', '工艺节拍÷3600×工时费'),
    (35, '工装分摊', '=加工及工装!H23', '元/台', '加工及工装'),
    (36, '运费', '=运费计算!$B$33', '元/台', '运费计算（跨越费率）'),
    (37, '利润', '=SUM(B29:B36)*0.15', '元/台', '工厂利润'),
    (38, '总成本未税', '=SUM(B29:B37)', '元/台', '自动汇总'),
]
for r, a, b, c, d in cost_rows:
    ws.cell(r, 1, a).font = font(bold=r in (37, 38))
    ws.cell(r, 2, b).font = font(color=GREEN if '!' in b else BLACK, bold=r in (37, 38))
    ws.cell(r, 3, c).font = font()
    ws.cell(r, 4, d).font = font()
    ws.cell(r, 2).number_format = '0.0000' if r == 34 else '0.00'
quote_rows = [
    (40, '五、自动报价结果', None, None, None),
    (41, '报价项目', '结果', '单位', '备注'),
    (42, '目标毛利率', '=参数!B4', '%', '参数页可改'),
    (43, '建议报价未税', '=IFERROR(B38/(1-B42),0)', '元/台', '总成本/(1-毛利率)'),
    (44, '税率', '=参数!B3', '%', '参数页可改'),
    (45, '建议报价含税', '=B43*(1+B44)', '元/台', '未税价×(1+税率)'),
    (46, '客户目标价', None, '元/台', '手工填写'),
    (47, '目标价差异', '=IF(B46="","",B43-B46)', '元/台', '建议价-目标价'),
    (48, '报价毛利率', '=IFERROR((B43-B38)/B43,0)', '%', '自动计算'),
    (49, '年销售额未税', '=B43*B8', '元/年', '自动计算'),
    (50, '年毛利额', '=IFERROR((B43-B38)*B8,0)', '元/年', '自动计算'),
]
for r, a, b, c, d in quote_rows:
    ws.cell(r, 1, a).font = font(bold=r in (40, 41))
    if b is not None:
        ws.cell(r, 2, b).font = font(color=GREEN if isinstance(b, str) and '!' in b else BLACK, bold=r == 41)
    ws.cell(r, 3, c).font = font(bold=r == 41)
    ws.cell(r, 4, d).font = font(bold=r == 41)
ws['A52'] = '六、风险检查'
ws['A53'] = '客供料数量'
ws['B53'] = '=COUNTIF(物料明细!I:I,"是")'
ws['C53'] = '项'
ws['A54'] = '新物料待报价'
ws['B54'] = '=COUNTIF(物料明细!H:H,0)'
ws['C54'] = '项'
for ref in ['A27', 'A40', 'A52']:
    ws[ref].font = font(bold=True, color=WHITE)
    ws[ref].fill = FILL_SEC
for ref in ['A28', 'B28', 'C28', 'D28', 'E28', 'A41', 'B41', 'C41', 'D41']:
    ws[ref].font = font(bold=True, color=WHITE)
    ws[ref].fill = FILL_SEC
required_groups = ['B4:B6', 'B8:B9', 'B13:B20', 'E20:E20', 'G20:G20', 'B22:B24']
for grp in required_groups:
    anchor = grp.split(':')[0]
    for row in ws[grp]:
        for cell in row:
            cell.fill = FILL_EMPTY
    ws.conditional_formatting.add(
        grp,
        FormulaRule(formula=[f'LEN({anchor})>0'], fill=FILL_DONE),
    )

# ---------------- 使用说明 ----------------
ws2 = wb['使用说明']
ws2['B3'] = '首页【报价汇总】只填：产品信息、成品尺寸与单台净重、每箱件数、是否带散热器、是否带组装结构、是否含整托、物流产品、目的地、每票件数。包装费、装配费与运费全部自动算。黄色底=必填待填，填完后自动变绿。'
ws2['B4'] = '首页【报价汇总】分别填写【是否带散热器】与【是否带组装结构】：任一为「是」→大板（EPE珍珠棉+纸箱+护角+托盘+缠绕膜+打包带）；两项均为「否」→小板（防静电气泡袋+隔板+纸箱+护角+托盘+缠绕膜）。如有组装结构，填写装配节拍(秒/台)和工时费，装配费=节拍÷3600×工时费。单价与系数在《参数》页改。'
ws2['B8'] = '跨越费率为参考价，可在《跨越费率》页直接改；金额默认不含税；包装费按方案清单自动算。'

# ---------------- 参数 ----------------
wp = wb['参数']
wp['A10'] = '防静电气泡袋单价'
wp['A11'] = '气泡袋单边余量'
wp['B10'] = 3
wp['B10'].font = font(color=BLUE)

wp['A41'] = '四、包装方案参数（小板/大板）'
wp['A41'].font = font(bold=True, color=WHITE)
wp['A41'].fill = FILL_SEC
wp.merge_cells('A41:C41')

hdr = ['A42', 'B42', 'C42', 'D42']
vals = ['参数项', '参数值', '单位', '说明']
for ref, v in zip(hdr, vals):
    c = wp[ref]
    c.value = v
    c.font = font(bold=True, color=WHITE)
    c.fill = FILL_SEC

rows = [
    ('防静电气泡袋克重', 60, 'g/㎡', '气泡袋面密度', '0'),
    ('隔板单价', 0.3, '元/件', '小板每件隔板', '0.00'),
    ('隔板克重', 20, 'g/件', '小板隔板重量', '0'),
    ('默认装配工时费', 60, '元/小时', '首页可按项目覆盖', '0.00'),
]
for i, (a, b, cunit, d, fmt) in enumerate(rows):
    r = 43 + i
    wp.cell(row=r, column=1, value=a).font = font()
    bc = wp.cell(row=r, column=2, value=b)
    bc.font = font(color=BLUE)
    bc.number_format = fmt
    wp.cell(row=r, column=3, value=cunit).font = font()
    wp.cell(row=r, column=4, value=d).font = font()

# ---------------- 加工及工装 ----------------
wm = wb['加工及工装']
wm['C8'] = '=IF(报价汇总!B20="是",报价汇总!E20/3600,0)'
wm['D8'] = '=报价汇总!G20'
wm['C8'].font = font(color=GREEN)
wm['D8'].font = font(color=GREEN)
wm['C8'].number_format = '0.0000'
wm['D8'].number_format = '0.00'

# ---------------- 运费计算 ----------------
wf = wb['运费计算']
wf['B7'] = '=IF(报价汇总!B16="","",报价汇总!B16+包装计算!$B$41)'
wf['B8'] = '=包装计算!$B$17'

# ---------------- 包装计算（整表重写） ----------------
wpk = wb['包装计算']
for rng in list(wpk.merged_cells.ranges):
    wpk.unmerge_cells(str(rng))
for row in wpk.iter_rows(min_row=1, max_row=70, min_col=1, max_col=5):
    for c in row:
        c.value = None
        c.font = Font(name=F_NAME, size=10)
        c.fill = PatternFill()
        c.number_format = 'General'
        c.alignment = Alignment()

def title(cell, text):
    cell.value = text
    cell.font = font(size=12, bold=True, color=WHITE)
    cell.fill = FILL_TITLE

def section(cell, text):
    cell.value = text
    cell.font = font(bold=True, color=WHITE)
    cell.fill = FILL_SEC

def label(cell, text):
    cell.value = text
    cell.font = font()

def formula(cell, text, fmt='General', bold=False):
    cell.value = text
    cell.font = font(bold=bold, color=BLACK if bold else GREEN)
    cell.number_format = fmt

def fnum(cell, text, fmt):
    formula(cell, text, fmt, bold=False)

title(wpk['A1'], '包装费计算（自动，按包装方案清单）')
wpk.merge_cells('A1:E1')

section(wpk['A3'], '一、输入（自动取自报价汇总）')
wpk.merge_cells('A3:E3')
labels = ['成品长(mm)', '成品宽(mm)', '成品高(mm)', '每箱件数N', '是否含整托', '包装方案(自动)']
for idx, (r, f) in enumerate([(4, '=报价汇总!B13'), (5, '=报价汇总!B14'), (6, '=报价汇总!B15'),
                  (7, '=报价汇总!B17'), (8, '=报价汇总!B18'), (9, '=IF(OR(报价汇总!B19="是",报价汇总!B20="是"),"大板","小板")')]):
    label(wpk.cell(row=r, column=1), labels[idx])
    if r in (4, 5, 6, 7):
        fnum(wpk.cell(row=r, column=2), f, '0')
    else:
        formula(wpk.cell(row=r, column=2), f, 'General')

section(wpk['A11'], '二、包装几何（自动）')
wpk.merge_cells('A11:E11')
geo = [
    (12, '成品最大边长(mm)', '=MAX(B4:B6)', '0'),
    (13, '缓冲厚度t(mm)', '=VLOOKUP($B$12,$A$58:$D$61,3,TRUE)', '0'),
    (14, '箱内长(mm)', '=B4+2*B13+参数!$B$22', '0'),
    (15, '箱内宽(mm)', '=B5+2*B13+参数!$B$22', '0'),
    (16, '箱内高(mm)', '=B7*(B6+2*B13)+参数!$B$22', '0'),
    (17, '单箱体积(㎝³)', '=B14*B15*B16/1000', '0'),
]
for r, a, f, fmt in geo:
    label(wpk.cell(row=r, column=1), a)
    fnum(wpk.cell(row=r, column=2), f, fmt)

section(wpk['A19'], '三、内包装材料费（单件）')
wpk.merge_cells('A19:E19')
inner = [
    (20, '气泡袋长(mm)', '=B4+B6+2*参数!$B$11', '0'),
    (21, '气泡袋宽(mm)', '=B5+B6+2*参数!$B$11', '0'),
    (22, '气泡袋面积(㎡)', '=B20*B21/10^6', '0.0000'),
    (23, '气泡袋费(元/件)', '=B22*参数!$B$10', '0.0000'),
    (24, '隔板费(元/件)', '=IF($B$9="小板",IF(OR($B$7="",$B$7=0),0,参数!$B$44*MAX($B$7-1,0)/$B$7),0)', '0.0000'),
    (25, 'EPE体积(㎥/件)', '=2*B13*(B4*B5+B4*B6+B5*B6)/10^9', '0.0000'),
    (26, 'EPE费(元/件)', '=B25*参数!$B$14', '0.0000'),
    (27, '内包材料费(元/件)', '=IF($B$9="小板",B23+B24,B26)', '0.0000'),
    (28, '纸箱用纸面积(㎡)', '=(B14+B15)*2*(B15+2*B16)/10^6*(1+参数!$B$21)', '0.0000'),
    (29, '瓦楞类型', '=VLOOKUP($B$12,$A$58:$D$61,4,TRUE)', 'General'),
    (30, '纸板单价(元/㎡)', '=VLOOKUP(B29,$A$65:$B$67,2,FALSE)', '0.00'),
    (31, '纸箱费(元/箱)', '=B28*B30+参数!$B$20', '0.00'),
    (32, '纸箱费(元/件)', '=IF(OR(B7="",B7=0),0,B31/B7)', '0.0000'),
    (33, '辅料费(元/件)', '=IF(OR(B7="",B7=0),0,(参数!$B$23+参数!$B$24)/B7)', '0.0000'),
]
for r, a, f, fmt in inner:
    label(wpk.cell(row=r, column=1), a)
    fnum(wpk.cell(row=r, column=2), f, fmt)
label(wpk['A34'], '内包装单件费(元)')
wpk['A34'].font = font(bold=True)
formula(wpk['B34'], '=B27+B32+B33', '0.0000', bold=True)

section(wpk['A36'], '四、整托分摊（可选，勾选含整托生效）')
wpk.merge_cells('A36:E36')
pallet = [
    (37, '每箱占地(㎡)', '=B14*B15/10^6', '0.0000'),
    (38, '每托件数(件)', '=IF(OR(B37="",B37=0),0,ROUNDDOWN(参数!$B$31/B37,0)*参数!$B$32)', '0'),
    (39, '每托包装费(元/托)', '=参数!$B$29+参数!$B$25/参数!$B$26+参数!$B$27*参数!$B$28+IF($B$9="大板",参数!$B$30,0)', '0.00'),
    (40, '整托分摊(元/件)', '=IF(OR(B38="",B38=0),0,B39/B38)', '0.0000'),
    (41, '包装增重(kg/件)', '=IF(OR(B7="",B7=0),0,IF($B$9="小板",B22*参数!$B$43/1000,B25*参数!$B$15)+B28*参数!$B$19/1000/B7+IF($B$9="小板",参数!$B$45/1000*MAX($B$7-1,0)/$B$7,0)+0.005)', '0.000'),
]
for r, a, f, fmt in pallet:
    label(wpk.cell(row=r, column=1), a)
    fnum(wpk.cell(row=r, column=2), f, fmt)

label(wpk['A43'], '包装费合计(元/件)')
wpk['A43'].font = font(bold=True)
formula(wpk['B43'], '=B34+IF($B$8="是",B40,0)', '0.0000', bold=True)

section(wpk['A45'], '五、包装方案清单对照（√=该方案包含）')
wpk.merge_cells('A45:E45')
hdr2 = ['包装物料', '单位', '单价(元)', '小板', '大板']
for i, h in enumerate(hdr2):
    c = wpk.cell(row=46, column=1 + i, value=h)
    c.font = font(bold=True, color=WHITE)
    c.fill = FILL_SEC

config = [
    ('防静电气泡袋', '元/㎡', '=参数!$B$10', '√', '—'),
    ('隔板', '元/件', '=参数!$B$44', '√', '—'),
    ('EPE珍珠棉', '元/m³', '=参数!$B$14', '—', '√'),
    ('纸箱', '元/箱', '按面积×瓦楞', '√', '√'),
    ('护角', '元/套', '=参数!$B$29', '√', '√'),
    ('托盘', '元/托', '=参数!$B$25/参数!$B$26', '√', '√'),
    ('缠绕膜', '元/托', '=参数!$B$27*参数!$B$28', '√', '√'),
    ('打包带', '元/托', '=参数!$B$30', '—', '√'),
]
for i, (a, b, c, d, e) in enumerate(config):
    r = 47 + i
    wpk.cell(row=r, column=1, value=a).font = font()
    wpk.cell(row=r, column=2, value=b).font = font()
    cc = wpk.cell(row=r, column=3, value=c)
    cc.font = font(color=GREEN if str(c).startswith('=') else BLACK)
    if str(c).startswith('='):
        cc.number_format = '0.00'
    wpk.cell(row=r, column=4, value=d).font = font()
    wpk.cell(row=r, column=5, value=e).font = font()

wpk['A55'] = '口径：气泡袋按袋面积×单价；隔板=(N-1)/N×单价；EPE按体积×单价；纸箱按面积×单价÷N；护角/托盘/缠绕膜/打包带按整托费用÷每托件数。'
wpk['A55'].font = font()
wpk.merge_cells('A55:E55')

section(wpk['A56'], '六、成品最大边长档位表（自动匹配缓冲厚度/瓦楞）')
wpk.merge_cells('A56:E56')
for i, h in enumerate(['下限mm', '上限mm', '缓冲厚度mm', '瓦楞']):
    c = wpk.cell(row=57, column=1 + i, value=h)
    c.font = font(bold=True, color=WHITE)
    c.fill = FILL_SEC
band = [
    (0, 200, 15, '单瓦楞3层'),
    (200, 350, 20, '双瓦楞5层'),
    (350, 550, 25, '双瓦楞5层'),
    (550, 999999, 30, '重型7层'),
]
for i, (a, b, c, d) in enumerate(band):
    r = 58 + i
    wpk.cell(row=r, column=1, value=a).font = font()
    wpk.cell(row=r, column=2, value=b).font = font()
    wpk.cell(row=r, column=3, value=c).font = font()
    wpk.cell(row=r, column=4, value=d).font = font()

section(wpk['A63'], '七、瓦楞单价映射')
wpk.merge_cells('A63:E63')
for i, h in enumerate(['瓦楞类型', '纸板单价(元/㎡)']):
    c = wpk.cell(row=64, column=1 + i, value=h)
    c.font = font(bold=True, color=WHITE)
    c.fill = FILL_SEC
corr = [
    ('单瓦楞3层', '=参数!$B$16'),
    ('双瓦楞5层', '=参数!$B$17'),
    ('重型7层', '=参数!$B$18'),
]
for i, (a, b) in enumerate(corr):
    r = 65 + i
    wpk.cell(row=r, column=1, value=a).font = font()
    bc = wpk.cell(row=r, column=2, value=b)
    bc.font = font(color=GREEN)
    bc.number_format = '0.00'

wpk.column_dimensions['A'].width = 26
wpk.column_dimensions['B'].width = 16
wpk.column_dimensions['C'].width = 14
wpk.column_dimensions['D'].width = 10
wpk.column_dimensions['E'].width = 10

wb.save(OUT)
print('saved', OUT)


def recalc_and_repair(path):
    r = subprocess.run([sys.executable, RECALC, path], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print('RECALC STDERR:', r.stderr)
        raise SystemExit(r.returncode)
    tmp = path + '.tmp'
    with zipfile.ZipFile(path, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name in zin.namelist():
            data = zin.read(name)
            if name == 'xl/styles.xml':
                s = data.decode('utf-8')
                s = s.replace(
                    '<patternFill><bgColor rgb="FFC6EFCE"/></patternFill>',
                    '<patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/></patternFill>',
                )
                data = s.encode('utf-8')
            zout.writestr(name, data)
    shutil.move(tmp, path)
    print('recalc + repair done', path)


recalc_and_repair(OUT)
