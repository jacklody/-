/**
 * 智能导入页面
 */

function renderSmartImport() {
  renderHeader('智能导入', null);
  
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div style="max-width:960px; margin:0 auto;">
      ${renderImportIntro()}
      
      <div style="margin-top:24px; display:grid; grid-template-columns:repeat(2, 1fr); gap:20px;">
        ${renderImportCard('飞书', 'message-square', 'var(--state-info)', [
          '自动识别飞书消息中的待办事项',
          '支持群聊、私聊、文档评论',
          '智能提取时间、优先级、标签'
        ], '已连接', true)}
        
        ${renderImportCard('邮件', 'mail', 'var(--state-success)', [
          '从邮件中提取待办任务',
          '支持Outlook、Gmail等主流邮箱',
          '自动解析截止时间和关键信息'
        ], '已连接', true)}
        
        ${renderImportCard('微信', 'message-circle', 'var(--state-warning)', [
          '识别微信聊天中的待办事项',
          '支持文本、图片、文件',
          '一键同步到日历助手'
        ], '未连接', false)}
        
        ${renderImportCard('手动导入', 'upload', 'var(--cal-primary)', [
          '从Excel、CSV文件导入',
          '支持自定义字段映射',
          '批量创建待办任务'
        ], null, null)}
      </div>
      
      ${renderRecentImports()}
    </div>
  `;
}

// 渲染导入介绍
function renderImportIntro() {
  return `
    <div style="padding:24px; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:linear-gradient(135deg, rgba(74,158,255,0.05) 0%, rgba(74,158,255,0.02) 100%);">
      <div style="display:flex; align-items:flex-start; gap:16px;">
        <div style="width:48px; height:48px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-large); background:var(--state-info-muted); color:var(--cal-primary); flex-shrink:0;">
          <i data-lucide="sparkles" style="width:24px; height:24px;"></i>
        </div>
        <div style="flex:1;">
          <h2 class="cal-h2" style="margin-bottom:8px;">智能导入 · 多源待办聚合</h2>
          <p style="font-size:13px; color:var(--cal-muted-foreground); line-height:1.6;">
            从飞书、邮件、微信等多种来源自动识别待办事项，智能提取时间、优先级、标签等信息，一键同步到日历助手，让待办管理更高效。
          </p>
        </div>
      </div>
    </div>
  `;
}

// 渲染导入卡片
function renderImportCard(title, icon, color, features, status, connected) {
  return `
    <div class="card" style="height:100%; display:flex; flex-direction:column;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--cal-border-subtle);">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:36px; height:36px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-medium); background:${color === 'var(--cal-primary)' ? 'var(--state-info-muted)' : 'var(--state-info-muted)'}; color:${color};">
              <i data-lucide="${icon}" style="width:18px; height:18px;"></i>
            </div>
            <span class="cal-h3">${title}</span>
          </div>
          ${status ? `<span class="badge ${connected ? 'badge-success' : ''}" style="${!connected ? 'background:var(--cal-muted); color:var(--cal-muted-foreground);' : ''}">${status}</span>` : ''}
        </div>
      </div>
      
      <div style="flex:1; padding:16px 20px;">
        <ul style="list-style:none; display:flex; flex-direction:column; gap:8px;">
          ${features.map(feature => `
            <li style="display:flex; align-items:flex-start; gap:8px; font-size:13px; color:var(--cal-foreground);">
              <i data-lucide="check" style="width:14px; height:14px; color:var(--state-success); flex-shrink:0; margin-top:2px;"></i>
              <span>${feature}</span>
            </li>
          `).join('')}
        </ul>
      </div>
      
      <div style="padding:16px 20px; border-top:1px solid var(--cal-border-subtle);">
        ${connected !== null ? `
          <button class="btn ${connected ? 'btn-ghost' : 'btn-primary'}" style="width:100%; justify-content:center;">
            <i data-lucide="${connected ? 'settings' : 'plus'}" style="width:16px; height:16px;"></i>
            <span>${connected ? '管理设置' : '立即连接'}</span>
          </button>
        ` : `
          <button class="btn btn-outline" style="width:100%; justify-content:center;">
            <i data-lucide="upload" style="width:16px; height:16px;"></i>
            <span>上传文件</span>
          </button>
        `}
      </div>
    </div>
  `;
}

// 渲染最近导入
function renderRecentImports() {
  const recentImports = [
    { time: '14:32', source: 'feishu', title: '核对Q3钢材采购报价单', status: 'success' },
    { time: '12:18', source: 'email', title: '供应商付款审批流程', status: 'success' },
    { time: '昨天', source: 'feishu', title: '每日采购晨会纪要', status: 'success' },
    { time: '昨天', source: 'email', title: '供应商月度评估会议', status: 'pending' }
  ];
  
  return `
    <div class="card" style="margin-top:32px;">
      <div style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--cal-border-subtle);">
        <div style="display:flex; align-items:center; gap:10px;">
          <i data-lucide="history" style="width:16px; height:16px; color:var(--cal-primary);"></i>
          <span class="cal-h4">最近导入</span>
        </div>
        <button class="btn btn-sm btn-ghost" style="gap:4px;">
          <span>查看全部</span>
          <i data-lucide="chevron-right" style="width:14px; height:14px;"></i>
        </button>
      </div>
      
      <div style="padding:0;">
        ${recentImports.map((item, index) => `
          <div style="display:flex; align-items:center; gap:12px; padding:12px 20px; ${index < recentImports.length - 1 ? 'border-bottom:1px solid var(--cal-border-subtle);' : ''}">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-medium); background:var(--state-info-muted); color:var(--state-info);">
              <i data-lucide="${getSourceIcon(item.source)}" style="width:16px; height:16px;"></i>
            </div>
            <div style="flex:1; min-width:0;">
              <div style="font-size:13px; color:var(--cal-foreground);">${item.title}</div>
              <div style="font-size:11px; color:var(--cal-muted-foreground);">
                ${item.time} · ${item.source === 'feishu' ? '飞书' : '邮件'}
              </div>
            </div>
            <span class="badge ${item.status === 'success' ? 'badge-success' : 'badge-warning'}">
              <i data-lucide="${item.status === 'success' ? 'check-circle-2' : 'clock'}" style="width:12px; height:12px;"></i>
              ${item.status === 'success' ? '已导入' : '处理中'}
            </span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}