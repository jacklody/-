/**
 * 集成设置页面
 */

function renderIntegration() {
  renderHeader('集成设置', null);
  
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div style="max-width:960px; margin:0 auto;">
      ${renderIntegrationHeader()}
      
      <div style="margin-top:24px; display:flex; flex-direction:column; gap:16px;">
        ${renderIntegrationItem('飞书', 'message-square', 'var(--state-info)', 
          '企业协作平台，支持消息、文档、日历同步',
          true, [
            '自动识别飞书消息中的待办',
            '同步飞书日历事件',
            '接收飞书提醒推送'
          ]
        )}
        
        ${renderIntegrationItem('邮件', 'mail', 'var(--state-success)', 
          '支持Outlook、Gmail等主流邮箱',
          true, [
            '从邮件中提取待办任务',
            '邮件提醒同步到日历助手',
            '定时扫描新邮件'
          ]
        )}
        
        ${renderIntegrationItem('微信', 'message-circle', 'var(--state-warning)', 
          '微信消息识别与同步',
          false, [
            '识别微信聊天中的待办',
            '同步微信群聊任务',
            '微信提醒推送'
          ]
        )}
        
        ${renderIntegrationItem('企业微信', 'briefcase', 'var(--cal-primary)', 
          '企业微信待办同步',
          false, [
            '识别企业微信消息中的待办',
            '同步企业微信日程',
            '企业微信提醒推送'
          ]
        )}
        
        ${renderIntegrationItem('钉钉', 'bell', '#0089FF', 
          '钉钉待办与日程同步',
          false, [
            '识别钉钉消息中的待办',
            '同步钉钉日程事件',
            '钉钉提醒推送'
          ]
        )}
      </div>
      
      ${renderSyncSettings()}
    </div>
  `;
}

// 渲染集成头部
function renderIntegrationHeader() {
  return `
    <div style="padding:24px; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:var(--cal-card);">
      <div style="display:flex; align-items:flex-start; gap:16px;">
        <div style="width:48px; height:48px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-large); background:var(--state-info-muted); color:var(--cal-primary); flex-shrink:0;">
          <i data-lucide="plug" style="width:24px; height:24px;"></i>
        </div>
        <div style="flex:1;">
          <h2 class="cal-h2" style="margin-bottom:8px;">集成设置</h2>
          <p style="font-size:13px; color:var(--cal-muted-foreground); line-height:1.6;">
            连接飞书、邮件、微信等外部平台，实现待办任务的多源同步与统一管理。已连接的平台将自动识别和导入待办事项。
          </p>
        </div>
      </div>
      
      <div style="margin-top:20px; padding-top:20px; border-top:1px solid var(--cal-border-subtle); display:flex; gap:12px;">
        <div style="flex:1; padding:12px; border-radius:var(--cal-radius-medium); background:var(--cal-muted);">
          <div style="font-size:22px; font-weight:600; color:var(--cal-foreground);">2</div>
          <div style="font-size:11px; color:var(--cal-muted-foreground);">已连接平台</div>
        </div>
        <div style="flex:1; padding:12px; border-radius:var(--cal-radius-medium); background:var(--cal-muted);">
          <div style="font-size:22px; font-weight:600; color:var(--cal-foreground);">15</div>
          <div style="font-size:11px; color:var(--cal-muted-foreground);">本周导入任务</div>
        </div>
        <div style="flex:1; padding:12px; border-radius:var(--cal-radius-medium); background:var(--cal-muted);">
          <div style="font-size:22px; font-weight:600; color:var(--cal-foreground);">98%</div>
          <div style="font-size:11px; color:var(--cal-muted-foreground);">识别准确率</div>
        </div>
      </div>
    </div>
  `;
}

// 渲染集成项
function renderIntegrationItem(name, icon, color, description, connected, features) {
  return `
    <div class="card">
      <div style="display:flex; align-items:center; gap:16px; padding:20px;">
        <div style="width:48px; height:48px; display:flex; align-items:center; justify-content:center; border-radius:var(--cal-radius-large); background:${color === 'var(--cal-primary)' ? 'var(--state-info-muted)' : 'var(--state-info-muted)'}; color:${color}; flex-shrink:0;">
          <i data-lucide="${icon}" style="width:24px; height:24px;"></i>
        </div>
        
        <div style="flex:1; min-width:0;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span class="cal-h3">${name}</span>
            ${connected ? '<span class="badge badge-success"><i data-lucide="check" style="width:12px; height:12px;"></i>已连接</span>' : '<span class="badge" style="background:var(--cal-muted); color:var(--cal-muted-foreground);">未连接</span>'}
          </div>
          <div style="font-size:13px; color:var(--cal-muted-foreground);">${description}</div>
          
          <div style="margin-top:12px; display:flex; flex-wrap:wrap; gap:12px;">
            ${features.map(feature => `
              <div style="display:flex; align-items:center; gap:6px; font-size:12px; color="${connected ? 'var(--cal-foreground)' : 'var(--cal-muted-foreground)'}">
                <i data-lucide="check" style="width:14px; height:14px; color:${connected ? 'var(--state-success)' : 'var(--cal-border)'};"></i>
                <span>${feature}</span>
              </div>
            `).join('')}
          </div>
        </div>
        
        <div style="flex-shrink:0; display:flex; gap:8px;">
          ${connected ? `
            <button class="btn btn-ghost" style="gap:6px;">
              <i data-lucide="settings" style="width:16px; height:16px;"></i>
              <span>设置</span>
            </button>
            <button class="btn btn-ghost" style="color:var(--state-error); gap:6px;">
              <i data-lucide="link-off" style="width:16px; height:16px;"></i>
              <span>断开</span>
            </button>
          ` : `
            <button class="btn btn-primary" style="gap:6px;">
              <i data-lucide="link" style="width:16px; height:16px;"></i>
              <span>连接</span>
            </button>
          `}
        </div>
      </div>
    </div>
  `;
}

// 渲染同步设置
function renderSyncSettings() {
  return `
    <div class="card" style="margin-top:32px;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--cal-border-subtle);">
        <div style="display:flex; align-items:center; gap:10px;">
          <i data-lucide="refresh-cw" style="width:16px; height:16px; color:var(--cal-primary);"></i>
          <span class="cal-h4">同步设置</span>
        </div>
      </div>
      
      <div style="padding:0 20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:16px 0; border-bottom:1px solid var(--cal-border-subtle);">
          <div>
            <div style="font-size:13px; color:var(--cal-foreground);">自动同步</div>
            <div style="font-size:11px; color:var(--cal-muted-foreground);">每隔15分钟自动同步已连接平台的数据</div>
          </div>
          <button class="switch" data-on="true" onclick="this.dataset.on = this.dataset.on === 'true' ? 'false' : 'true'">
            <span class="switch-knob"></span>
          </button>
        </div>
        
        <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:16px 0; border-bottom:1px solid var(--cal-border-subtle);">
          <div>
            <div style="font-size:13px; color:var(--cal-foreground);">仅同步工作时间</div>
            <div style="font-size:11px; color:var(--cal-muted-foreground);">仅在周一至周五 09:00-18:00 期间同步</div>
          </div>
          <button class="switch" data-on="false" onclick="this.dataset.on = this.dataset.on === 'true' ? 'false' : 'true'">
            <span class="switch-knob"></span>
          </button>
        </div>
        
        <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:16px 0;">
          <div>
            <div style="font-size:13px; color:var(--cal-foreground);">同步历史数据</div>
            <div style="font-size:11px; color:var(--cal-muted-foreground);">首次连接时同步最近30天的待办数据</div>
          </div>
          <button class="switch" data-on="true" onclick="this.dataset.on = this.dataset.on === 'true' ? 'false' : 'true'">
            <span class="switch-knob"></span>
          </button>
        </div>
      </div>
      
      <div style="padding:16px 20px; border-top:1px solid var(--cal-border-subtle); display:flex; align-items:center; gap:12px; background:var(--cal-muted);">
        <i data-lucide="info" style="width:16px; height:16px; color:var(--cal-primary); flex-shrink:0;"></i>
        <span style="font-size:12px; color:var(--cal-muted-foreground);">上次同步时间：2026-07-31 14:30 · 下次同步时间：2026-07-31 14:45</span>
      </div>
    </div>
  `;
}