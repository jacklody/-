/**
 * 工作台·周视图页面
 * 支持拖拽待办卡片
 */

function renderWeekView() {
  renderHeader('周视图', '2026年7月31日 · 周五');
  
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:12px; height:100%;">
      ${renderWeekStats()}
      ${renderWeekNavigation()}
      ${renderDragHint()}
      ${renderWeekGrid()}
      ${renderWeekSummary()}
    </div>
  `;
  
  // 初始化拖拽功能
  initDragAndDrop();
}

// 渲染周统计
function renderWeekStats() {
  return `
    <div class="stats-grid" style="gap:12px;">
      <div class="stat-card" style="padding:12px;">
        <div class="stat-icon" style="width:36px; height:36px; background: var(--state-info-muted); color: var(--state-info);">
          <i data-lucide="list-todo" style="width:18px; height:18px;"></i>
        </div>
        <div>
          <div class="stat-label">本周待办</div>
          <div class="stat-value" style="font-size:17px;">15</div>
          <span style="font-size:11px; color: var(--state-error); font-weight:500;">4 紧急</span>
        </div>
      </div>
      
      <div class="stat-card" style="padding:12px;">
        <div class="stat-icon" style="width:36px; height:36px; background: var(--state-success-muted); color: var(--state-success);">
          <i data-lucide="check-circle-2" style="width:18px; height:18px;"></i>
        </div>
        <div>
          <div class="stat-label">已完成</div>
          <div class="stat-value" style="font-size:17px;">8</div>
          <span style="font-size:11px; color: var(--cal-muted-foreground);">本周</span>
        </div>
      </div>
      
      <div class="stat-card" style="padding:12px;">
        <div class="stat-icon" style="width:36px; height:36px; background: var(--state-error-muted); color: var(--state-error);">
          <i data-lucide="alarm-clock" style="width:18px; height:18px;"></i>
        </div>
        <div>
          <div class="stat-label">逾期</div>
          <div class="stat-value" style="font-size:17px; color:var(--state-error);">2</div>
          <span style="font-size:11px; color: var(--state-error);">需立即处理</span>
        </div>
      </div>
      
      <div class="stat-card" style="padding:12px;">
        <div class="stat-icon" style="width:36px; height:36px; background: var(--state-info-muted); color: var(--cal-primary);">
          <i data-lucide="trending-up" style="width:18px; height:18px;"></i>
        </div>
        <div style="flex:1;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="stat-label">本周完成率</div>
            <span style="font-size:17px; font-weight:600; color: var(--cal-primary);">53%</span>
          </div>
          <div style="margin-top:6px; height:6px; background: var(--cal-muted); border-radius:9999px; overflow:hidden;">
            <div style="height:100%; width:53%; background: var(--cal-primary); border-radius:9999px;"></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 渲染周导航
function renderWeekNavigation() {
  return `
    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:var(--cal-card);">
      <div style="display:flex; align-items:center; gap:6px;">
        <button class="btn btn-sm btn-ghost" style="gap:4px;">
          <i data-lucide="chevron-left" style="width:16px; height:16px;"></i>
          <span>上一周</span>
        </button>
        <button class="btn btn-sm" style="background:var(--state-info-muted); color:var(--cal-primary); gap:6px;">
          <i data-lucide="locate-fixed" style="width:14px; height:14px;"></i>
          <span>本周</span>
        </button>
        <button class="btn btn-sm btn-ghost" style="gap:4px;">
          <span>下一周</span>
          <i data-lucide="chevron-right" style="width:16px; height:16px;"></i>
        </button>
      </div>
      
      <div style="display:flex; align-items:center; gap:8px;">
        <i data-lucide="calendar-range" style="width:16px; height:16px; color:var(--cal-muted-foreground);"></i>
        <span style="font-size:13px; font-weight:500;">2026年7月27日 - 8月2日</span>
        <span class="badge badge-info">第31周</span>
      </div>
      
      <div style="display:flex; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-medium); padding:2px;">
        <a href="#month-view" class="btn btn-sm btn-ghost" style="gap:6px;">
          <i data-lucide="calendar" style="width:14px; height:14px;"></i>
          <span>月视图</span>
        </a>
        <button class="btn btn-sm btn-primary" style="gap:6px;">
          <i data-lucide="calendar-days" style="width:14px; height:14px;"></i>
          <span>周视图</span>
        </button>
      </div>
    </div>
  `;
}

// 渲染拖拽提示
function renderDragHint() {
  return `
    <div style="display:flex; align-items:center; gap:8px; padding:8px 12px; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-medium); background:var(--cal-card);">
      <i data-lucide="info" style="width:16px; height:16px; color:var(--cal-primary); flex-shrink:0;"></i>
      <span style="font-size:11px; color:var(--cal-muted-foreground);">
        <span style="font-weight:500; color:var(--cal-foreground);">拖拽待办卡片</span>可跨日期移动 — 拖至更早日期标记为「提前完成」，拖至更晚日期标记为「延期」
      </span>
    </div>
  `;
}

// 渲染周网格
function renderWeekGrid() {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const today = new Date();
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - today.getDay() + 1); // 本周一
  
  const weekTodos = {
    '2026-07-27': [
      { id: 101, time: '09:00', title: '采购部周例会', priority: 'completed', source: 'manual' },
      { id: 102, time: '14:00', title: '核对上周钢材入库数据', priority: 'completed', source: 'feishu' },
      { id: 103, time: '16:00', title: '提交月度采购预算', priority: 'normal', source: 'email' }
    ],
    '2026-07-28': [
      { id: 104, time: '10:00', title: '供应商电话沟通铝锭报价', priority: 'completed', source: 'feishu' },
      { id: 105, time: '15:00', title: '整理Q2成本分析归档', priority: 'normal', source: 'manual' }
    ],
    '2026-07-29': [
      { id: 106, time: '09:30', title: '铜材到货验收', priority: 'completed', source: 'feishu' },
      { id: 107, time: '14:00', title: '物流供应商季度评估', priority: 'secondary', source: 'email' },
      { id: 108, time: '16:30', title: '更新采购台账', priority: 'normal', source: 'manual' }
    ],
    '2026-07-30': [
      { id: 109, time: '10:00', title: '钢材期货锁价决策会', priority: 'urgent', source: 'feishu' },
      { id: 110, time: '15:00', title: '供应商付款审核', priority: 'completed', source: 'email' }
    ],
    '2026-07-31': [
      { id: 111, time: '09:00', title: '每日采购晨会纪要', priority: 'completed', source: 'feishu' },
      { id: 1, time: '14:00', title: '核对Q3钢材采购报价单', priority: 'urgent', source: 'feishu' },
      { id: 112, time: '15:30', title: '供应商月度评估电话会议', priority: 'normal', source: 'email' },
      { id: 2, time: '16:30', title: '提交供应商付款审批流程', priority: 'urgent', source: 'email' }
    ],
    '2026-08-01': [
      { id: 3, time: '10:00', title: '整理铝锭月度成本分析报告', priority: 'secondary', source: 'feishu' }
    ],
    '2026-08-02': [
      { id: 113, time: '14:00', title: '跟进物流旺季运费谈判准备', priority: 'normal', source: 'wechat' }
    ]
  };
  
  return `
    <div class="week-grid" style="flex:1; overflow:hidden;">
      ${days.map((day, index) => {
        const date = new Date(weekStart);
        date.setDate(weekStart.getDate() + index);
        const dateStr = date.toISOString().split('T')[0];
        const isToday = dateStr === today.toISOString().split('T')[0];
        const isWeekend = index >= 5;
        const dayTodos = weekTodos[dateStr] || [];
        
        return `
          <div class="week-day-column" data-day="${dateStr}" data-day-index="${index + 1}">
            <div class="week-day-header ${isToday ? 'today' : ''} ${isWeekend ? 'weekend' : ''}">
              <div class="week-day-name">${day}</div>
              <div class="week-day-number">${date.getDate()}</div>
            </div>
            
            <div style="display:none; align-items:center; justify-content:center; gap:6px; padding:8px; font-size:11px; font-weight:500; color:var(--cal-primary);" class="drop-hint">
              <i data-lucide="move" style="width:14px; height:14px;"></i>
              <span class="drop-hint-text">释放放置</span>
            </div>
            
            <div class="week-day-content no-scrollbar">
              ${dayTodos.map(todo => renderWeekTodoCard(todo, dateStr)).join('')}
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

// 渲染周待办卡片
function renderWeekTodoCard(todo, date) {
  const isCompleted = todo.priority === 'completed';
  const borderColor = getPriorityColor(todo.priority);
  const sourceIcon = getSourceIcon(todo.source);
  
  return `
    <div class="week-todo-card ${isCompleted ? 'completed' : ''}" 
         draggable="true" 
         data-card-id="${todo.id}" 
         data-original-day="${date}"
         style="--card-border-color: ${borderColor};">
      <span style="position:absolute; left:0; top:0; height:100%; width:3px; background:${borderColor};"></span>
      
      <div style="font-size:11px; font-weight:600; color:${isCompleted ? 'var(--cal-muted-foreground)' : 'var(--cal-primary)'};">${todo.time}</div>
      
      <p style="margin-top:4px; font-size:11px; font-weight:600; ${isCompleted ? 'text-decoration:line-through;' : ''} color:${isCompleted ? 'var(--cal-muted-foreground)' : 'var(--cal-foreground)'}; line-height:1.4;" class="line-clamp-2">
        ${todo.title}
      </p>
      
      <div style="margin-top:8px; display:flex; align-items:center; justify-content:space-between;">
        <span style="display:flex; align-items:center; gap:4px; font-size:11px; color:var(--cal-muted-foreground);">
          <i data-lucide="${sourceIcon}" style="width:12px; height:12px;"></i>
          <span>${todo.source === 'feishu' ? '飞书' : (todo.source === 'email' ? '邮件' : (todo.source === 'wechat' ? '微信' : '手动'))}</span>
        </span>
        ${isCompleted ? 
          '<i data-lucide="check" style="width:14px; height:14px; color:var(--state-success);"></i>' : 
          `<span style="width:6px; height:6px; border-radius:50%; background:${borderColor};"></span>`
        }
      </div>
    </div>
  `;
}

// 渲染周总结
function renderWeekSummary() {
  return `
    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:var(--cal-card);">
      <div style="display:flex; align-items:center; gap:8px; font-size:11px; color:var(--cal-muted-foreground);">
        <i data-lucide="calendar-clock" style="width:16px; height:16px; color:var(--cal-primary);"></i>
        <span>本周共 <span style="font-weight:600; color:var(--cal-foreground);">15</span> 项待办，已完成 <span style="font-weight:600; color:var(--state-success);">8</span> 项，逾期 <span style="font-weight:600; color:var(--state-error);">2</span> 项</span>
      </div>
      
      <a href="#smart-import" class="btn btn-sm" style="background:var(--state-info-muted); color:var(--cal-primary); gap:6px;">
        <i data-lucide="sparkles" style="width:14px; height:14px;"></i>
        <span>快速跳转智能导入</span>
      </a>
    </div>
  `;
}

// 初始化拖拽功能
function initDragAndDrop() {
  let draggedCard = null;
  let draggedOriginalDay = null;
  let draggedCardId = null;
  
  // 拖拽开始
  document.addEventListener('dragstart', (e) => {
    const card = e.target.closest('.week-todo-card');
    if (!card) return;
    
    draggedCard = card;
    draggedOriginalDay = card.dataset.originalDay;
    draggedCardId = card.dataset.cardId;
    
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', draggedCardId);
  });
  
  // 拖拽结束
  document.addEventListener('dragend', (e) => {
    const card = e.target.closest('.week-todo-card');
    if (card) card.classList.remove('dragging');
    
    document.querySelectorAll('.week-day-column').forEach(col => {
      col.classList.remove('drop-target', 'drop-earlier', 'drop-later');
    });
    
    const hints = document.querySelectorAll('.drop-hint-text');
    hints.forEach(hint => hint.textContent = '释放放置');
    
    draggedCard = null;
    draggedOriginalDay = null;
    draggedCardId = null;
  });
  
  // 拖拽经过
  document.querySelectorAll('.week-day-column').forEach(col => {
    col.addEventListener('dragover', (e) => {
      if (!draggedCard) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      
      col.classList.remove('drop-target', 'drop-earlier', 'drop-later');
      const targetDay = col.dataset.day;
      const hint = col.querySelector('.drop-hint-text');
      
      if (targetDay < draggedOriginalDay) {
        col.classList.add('drop-earlier');
        if (hint) hint.textContent = '提前完成';
      } else if (targetDay > draggedOriginalDay) {
        col.classList.add('drop-later');
        if (hint) hint.textContent = '延期';
      } else {
        col.classList.add('drop-target');
        if (hint) hint.textContent = '释放放置';
      }
    });
    
    col.addEventListener('dragleave', (e) => {
      if (e.target === col || !col.contains(e.relatedTarget)) {
        col.classList.remove('drop-target', 'drop-earlier', 'drop-later');
      }
    });
    
    col.addEventListener('drop', (e) => {
      e.preventDefault();
      if (!draggedCard) return;
      
      const targetDay = col.dataset.day;
      col.classList.remove('drop-target', 'drop-earlier', 'drop-later');
      
      const cardContainer = col.querySelector('.week-day-content');
      if (cardContainer && draggedCard.parentElement !== cardContainer) {
        cardContainer.appendChild(draggedCard);
        draggedCard.dataset.originalDay = targetDay;
        
        // 显示提示
        const msg = targetDay < draggedOriginalDay ? '已标记为「提前完成」' : '已标记为「延期」';
        showToast(msg, targetDay < draggedOriginalDay ? 'success' : 'warning');
      }
    });
  });
}

// 显示提示
function showToast(msg, type) {
  const existing = document.getElementById('drag-toast');
  if (existing) existing.remove();
  
  const toast = document.createElement('div');
  toast.id = 'drag-toast';
  toast.style.cssText = `
    position: fixed;
    bottom: 80px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: opacity 0.3s;
    opacity: 0;
    background: ${type === 'success' ? 'var(--state-success)' : 'var(--state-warning)'};
    color: ${type === 'success' ? '#ffffff' : '#1a1200'};
  `;
  toast.innerHTML = `<span>${msg}</span>`;
  document.body.appendChild(toast);
  
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
  });
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}