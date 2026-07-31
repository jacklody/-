/**
 * 提醒中心页面
 */

function renderReminder() {
  renderHeader('提醒中心', '2026年7月31日 星期五');
  
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${renderOverdueAlert()}
    
    <div style="margin-top:20px; display:flex; gap:20px;">
      <!-- 左侧内容 -->
      <div style="flex:1; display:flex; flex-direction:column; gap:20px;">
        ${renderTodayTimeline()}
        ${renderFuture7Days()}
      </div>
      
      <!-- 右侧设置 -->
      <aside style="width:320px; flex-shrink:0;">
        ${renderReminderSettings()}
      </aside>
    </div>
  `;
}

// 渲染逾期提醒
function renderOverdueAlert() {
  return `
    <div role="alert" style="display:flex; align-items:center; gap:12px; padding:12px 16px; border:1px solid transparent; border-left-width:3px; border-left-color:var(--state-error); border-radius:var(--cal-radius-large); background:rgba(255,71,87,0.08);">
      <div style="width:36px; height:36px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-medium); background:var(--state-error-muted); color:var(--state-error); flex-shrink:0;">
        <i data-lucide="alert-triangle" style="width:20px; height:20px;"></i>
      </div>
      <div style="flex:1; min-width:0;">
        <div style="font-size:13px; font-weight:500; color:var(--cal-foreground);">2 项待办已逾期</div>
        <div style="font-size:11px; color:var(--cal-muted-foreground);">建议立即处理，以免影响后续采购与付款安排</div>
      </div>
      <button class="btn" style="background:var(--state-error); color:var(--state-error-foreground); gap:6px;">
        <i data-lucide="zap" style="width:14px; height:14px;"></i>
        <span>立即处理</span>
      </button>
      <button class="btn btn-ghost btn-icon" aria-label="关闭提醒">
        <i data-lucide="x" style="width:16px; height:16px;"></i>
      </button>
    </div>
  `;
}

// 渲染今日时间线
function renderTodayTimeline() {
  const timelineItems = [
    { time: '09:00', status: 'completed', title: '每日采购晨会纪要整理', source: 'feishu' },
    { time: '10:00', status: 'completed', title: '检查昨日钢材入库记录', source: 'manual' },
    { time: '14:00', status: 'current', priority: 'urgent', title: '核对Q3钢材采购报价单', source: 'feishu', badges: ['采购报价单 #Q3-2026', '3 位负责人'] },
    { time: '15:30', status: 'pending', priority: 'normal', title: '供应商月度评估电话会议', source: 'email', badges: ['电话会议', '5 位参会人'] },
    { time: '16:30', status: 'pending', priority: 'urgent', title: '提交供应商付款审批流程', source: 'email', badges: ['付款审批单', '预计 15 分钟'] },
    { time: '18:00', status: 'pending', priority: 'secondary', title: '整理今日工作日报', source: 'manual', badges: ['日报模板', '预计 20 分钟'] }
  ];
  
  return `
    <section class="card">
      <div style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--cal-border-subtle);">
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-medium); background:var(--state-info-muted); color:var(--state-info);">
            <i data-lucide="list-checks" style="width:16px; height:16px;"></i>
          </div>
          <div>
            <h3 class="cal-h3">今日提醒</h3>
            <div class="cal-body-xs" style="color:var(--cal-muted-foreground);">2026年7月31日 星期五</div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge badge-info">
            <i data-lucide="check-check" style="width:12px; height:12px;"></i>
            已完成 2 / 6
          </span>
          <button class="btn btn-ghost btn-icon" aria-label="筛选">
            <i data-lucide="sliders-horizontal" style="width:16px; height:16px;"></i>
          </button>
        </div>
      </div>
      
      <div style="padding:20px;">
        <div class="timeline">
          ${timelineItems.map(item => renderTimelineItem(item)).join('')}
        </div>
      </div>
    </section>
  `;
}

// 渲染时间线项
function renderTimelineItem(item) {
  const isCompleted = item.status === 'completed';
  const isCurrent = item.status === 'current';
  const color = isCompleted ? 'var(--state-success)' : getPriorityColor(item.priority);
  const sourceIcon = getSourceIcon(item.source);
  
  return `
    <div class="timeline-item ${isCurrent ? 'current' : ''}">
      <div class="timeline-time">${item.time}</div>
      <div class="timeline-dot" style="--dot-color: ${color};">
        <span style="width:10px; height:10px; border-radius:50%; background:${color}; box-shadow:0 0 0 3px var(--cal-card);"></span>
      </div>
      <div class="timeline-content" style="${isCompleted ? 'opacity:0.7;' : ''}">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge ${isCompleted ? 'badge-success' : (item.priority === 'urgent' ? 'badge-error' : (item.priority === 'secondary' ? 'badge-warning' : 'badge-info'))}">
            ${isCompleted ? '<i data-lucide="check" style="width:12px; height:12px;"></i>已完成' : (item.priority === 'urgent' ? '紧急' : (item.priority === 'secondary' ? '次要' : '正常'))}
          </span>
          <span style="display:flex; align-items:center; gap:4px; font-size:11px; color:var(--cal-muted-foreground);">
            <i data-lucide="${sourceIcon}" style="width:12px; height:12px;"></i>
            ${item.source === 'feishu' ? '飞书' : (item.source === 'email' ? '邮件' : '手动')}
          </span>
          ${isCurrent ? '<span class="badge badge-info" style="margin-left:auto;"><i data-lucide="clock" style="width:12px; height:12px;"></i>即将到来</span>' : ''}
        </div>
        <div style="margin-top:4px; font-size:13px; ${isCompleted ? 'text-decoration:line-through;' : ''} font-weight:${isCurrent ? '500' : '400'}; color:${isCompleted ? 'var(--cal-muted-foreground)' : 'var(--cal-foreground)'};">
          ${item.title}
        </div>
        ${item.badges ? `
          <div style="margin-top:6px; display:flex; flex-wrap:wrap; gap:8px; font-size:11px; color:var(--cal-muted-foreground);">
            ${item.badges.map(badge => `<span style="display:flex; align-items:center; gap:4px;"><i data-lucide="link" style="width:12px; height:12px;"></i>${badge}</span>`).join('')}
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

// 渲染未来7天
function renderFuture7Days() {
  const days = [
    { date: '8月1日', weekday: '周六', count: 3, items: ['周报汇总整理', '供应商合同复审'] },
    { date: '8月2日', weekday: '周日', count: 2, items: ['月度库存盘点', '客户回访跟进'] },
    { date: '8月3日', weekday: '周一', count: 4, items: ['Q3采购计划评审', '新材料样品测试'] },
    { date: '8月4日', weekday: '周二', count: 1, items: ['季度财务对账'] },
    { date: '8月5日', weekday: '周三', count: 2, items: ['供应商拜访准备', '成本分析报告'] }
  ];
  
  return `
    <section class="card">
      <div style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--cal-border-subtle);">
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-medium); background:var(--cal-muted); color:var(--cal-muted-foreground);">
            <i data-lucide="calendar-days" style="width:16px; height:16px;"></i>
          </div>
          <div>
            <h3 class="cal-h3">未来7天</h3>
            <div class="cal-body-xs" style="color:var(--cal-muted-foreground);">8月1日 - 8月7日 · 共 18 项提醒</div>
          </div>
        </div>
        <button class="btn btn-sm btn-ghost" style="gap:4px;">
          <span>查看全部</span>
          <i data-lucide="chevron-right" style="width:14px; height:14px;"></i>
        </button>
      </div>
      
      <div style="padding:16px 20px;">
        <div style="display:flex; gap:12px; overflow-x:auto; padding-bottom:4px;" class="no-scrollbar">
          ${days.map(day => `
            <div style="width:156px; flex-shrink:0; padding:12px; border:1px solid var(--cal-border); border-radius:var(--cal-radius-medium); background:var(--cal-card-elevated); transition:border-color 0.2s;" onmouseover="this.style.borderColor='var(--cal-primary)'" onmouseout="this.style.borderColor='var(--cal-border)'">
              <div style="display:flex; align-items:start; justify-content:space-between; gap:8px;">
                <div>
                  <div style="font-size:13px; font-weight:600; color:var(--cal-foreground);">${day.date}</div>
                  <div style="font-size:11px; color:${day.weekday.includes('周') && !day.weekday.includes('周') ? 'var(--cal-muted-foreground)' : 'var(--state-warning)'};">${day.weekday}</div>
                </div>
                <span class="badge badge-info">${day.count}</span>
              </div>
              <div style="margin-top:10px; display:flex; flex-direction:column; gap:6px;">
                ${day.items.map((item, i) => `
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span style="width:6px; height:6px; border-radius:50%; background:${i === 0 && day.count > 2 ? 'var(--state-error)' : 'var(--state-info)'};"></span>
                    <span style="font-size:11px; color:var(--cal-muted-foreground); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${item}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}

// 渲染提醒设置
function renderReminderSettings() {
  return `
    <div style="display:flex; flex-direction:column; gap:12px;">
      <div style="padding:0 4px; display:flex; align-items:center; gap:8px;">
        <i data-lucide="settings-2" style="width:16px; height:16px; color:var(--cal-muted-foreground);"></i>
        <h3 class="cal-h3">提醒设置</h3>
      </div>
      
      ${renderSettingCard('clock', '默认提醒时间', [
        { label: '提前30分钟提醒', desc: '事件开始前 30 分钟推送', on: true },
        { label: '提前1天提醒', desc: '事件前一日 09:00 推送', on: true },
        { label: '提前3天提醒', desc: '事件前 3 日 09:00 推送', on: false }
      ])}
      
      ${renderRemindMethods()}
      
      ${renderSettingCard('moon', '免打扰时段', [
        { label: '周末免打扰', desc: '周六、周日不推送提醒', on: false }
      ], true)}
      
      ${renderSettingCard('alert-circle', '逾期自动提醒', [
        { label: '逾期项每日提醒', desc: '每天 09:00 重新提醒未完成项', on: true }
      ])}
    </div>
  `;
}

// 渲染设置卡片
function renderSettingCard(icon, title, items, hasExtra = false) {
  return `
    <div class="card">
      <div style="display:flex; align-items:center; gap:8px; padding:12px 16px; border-bottom:1px solid var(--cal-border-subtle);">
        <i data-lucide="${icon}" style="width:16px; height:16px; color:var(--cal-primary);"></i>
        <span class="cal-h4">${title}</span>
      </div>
      <div style="padding:0 16px;">
        ${items.map(item => `
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 0; border-bottom:1px solid var(--cal-border-subtle);">
            <div style="min-width:0;">
              <div style="font-size:13px; color:var(--cal-foreground);">${item.label}</div>
              <div style="font-size:11px; color:var(--cal-muted-foreground);">${item.desc}</div>
            </div>
            <button class="switch" data-on="${item.on}" onclick="this.dataset.on = this.dataset.on === 'true' ? 'false' : 'true'">
              <span class="switch-knob"></span>
            </button>
          </div>
        `).join('')}
        ${hasExtra ? `
          <div style="padding:12px 0;">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 12px; border-radius:var(--cal-radius-medium); background:var(--cal-card-elevated);">
              <div style="display:flex; align-items:center; gap:8px;">
                <i data-lucide="moon-star" style="width:16px; height:16px; color:var(--state-warning);"></i>
                <span style="font-size:13px; color:var(--cal-muted-foreground);">夜间免打扰</span>
              </div>
              <div style="display:flex; align-items:center; gap:6px; font-family:var(--cal-font-mono); font-size:13px; color:var(--cal-foreground);">
                <span>22:00</span>
                <i data-lucide="arrow-right" style="width:14px; height:14px; color:var(--cal-muted-foreground);"></i>
                <span>08:00</span>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

// 渲染提醒方式
function renderRemindMethods() {
  const methods = [
    { name: '应用内通知', icon: 'smartphone', checked: true },
    { name: '邮件通知', icon: 'mail', checked: true },
    { name: '飞书推送', icon: 'message-square', checked: true },
    { name: '微信通知', icon: 'message-circle', checked: false, disabled: true }
  ];
  
  return `
    <div class="card">
      <div style="display:flex; align-items:center; gap:8px; padding:12px 16px; border-bottom:1px solid var(--cal-border-subtle);">
        <i data-lucide="bell-ring" style="width:16px; height:16px; color:var(--cal-primary);"></i>
        <span class="cal-h4">提醒方式</span>
      </div>
      <div style="padding:0 16px;">
        ${methods.map(method => `
          <label style="display:flex; align-items:center; gap:10px; padding:12px 0; border-bottom:1px solid var(--cal-border-subtle); cursor:${method.disabled ? 'not-allowed' : 'pointer'};">
            <span class="checkbox" data-checked="${method.checked}" data-disabled="${method.disabled}">
              ${method.checked && !method.disabled ? '<i data-lucide="check" style="width:12px; height:12px;"></i>' : ''}
            </span>
            <span style="font-size:13px; color:${method.disabled ? 'var(--cal-muted-foreground)' : 'var(--cal-foreground)'};">${method.name}</span>
            <i data-lucide="${method.icon}" style="width:14px; height:14px; margin-left:auto; color:var(--cal-muted-foreground);"></i>
            ${method.disabled ? '<span class="badge" style="background:var(--cal-muted); color:var(--cal-muted-foreground);">未连接</span>' : ''}
          </label>
        `).join('')}
      </div>
      <div style="padding:12px 16px; border-top:1px solid var(--cal-border-subtle);">
        <a href="#integration" class="btn btn-outline" style="width:100%; justify-content:center; gap:6px;">
          <i data-lucide="plug" style="width:16px; height:16px;"></i>
          <span>配置集成通知</span>
          <i data-lucide="chevron-right" style="width:14px; height:14px;"></i>
        </a>
      </div>
    </div>
  `;
}