# 智能日历助手 v4.0 协作汇总版 — 实现计划

日期：2026-09-21
分支：`feature/collab-approval-v4`
基线：main @ `智能日历助手.html`（2875 行，单文件 HTML）
设计文档：`docs/superpowers/specs/2026-09-21-collab-approval-v4-design.md`

---

## Goal

将现有 v3 单文件 HTML 日历助手升级为 v4.0 协作汇总版：在保持零依赖、纯前端、单 HTML 文件架构的前提下，新增 @提及、飞书 Webhook 消息卡片通知、成果资料上传（Base64）、部门经理汇总看板（KPI/图表/表格/报告/定时推送）、多维筛选排序、深链路由等能力。**不做审批流**，仅做经理内容汇总。

## Architecture

- 单文件：所有 CSS/JS/HTML 内联在 `智能日历助手.html`
- 存储：localStorage `magong_todo_calendar` 键，升级为版本化结构 `{version:4, todos:[], members:[], groups:[], webhookConfig:{...}}`
- 迁移：加载时检测旧数组格式自动迁移，迁移前备份到 `magong_todo_calendar_v3_backup`
- 飞书集成：`fetch(url, {method:'POST', mode:'no-cors', body: cardJSON})` + Web Crypto HMAC-SHA256 签名
- 图表：纯 CSS/Canvas 自绘（水平柱状图、饼图），不引入第三方库

## Tech Stack

无新增依赖。现有原生 HTML/CSS/JS +：
- Web Crypto API（HMAC-SHA256 签名）
- FileReader API（文件→Base64）
- URL Hash API（深链路由）
- Notification API（本地通知 fallback）
- Canvas 2D（图表绘制）

---

## File Structure Map

仅修改/新增以下文件：

```
/workspace/
├── 智能日历助手.html            # 唯一修改的运行时文件（约 +1800 JS / +350 CSS / +HTML）
└── docs/superpowers/
    ├── specs/
    │   └── 2026-09-21-collab-approval-v4-design.md  # 已完成
    └── plans/
        └── 2026-09-21-collab-approval-v4.md         # 本文件
```

---

## Implementation Phases (共 8 个阶段，约 60+ 个小任务)

---

### Phase 0：数据模型 v4 + 迁移 + 工具函数（约 150 行 JS）

**Task 0.1 确认分支状态**
```bash
cd /workspace && git status && git branch
```
预期：在 `feature/collab-approval-v4` 分支，工作区干净。

**Task 0.2 扩展常量与版本号**
- 在 `<script>` 顶部 `STORAGE_KEY`（L997）后插入新常量：`APP_VERSION='4.0'`、`STORAGE_KEY_V3_BACKUP`、附件大小限制常量、`ALLOWED_MIME`、`FILE_EXT_ICONS`、`AVATAR_COLORS`、`MENTION_TRIGGER`
- 顶栏 `<span class="topbar-sub">v3.0</span>` 改为 `<span class="topbar-sub">v4.0 · 协作汇总版</span>`

**Task 0.3 扩展全局状态变量**
- 在现有全局 `let` 声明区（L1003-L1017）追加：`members=[]`、`groups=[]`、`webhookConfig={...}`、dashboard/deliver/mention/router 相关状态变量

**Task 0.4 改写 loadData/saveData 为版本化结构**
- 新增 `defaultData()`：返回 `{version:4, todos:[...], members:[...], groups:[...], webhookConfig:{...}}`，默认包含示例经理+示例成员
- 新增 `migrateV3toV4(raw)`：先备份到 v3_backup，将旧 todos 数组升级为新结构（补 assignees/mentions/attachments/deliverables/history 等字段）
- 改写 `loadData()`：三种分支：①raw为null→用defaultData；②raw解析后是数组→migrateV3toV4；③version===4→解构赋值+补字段默认值；④兜底→defaultData
- 改写 `saveData()`：包装为 `{version:4,todos,members,groups,webhookConfig}` 再 `setItem`；捕获 QuotaExceededError 给 toast

**Task 0.5 新增工具函数（约20个）**
在 `escapeHtml` 附近添加：
- `getMemberById / getCurrentUser / getSubordinatesOf / getGroupById`
- `genMemberId / genGroupId / genAttId`
- `formatBytes / getFileExt / getFileIcon / isImageMime`
- `escapeAttr / fmtDateTime / parseTimeStr / daysBetween`
- `getTodoStatus(todo)` → 返回 'done'|'inprogress'|'overdue'|'duesoon'（基于 todo.done 和 todo.date 派生）
- `getStatusLabel / getStatusColor`
- `getStorageUsed` 返回 localStorage 估算占用字节

**验证**：浏览器打开 HTML，控制台无报错，默认加载示例数据并看到 2 个示例成员+1个群组。

提交：
```bash
git add -A && git commit -m "feat(v4): phase0 - 数据模型v4迁移、常量、工具函数"
```

---

### Phase 1：CSS 扩展（约 350 行 CSS）

在 `</style>` 前追加以下 CSS 区块（每段独立）：

1. **通用组件**：`.badge`（彩色徽章）、`.avatar`/`.avatar-sm`/`.avatar-lg`/`.avatar-stack`（头像堆叠）、`.mention-tag`/`.mention-tag.at-all`（@标签）、`.btn-ghost`、`.current-user-chip`（当前身份chip）
2. **经理工作台**：`.dashboard-view`、`.dashboard-toolbar`、`.kpi-grid`/`.kpi-card`、`.chart-row`/`.chart-card`、`.hbar-chart`/`.hbar-row`/`.hbar-track`/`.hbar-fill`（水平柱状图）、`.pie-wrap`/`.pie-legend`、`.timeline`/`.timeline-item`、`.data-table`（明细表格）、`.table-actions`
3. **模态框**：`.modal-mask`/`.modal`/`.modal-lg`/`.modal-xl`/`.modal-header`/`.modal-body`/`.modal-footer`、`.form-row`/`.form-label`/`.form-input`/`.form-textarea`/`.form-select`/`.form-hint`/`.form-row-2col`
4. **@提及下拉**：`.mention-dropdown`/`.mention-item`/`.mention-divider`
5. **负责人选择器**：`.assignee-picker`/`.assignee-chip`/`.assignee-picker-placeholder`/`.assignee-quick-actions`
6. **附件上传**：`.drop-zone`、`.attachments-grid`/`.attachment-card`（缩略图/图标/文件名/meta/悬浮操作）、`.upload-progress`、`.storage-bar`（存储容量条）
7. **设置面板**：`.settings-tabs`/`.settings-tab`/`.settings-body`、`.guide-box`（折叠指引区）、`.member-cards`/`.member-card`/`.group-cards`/`.group-card`/`.icon-btn`
8. **待办项增强**：`.todo-item-hl-mention`（被@高亮左边条）、`.todo-assignees`（头像组）、`.todo-meta-row`、`.todo-mention-all-flag`、`.attachments-inline`/`.attachment-pill`、`.todo-detail-attachments`
9. **筛选快捷标签**：`.quick-tags`/`.quick-tag`（含.active 态和计数）
10. **飞书跳转提示**：`.feishu-banner`
11. **图片预览**：`.img-preview-modal`
12. **动画**：`@keyframes pulse-hl` + `.todo-item.highlight-pulse`（脉冲闪烁）
13. **响应式**：`@media(max-width:1100px)` 让图表区单列显示

提交：
```bash
git add -A && git commit -m "feat(v4): phase1 - CSS扩展（徽章/工作台/模态框/@提及/附件/设置面板等）"
```

---

### Phase 2：HTML 骨架（约 250 行 HTML）

**Task 2.1 顶栏改造**
- `.topbar-sub` 版本号更新为 v4.0
- `.topbar-actions`（view-switch 之前）新增：当前身份 chip（`.current-user-chip` 含头像+姓名）、「📊 工作台」按钮（`#btnDashboard`）、「⚙️」齿轮按钮（`#btnSettings`）

**Task 2.2 飞书跳转提示条**
在 topbar 之后、stats 之前插入：
```html
<div class="feishu-banner hidden" id="feishuBanner">📨 来自飞书跳转，已定位到相关待办<span class="close" onclick="document.getElementById('feishuBanner').classList.add('hidden')">✕</span></div>
```

**Task 2.3 工作台视图容器**
在 `.main` 内（与 `.calendar-panel`/`.todo-panel` 同级，初始 `style="display:none"`）新增 `#dashboardView`，包含：
- 顶部 toolbar（标题、周期下拉、维度下拉、刷新按钮）
- KPI 4卡（`#kpiGrid`）
- 双栏图表区：水平柱状图（`#hbarChart`）+ 成果时间线（`#timeline`）
- 双栏：饼图（canvas#pieChart + legend）+ 重点关注区（`#highlightsList`）
- 明细表格（`#detailTable`，含负责人/任务/截止/优先级/状态/成果/操作7列）
- 底部操作：生成报告/推送飞书/导出Markdown三个按钮

**Task 2.4 设置面板模态框**
在 `#app` 闭合 `</div>` 前插入 `#settingsModal`：4个Tab（飞书集成/成员管理/群组管理/数据管理），内容动态渲染到 `#settingsBody`。

**Task 2.5 提交成果弹窗** `#deliverModal`：交付结果说明 textarea + 拖拽上传区 + 文件隐藏 input + 待传附件预览网格。

**Task 2.6 报告预览模态框** `#reportModal`：含复制/下载/打印/推送飞书4个按钮 + `<pre id="reportMdContent">` 显示 Markdown。

**Task 2.7 图片预览模态框** `#imgPreviewModal`：全屏黑底，点击关闭。

**验证**：浏览器打开 HTML，页面无明显错乱（dashboard 初始隐藏，模态框初始 hidden），控制台无报错。

提交：
```bash
git add -A && git commit -m "feat(v4): phase2 - HTML视图骨架（工作台/设置/提交成果/报告/图片预览）"
```

---

### Phase 3：核心功能 JS 模块 — @提及 + 附件 + Webhook（约 600 行 JS）

**Task 3.1 @提及解析与渲染引擎**
- `parseMentions(text)` → 返回 `{html, memberIds, groupIds, mentionAll}`，识别 `@[m_xxx]`、`@[g_xxx]`、`@[all]` 三种标记，member渲染为蓝色标签+title显示部门职能，group渲染为标签，all渲染为红色标签
- `expandMentionRecipients(todo)` → 展开所有应通知的 memberId 集合：assignees + mentionAll全员 + desc中@的成员 + @群组展开成员 - 当前用户（去重）

**Task 3.2 @提及下拉交互**
- `showMentionDropdown(textarea, onSelect)`：光标前匹配 `/@([^\s@]*)$/` 时显示下拉
- 下拉项顺序：@所有人 → 成员列表（关键字过滤）→ 分隔线 → 群组列表（关键字过滤）
- 键盘支持：ArrowUp/Down导航、Enter/Tab选择、Escape关闭
- `insertMention(textarea, type, id)`：将 `@xxx` 替换为 `@[id]` 或 `@[all]` 标记
- `hideMentionDropdown()`、全局 click/keydown 监听器绑定

**Task 3.3 负责人选择器组件**
- `renderAssigneePicker(container, selectedIds, opts)`：渲染 chip 列表+内嵌 input+快捷按钮（@所有人/@选择群组/+选择成员）
- `assigneeHandlePick / assigneePickAll / assigneePickGroup / assigneeShowAll` 辅助函数
- `onAssigneeChange` 回调（默认空，创建待办弹窗覆盖此函数）

**Task 3.4 文件上传与 Base64**
- 全局 `pendingAttachments=[]`
- `handleFileSelection(files)`：校验大小+格式，FileReader.readAsDataURL 转 Base64，push 到 pendingAttachments
- `renderPendingAttachments / renderAttachmentCard(a,canDelete)`：图片显示缩略图，其他显示图标+文件名+大小
- `bindAttachmentCardEvents`：点击卡片→图片预览或下载；悬停显示删除按钮
- `removeAttachment(id,isPending) / downloadAttachment(att) / previewImage(src)`
- `bindDropZone()`：绑定拖拽事件（dragenter/over/leave/drop）

**Task 3.5 飞书 Webhook 核心**
- `hmacSha256Base64(secret, message)`：使用 Web Crypto API 生成签名
- `resolveWebhookTarget(groupId)`：群组级覆盖→全局默认→null
- `getAppBaseUrl()`：有配置用配置，否则用 `window.location.href.split('#')[0]`
- `buildDeepLink(path, params)`：构造 `{base}#path?params` 回跳URL
- `buildAtMentionsText(memberIds)`：有 open_id 用 `<at id="ou_xxx"></at>`（飞书@语法），否则用纯文本 `@姓名`
- `buildFeishuCalendarLink(todo)`：构造飞书 AppLink `https://applink.feishu.cn/client/calendar/event/create?...` 预填 summary/startTime/endTime/attendees/description

**Task 3.6 消息卡片构建与发送**
- `sendFeishuCard(card, groupId)`：
  1. 若未配置 webhook，降级使用 Notification API（需先请求权限）
  2. 若有 secret，用 hmacSha256Base64 生成 timestamp+sign，加进 payload
  3. `fetch(url, {method:'POST', mode:'no-cors', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})`
  4. 由于 no-cors 不能读响应，发送成功与否由用户在飞书客户端确认
- `buildTodoReminderCard(todo, reason)`：构造单条待办提醒卡片（header红/黄/蓝按紧急度，body含标题/描述/截止/负责人/优先级/状态，底部两个按钮"查看详情"和"加入飞书日程"）
- `buildManagerSummaryCard(manager, stats, period)`：构造经理汇总卡片（header蓝，body含周期/人数/完成/进行中/即将到期/逾期/新成果，重点关注列表，按钮"查看完整汇总"和"查看全部待办"）
- `sendTodoNotification(todo, reason)`：确定通知目标成员列表 → 对每个有群组配置的群/全局默认，调用 sendFeishuCard
- `sendManagerSummaryPush(manager, period)`：计算统计 → 构造卡片 → 发送给经理所在群
- 防骚扰机制：`pushHistory` 记录 `{todoId+reason: date}`，24h 内不重复

提交：
```bash
git add -A && git commit -m "feat(v4): phase3 - @提及引擎、负责人选择器、附件上传、飞书Webhook核心"
```

---

### Phase 4：设置面板四大 Tab（约 400 行 JS）

**Task 4.1 设置面板打开/关闭/Tab切换**
- `openSettings() / closeSettings() / switchSettingsTab(tabName)`
- Tab 高亮切换、调用对应渲染函数：`renderFeishuTab / renderMembersTab / renderGroupsTab / renderDataTab`

**Task 4.2 飞书集成 Tab** `renderFeishuTab()`
- 表单字段：defaultWebhookUrl、defaultWebhookSecret、appBaseUrl、currentUserId（下拉选择成员）、dailyPush（开关+时间）、weeklyPush（开关+时间）
- 顶部折叠指引区（`<details class="guide-box">`）：5步配置指引（创建机器人→填入URL→绑定open_id→设置访问地址→测试消息）
- "发送测试消息"按钮：点击调用 `sendFeishuCard(buildTestCard())`，buildTestCard 使用一张最简单的文本卡片+测试跳转链接
- 保存按钮：写入 webhookConfig，saveData，showToast 成功

**Task 4.3 成员管理 Tab** `renderMembersTab()`
- 顶部"+ 添加成员"按钮 → 弹出简易输入或直接追加空卡片让用户填写
- 成员卡片网格（`.member-cards`）：每张卡显示头像、姓名输入、角色checkbox（标记为经理）、部门输入、职能输入、飞书open_id输入、头像颜色选择、经理下拉（从所有 role=manager 中选）、删除按钮
- 一键"批量设置经理"按钮：选中某经理+某部门，将该部门所有成员的 managerId 设为该经理
- 字段 change 事件自动保存到 members 数组+saveData
- 提供初始化示例：如果 members 为空，提示"请先添加成员"

**Task 4.4 群组管理 Tab** `renderGroupsTab()`
- "+ 创建群组"按钮
- 群组卡片：群名输入、成员多选（checkbox 列表）、群组级 webhookUrl、webhookSecret、删除按钮
- 实时保存

**Task 4.5 数据管理 Tab** `renderDataTab()`
- 存储容量进度条：显示 getStorageUsed / 5MB（估算），>80%黄色警告，>95%红色
- "清理30天前已完成任务的附件"按钮 → 确认后清理，saveData
- "导出全部数据"按钮 → 生成 JSON 文件下载（包含 version/todos/members/groups/webhookConfig）
- "导入数据"按钮 → 文件选择器，读取 JSON，确认后 merge/replace
- "重置所有数据"按钮 → 红色确认提示，确认后清空 localStorage 并 reload
- 附件管理清单：列出所有附件（文件名、大小、所属todo标题、上传者、上传时间），支持逐个删除

提交：
```bash
git add -A && git commit -m "feat(v4): phase4 - 设置面板（飞书集成/成员管理/群组管理/数据管理四个Tab）"
```

---

### Phase 5：创建/编辑待办弹窗增强 + 列表渲染增强 + 完成流程（约 350 行 JS + HTML 微调）

**Task 5.1 改造创建/编辑待办弹窗**

找到现有的编辑弹窗（新建/编辑 todo 的模态 HTML），在原有字段（title/desc/date/time/priority/category/scope）之后追加：
- 「👥 负责人」区：`<div id="assigneePickerContainer"></div>`（由 renderAssigneePicker 渲染）
- 「🔔 通知群组」下拉：`<select id="todoNotifyGroup">` 选项为"全局默认"+所有群组
- 「📎 完成时需提交成果」checkbox：`<label><input type="checkbox" id="todoRequireDeliverable" checked> 完成时需提交成果</label>`

**Task 5.2 修改保存待办逻辑**
- 打开弹窗时：
  - 编辑模式：读取现有 assignees/mentionAll/notifyGroupId/requireDeliverable 渲染到对应控件
  - 新建模式：默认 assignees=[currentUserId]，notifyGroupId=''，requireDeliverable=true
- 保存时：
  - 读取负责人（从 assigneePickerContainer 获取或用全局变量）
  - 读取通知群组和 requireDeliverable
  - 解析 desc 的 @mentions（parseMentions），填入 todo.mentions（记录atTime）
  - 创建 todo.history 记录 created 事件
  - 如果有 assignees（且非仅自己），调用 `sendTodoNotification(todo, 'assigned')`
  - saveData + 重渲染

**Task 5.3 待办列表卡片渲染增强**

修改现有渲染 todo item 的函数：
- 左侧状态条颜色：基于 getTodoStatus（done绿/overdue红/duesoon黄/inprogress蓝）
- 标题下方新增：负责人头像组（avatar-stack，最多显示3个，其余+N）、职能标签（badge）、状态徽章（badge）、mentionAll红色标签
- 如果当前用户是被@的（assignees包含currentUserId 或 mentionAll），给 todo-item 添加 `todo-item-hl-mention` 类
- 已完成待办若有附件，显示"📎 N份成果"标识（badge）
- 描述区渲染使用 parseMentions().html 而非 escapeHtml(desc)，让 @标签 显示为蓝色块
- 悬停菜单（操作按钮）新增：「📎 添加成果」按钮（仅完成后可点击）

**Task 5.4 标记完成 → 提交成果弹窗**

修改"✅ 完成"按钮逻辑：
- 如果 requireDeliverable=true：
  - 设置 `pendingCompleteTodoId = todoId`
  - 清空 `pendingAttachments=[]`
  - 打开 `#deliverModal`
  - 绑定 dropZone/fileInput 事件（bindDropZone）
- 如果 requireDeliverable=false：
  - 直接完成：todo.done=true, todo.completedAt=now, todo.history 追加 completed 记录, saveData, 重渲染
  - 通知经理（若有直属经理）sendTodoNotification(todo, 'completed')
- 「取消」→ closeDeliverModal 重置 pendingCompleteTodoId
- 「确认完成」→ confirmDeliver()：
  - todo.done=true, todo.completedAt=now
  - todo.deliverables = document.getElementById('deliverNotes').value
  - todo.attachments = [...(todo.attachments||[]), ...pendingAttachments]
  - todo.history 追加 completed 事件（含附件数量和deliverables摘要）
  - saveData, 关闭弹窗, pendingAttachments=[], pendingCompleteTodoId=null
  - 调用 sendTodoNotification(todo, 'deliverable') 通知经理
  - 重渲染

**Task 5.5 待办详情面板中的附件展示**

修改展开待办详情的函数（expandedTodoId 面板）：
- 在原有详情内容后追加 `.todo-detail-attachments` 区块
- 如果 todo.attachments 有内容，显示网格 `.attachments-grid`，用 renderAttachmentCard 渲染每个附件（canDelete = 当前用户是上传者 或 当前用户是上传者的经理）
- 若 todo.done，底部显示「📎 添加成果」按钮，点击打开文件选择追加附件（复用 handleFileSelection，但直接写入 todo.attachments 并 saveData）
- window._currentTodoAtts 和 window._currentTodoId 用于删除时回写

提交：
```bash
git add -A && git commit -m "feat(v4): phase5 - 编辑弹窗增强/列表渲染增强/完成提交流程/附件详情展示"
```

---

### Phase 6：经理汇总仪表盘（约 350 行 JS）

**Task 6.1 视图切换扩展**

修改 `switchView` 函数，新增 'dashboard' 视图：
- 原 month/week 控制 cal-panel 的 month/week section 显隐
- 新 'dashboard'：隐藏日历面板和待办面板（或仅隐藏待办），显示 `#dashboardView`
- 顶栏 view-switch 可保留原月/周按钮，工作台通过独立「📊 工作台」按钮切换
- 方案：`switchView('dashboard')` 设置 currentView='dashboard'，calendar-panel 隐藏（或缩小），todo-panel 隐藏，dashboardView 显示
- 新增 `switchView('list')` 的兼容（原代码可能已有日视图或列表视图，按现有处理）

顶栏 btnDashboard 点击事件：调用 `switchView('dashboard'); renderDashboard();`

**Task 6.2 统计聚合函数**

编写核心聚合逻辑：
- `getDashboardScope(period)` → 根据 period 返回 {startDate, endDate}
- `getSubordinateTodos(managerId, startDate, endDate)` → 获取 managerId 所有下属的、在范围内的 todos
- `computeStats(todos)` → 返回 {total, done, inProgress, dueSoon, overdue, newAttachments, completedRate}
- `groupByMember(todos)` → 返回 [{member, done, inProgress, overdue, duesoon, total}]
- `groupByFunc(todos)` → 返回 [{func, count}]
- `groupByStatus(todos)` → 返回按状态分组统计
- `getRecentDeliverables(todos, days=14)` → 按 completedAt 降序取最近 N 条有附件的完成记录
- `getHighlights(todos)` → 取逾期任务 + 高优先级任务，按紧急度排序

**Task 6.3 仪表盘渲染 renderDashboard()**

KPI 卡片：
- 填充 `#kpiGrid`，4个 KPI 卡片分别用蓝/绿/黄/红色调
- 每个卡片显示数字+小标签（完成率、逾期数等）

水平柱状图（按成员/按职能/按状态，根据当前维度切换）：
- 用纯 div+css 渲染 hbar-chart（不依赖canvas）
- 每行显示名称+进度条（已完成数/总数）+右侧数字
- `#chart1Title` 根据维度更新

近期交付成果时间线：
- 按日期分组，渲染 timeline-item（日期点、负责人、任务名、附件名）

饼图（按职能分布）：
- Canvas 2D 绘制，2~6 个扇区，按比例分配角度
- 旁边 legend 显示职能名+百分比

重点关注列表：
- 列出逾期和高优任务，每条显示 任务名/负责人/逾期天数 徽章，点击可跳转详情

明细表格：
- 遍历下属 todos（按状态/截止日期排序）
- 每行：负责人头像+姓名、任务名（可点击跳转）、截止日期、优先级彩点、状态徽章、成果（📎数量 或 -）、操作"查看"按钮

**Task 6.4 周期/维度切换事件**
- `#dashPeriod` change：更新 currentDashboardPeriod，重渲染
- `#dashDim` change：更新 currentDashboardDim，重渲染柱状图
- `#dashRefresh` click：重渲染

**Task 6.5 顶部身份显示刷新**
- `renderCurrentUserChip()`：更新头像颜色、姓名显示；如果当前用户是经理，chip 加一个小皇冠 👑 标识
- 设置面板切换 currentUserId 后，调用此函数+刷新列表

提交：
```bash
git add -A && git commit -m "feat(v4): phase6 - 经理汇总仪表盘（KPI/柱状图/饼图/时间线/明细表）"
```

---

### Phase 7：汇总报告生成 + 定时推送 + 深链路由 + 筛选增强（约 250 行 JS）

**Task 7.1 Markdown 报告生成**

- `generateMarkdownReport(manager, stats, period)`：返回 Markdown 字符串，按设计文档 §4.5.5 模板：
  - 标题（周期+经理名+生成时间）
  - 总体数据（总/完成/进行中/即将到期/逾期/新成果，含完成率）
  - 成员明细（每个成员名下列完成/进行中/逾期数和成果清单）
  - 重点关注（编号列表，逾期/高优任务）
  - 近期交付成果表格（时间/负责人/任务/交付物）
- `showReportModal(md)`：填充 `#reportMdContent.textContent=md`，打开 `#reportModal`
- 「📤 生成汇总报告」按钮：生成报告→调用 showReportModal
- `copyReportMd()`：navigator.clipboard.writeText
- `downloadReportMd()`：创建 Blob+`<a download>` 触发下载
- `printReport()`：打开新窗口渲染为 HTML，调用 window.print()
- `pushReportToFeishu()`：将报告分多条消息（或长消息卡片）推送到 webhook

**Task 7.2 定时推送调度**

- `schedulePushCheck()`：
  - 读取 webhookConfig.dailyPush / dailyPushTime / weeklyPush / weeklyPushTime / lastDailyPushDate / lastWeeklyPushDate
  - 获取当前时间，判断是否到点且今天/本周未推
  - 如果满足：获取当前用户（必须是manager）→ sendManagerSummaryPush → 更新 lastDailyPushDate/lastWeeklyPushDate → saveData
  - 启动 setTimeout 每60秒检查一次 schedulePushCheck（页面打开时）
  - 错过补发：页面加载时，如果今天是推送日且错过时间点（已过推送时间但未推），立即补发
- 页面加载完成后（DOMContentLoaded）：调用 schedulePushCheck() 启动定时器

**Task 7.3 URL Hash 深链路由**

- `handleRoute()`：页面加载时+hashchange事件时调用
  - 解析 `location.hash`
  - 若匹配 `#todo-{id}`：
    1. 查找 todo，确定 date
    2. 切换日历视图到对应周/月，currentDate 设为该月
    3. selectedDate = todo.date（若是day scope）或所在周
    4. 若有 source=feishu 参数，显示 #feishuBanner 5秒
    5. 等待渲染后，找到 DOM 中该 todo item：添加 highlight-pulse 类、scrollIntoView、自动展开详情（expandedTodoId=id）
    6. 若有 mention 参数，在详情中高亮对应@标签（加特殊背景色）
  - 若匹配 `#dashboard`：switchView('dashboard')，根据 period 参数设置 currentDashboardPeriod，renderDashboard
  - 若匹配 `#list`：应用 assignee/status/func 筛选参数
- 在 DOMContentLoaded 中调用 handleRoute()
- window.addEventListener('hashchange', handleRoute)

**Task 7.4 多维筛选增强**

扩展现有筛选 UI：
- 负责人下拉：全部 / 我负责的 / 我的下属（仅经理可见）/ 各成员（多选）/ 未分配
- 状态下拉：全部 / 进行中 / 已完成 / 即将到期 / 已逾期
- 职能下拉：从 members 的 func 字段动态生成
- 排序下拉：截止日期↑↓ / 优先级 / 创建时间 / 负责人姓名

筛选逻辑函数：
- `applyFilters(todos)` 返回根据当前筛选条件过滤后的数组
- `applySort(todos)` 根据排序字段排序

快捷标签区（在 "📋 待办事项" 标题下方）：
- 标签：#全部 / #我负责的 / #我的下属（经理可见）/ #已逾期(N) / #本周到期 / #有新成果
- 点击标签应用对应筛选条件，更新 active 态

修改现有 renderTodoList 函数：
- todos 过滤前先调用 applyFilters+applySort
- 待办项的显示状态色条基于 getTodoStatus

**Task 7.5 存储容量告警**

- `checkStorageQuota()`：计算 localStorage 已用估算 / 5MB
- 已用>80%：顶部显示黄色提示条（新增一个 `.storage-warning-bar`）
- 已用>95%：红色提示，拒绝新附件上传（在 handleFileSelection 前置检查）

提交：
```bash
git add -A && git commit -m "feat(v4): phase7 - 报告生成/定时推送/深链路由/筛选增强/容量告警"
```

---

### Phase 8：整合、初始化、打磨、验证

**Task 8.1 初始化流程整合**

修改底部 DOMContentLoaded 初始化（或 window.onload）：
1. 调用 loadData()
2. 调用 renderCurrentUserChip()
3. 绑定顶栏所有新按钮事件：btnDashboard、btnSettings、currentUserChip（点击切换身份）
4. 绑定设置/提交/报告模态框的相关事件
5. 绑定 dashboard 控件事件
6. 绑定文件上传 dropZone
7. 请求 Notification 权限（如果用户尚未授权且配置了 webhook 的也不强求）
8. 调用原有 init/renderCalendar/renderTodoList
9. 调用 schedulePushCheck()
10. 调用 handleRoute() 处理深链
11. 调用 checkStorageQuota()

**Task 8.2 顶栏"我的下属"按钮（经理可见性控制）**

- currentUserChip 点击后弹出一个小菜单：切换身份（列出所有成员）
- 普通成员不显示"我的下属"相关选项
- 非经理身份进入 dashboard 时，显示个人工作台（只看自己的，不显示团队汇总）

**Task 8.3 个人工作台（非经理）**

当 currentUser.role !== 'manager' 时，点击"📊 工作台"：
- 视图类似 dashboard，但只统计自己的数据（KPIs 显示个人待办数、已完成、即将到期、逾期）
- 不显示成员分布图和下属明细，显示"我的成就"（本周完成N项）
- 不显示"推送到飞书"群发按钮

**Task 8.4 边界情况处理**

- 无成员：在首次使用时默认创建一个"我"的成员
- 无 webhook 配置：所有发送降级为 Notification API + toast 提示"请先配置飞书Webhook"
- localStorage 满：保存时 QuotaExceededError 捕获→提示清理附件
- 过期日期判断：todo.date 为空时（无截止日期），不算逾期，归入进行中
- 深链 todo-id 不存在：显示"该待办不存在或已被删除"toast
- 附件删除权限：上传者本人或其经理可删

**Task 8.5 手动验证清单（浏览器中逐项测试）**

1. 页面加载无报错，默认显示v3示例数据（已迁移为v4格式）
2. 顶栏显示 v4.0 · 协作汇总版，有工作台按钮和⚙️按钮
3. 点击⚙️打开设置，四个Tab可切换
4. 成员管理Tab能看到默认"我"和"李经理"，可编辑字段/添加新成员
5. 群组管理Tab可创建群组
6. 飞书集成Tab能看到Webhook配置表单和折叠指引
7. 点击"+ 新建待办"，弹窗中有负责人区、通知群组、需提交成果checkbox
8. 输入@能弹出成员下拉，键盘可选，选中后变蓝色标签
9. 创建一个带负责人的待办（选自己），保存后列表项显示头像
10. 标记完成（勾选需提交成果）→弹出提交成果弹窗→可拖入文件→确认完成→todo变为已完成状态色
11. 点击已完成 todo 的详情，能看到附件网格，图片可点击预览，其他文件可下载
12. 切换身份为"李经理"（通过currentUserChip或设置面板）→点击📊工作台→看到仪表盘KPI/图表/表格
13. 仪表盘周期/维度切换可正常重渲染
14. 点击"📤 生成汇总报告"弹出Markdown预览，可复制/下载/打印
15. URL加 `#todo-{某个id}` 回车→页面自动定位+高亮脉冲
16. 筛选栏的"我负责的/已逾期"等快捷标签可正常过滤
17. 数据管理Tab可看到存储容量条、导出JSON
18. 控制台无JavaScript错误

**Task 8.6 修复验证中发现的问题**

根据测试发现的问题逐一修复，每修复一个提交一次：
```bash
git commit -m "fix(v4): 修复XXX问题"
```

最终提交：
```bash
git add -A && git commit -m "feat(v4): phase8 - 整合初始化、个人工作台、边界处理、打磨"
```

---

## TDD / Verification Steps

由于本项目是纯前端单HTML文件（无测试框架），采用**浏览器手动验证**作为TDD替代：

1. **每个Phase完成后**：浏览器打开文件，F12 Console 无红色错误，核心流程可走通
2. **Phase 0 后**：localStorage 中应看到 `{version:4,...}` 结构
3. **Phase 3 后**：可在控制台手动调 `parseMentions('请@[m_xxx]协助')` 验证解析
4. **Phase 5 后**：完整走一遍创建→分配→完成→上传成果流程
5. **Phase 6 后**：切换经理身份查看仪表盘
6. **Phase 7 后**：手动构造 hash URL 验证深链，生成报告
7. **最终**：按 Task 8.5 清单逐项验证

Lint/格式检查：本项目无构建工具，无lint命令。直接用浏览器验证运行时正确性。

---

## Commits Summary（预期约 8 个主提交）

| # | Commit Message | 估算行数 |
|---|---------------|---------|
| 1 | feat(v4): phase0 - 数据模型v4迁移、常量、工具函数 | ~150 JS |
| 2 | feat(v4): phase1 - CSS扩展 | ~350 CSS |
| 3 | feat(v4): phase2 - HTML视图骨架 | ~250 HTML |
| 4 | feat(v4): phase3 - @提及/负责人/附件/Webhook | ~600 JS |
| 5 | feat(v4): phase4 - 设置面板四个Tab | ~400 JS |
| 6 | feat(v4): phase5 - 编辑弹窗增强/列表/完成流程 | ~350 JS+HTML |
| 7 | feat(v4): phase6 - 经理汇总仪表盘 | ~350 JS |
| 8 | feat(v4): phase7 - 报告/定时推送/深链/筛选 | ~250 JS |
| 9 | feat(v4): phase8 - 整合初始化、个人工作台、打磨 | ~100 JS |

合计：约 1800 行 JS + 350 行 CSS + 250 行 HTML，与设计文档估算一致。

---

## Key Decision Notes

1. **存储键不变**：继续使用 `magong_todo_calendar`（而非改名为 `calendarAssistantData`），以确保 v3 数据自动迁移
2. **状态派生而非状态机**：不引入 submitted/approved/rejected 状态，用 getTodoStatus() 从 `done`+`date` 派生四种状态
3. **图表纯CSS+Canvas**：不引入Chart.js等第三方库，水平柱状图用div，饼图用Canvas 2D自绘
4. **Webhook no-cors**：飞书webhook支持跨域直连，但 no-cors 模式下前端无法读响应；通过"测试消息"按钮以用户是否在飞书实际收到消息判断成功
5. **签名安全**：HMAC-SHA256 在前端用 Web Crypto 生成，密钥留在浏览器本地，不上传任何服务器
6. **定时推送限制**：纯前端无后台进程，页面必须保持打开；错过推送时间点时补发
7. **单文件承诺**：所有代码均写在 `智能日历助手.html` 中，不拆分文件、不引入外部依赖
