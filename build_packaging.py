import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

SRC = '/workspace/.uploads/515f2b04-e179-4784-97f1-ed2324f7b971_产品成本测算报价表.xlsx'
OUT = '/workspace/产品成本测算报价表.xlsx'

wb = openpyxl.load_workbook(SRC)

F_NAME = '微软雅黑'
WHITE = 'FFFFFFFF'
BLUE = 'FF0000FF'
GREEN = 'FF008000'
BLACK = 'FF000000'
FILL_TITLE = PatternFill('solid', fgColor='FF0F3B5D')
FILL_SEC = PatternFill('solid', fgColor='FF3288B9')

def font(size=10, bold=False, color=BLACK):
    return Font(name=F_NAME, size=size, bold=bold, color=color)

# ---------------- 报价汇总 ----------------
ws = wb['报价汇总']
ws['A19'] = '包装方案(小板/大板)'
ws['A19'].font = font()
ws['B19'] = '小板'
ws['B19'].font = font(color=BLUE)
ws['B19'].alignment = Alignment(horizontal='left')
ws['D19'] = '带散热器/组装结构→大板，水泵/风机板→小板'
ws['D19'].font = font()
dv = DataValidation(type='list', formula1='"小板,大板"', allow_blank=False)
ws.add_data_validation(dv)
dv.add(ws['B19'])
ws['B30'] = '=包装计算!$B$43'

# ---------------- 使用说明 ----------------
ws2 = wb['使用说明']
ws2['B3'] = '首页【报价汇总】只填：产品信息、成品尺寸与单台净重、每箱件数、包装方案、是否含整托、物流产品、目的地、每票件数。包装费与运费全部自动算。'
ws2['B4'] = '首页选【包装方案】：小板=防静电气泡袋+隔板+纸箱+护角+托盘+缠绕膜；大板=EPE珍珠棉+纸箱+护角+托盘+缠绕膜+打包带。带散热器/组装结构产品（暖通商空大功率驱动板）选大板；水泵、风机板选小板。单价与系数在《参数》页改。'
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
]
for i, (a, b, cunit, d, fmt) in enumerate(rows):
    r = 43 + i
    wp.cell(row=r, column=1, value=a).font = font()
    bc = wp.cell(row=r, column=2, value=b)
    bc.font = font(color=BLUE)
    bc.number_format = fmt
    wp.cell(row=r, column=3, value=cunit).font = font()
    wp.cell(row=r, column=4, value=d).font = font()

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
labels = ['成品长(mm)', '成品宽(mm)', '成品高(mm)', '每箱件数N', '是否含整托', '包装方案(小板/大板)']
for idx, (r, f) in enumerate([(4, '=报价汇总!B13'), (5, '=报价汇总!B14'), (6, '=报价汇总!B15'),
                  (7, '=报价汇总!B17'), (8, '=报价汇总!B18'), (9, '=报价汇总!B19')]):
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
