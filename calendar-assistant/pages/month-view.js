/**
 * 工作台·月视图页面
 */

function renderMonthView() {
  renderHeader('工作台', '2026年7月31日 · 周五');
  
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:16px; height:100%;">
      ${renderStats()}
      
      <div style="display:flex; gap:16px; flex:1; min-height:0;">
        <!-- 左侧日历面板 -->
        <section style="width:320px; flex-shrink:0; display:flex; flex-direction:column; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:var(--cal-card);">
          ${renderCalendar()}
          ${renderTodaySchedule()}
        </section>
        
        <!-- 右侧待办列表 -->
        <section style="flex:1; display:flex; flex-direction:column; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-large); background:var(--cal-card);">
          ${renderTodoList()}
        </section>
      </div>
    </div>
  `;
  
  // 绑定事件
  bindCalendarEvents();
  bindTodoEvents();
}

// 渲染日历
function renderCalendar() {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startWeekday = (firstDay.getDay() + 6) % 7; // 周一为第一天
  
  let days = '';
  
  // 填充月初空白
  for (let i = 0; i < startWeekday; i++) {
    days += '<div></div>';
  }
  
  // 渲染当月日期
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const isToday = day === today.getDate();
    const dayTodos = AppState.todos.filter(t => t.date === dateStr);
    
    let indicators = '';
    if (dayTodos.length > 0) {
      indicators = '<div class="calendar-day-indicator">';
      dayTodos.slice(0, 3).forEach(todo => {
        const color = todo.completed ? 'var(--state-success)' : getPriorityColor(todo.priority);
        indicators += `<span style="background:${color};"></span>`;
      });
      indicators += '</div>';
    }
    
    days += `
      <div class="calendar-day ${isToday ? 'today' : ''}" data-date="${dateStr}">
        <span>${day}</span>
        ${indicators}
      </div>
    `;
  }
  
  // 渲染下月初日期
  const remainingDays = 42 - (startWeekday + lastDay.getDate());
  for (let i = 1; i <= Math.min(remainingDays, 7); i++) {
    days += `<div class="calendar-day other-month"><span>${i}</span></div>`;
  }
  
  return `
    <div style="padding:12px 16px; border-bottom:1px solid var(--cal-border-subtle);">
      <div style="display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:4px;">
          <button class="btn btn-ghost btn-sm btn-icon" aria-label="上个月">
            <i data-lucide="chevron-left" style="width:16px;height:16px;"></i>
          </button>
          <span class="cal-h4" style="padding:0 4px;">${year}年${month + 1}月</span>
          <button class="btn btn-ghost btn-sm btn-icon" aria-label="下个月">
            <i data-lucide="chevron-right" style="width:16px;height:16px;"></i>
          </button>
        </div>
        <button class="btn btn-sm btn-ghost">
          <i data-lucide="locate-fixed" style="width:14px;height:14px;"></i>
          <span>今天</span>
        </button>
      </div>
    </div>
    
    <div style="padding:12px;">
      <div class="calendar-grid">
        <div class="calendar-day-header">一</div>
        <div class="calendar-day-header">二</div>
        <div class="calendar-day-header">三</div>
        <div class="calendar-day-header">四</div>
        <div class="calendar-day-header">五</div>
        <div class="calendar-day-header">六</div>
        <div class="calendar-day-header">日</div>
        ${days}
      </div>
      
      <div style="margin-top:12px; display:flex; justify-content:center; gap:12px; font-size:11px; color:var(--cal-muted-foreground);">
        <span style="display:flex; align-items:center; gap:4px;">
          <span style="width:6px; height:6px; border-radius:50%; background:var(--state-error);"></span>紧急
        </span>
        <span style="display:flex; align-items:center; gap:4px;">
          <span style="width:6px; height:6px; border-radius:50%; background:var(--state-warning);"></span>次要
        </span>
        <span style="display:flex; align-items:center; gap:4px;">
          <span style="width:6px; height:6px; border-radius:50%; background:var(--state-info);"></span>正常
        </span>
        <span style="display:flex; align-items:center; gap:4px;">
          <span style="width:6px; height:6px; border-radius:50%; background:var(--state-success);"></span>已完成
        </span>
      </div>
    </div>
  `;
}

// 渲染今日日程
function renderTodaySchedule() {
  const today = new Date().toISOString().split('T')[0];
  const todayTodos = AppState.todos.filter(t => t.date === today);
  
  return `
    <div style="border-top:1px solid var(--cal-border-subtle);"></div>
    
    <div style="padding:12px 16px 6px; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:8px;">
        <i data-lucide="calendar-clock" style="width:16px; height:16px; color:var(--cal-primary);"></i>
        <span class="cal-h4">今日日程</span>
      </div>
      <span class="cal-body-xs" style="color:var(--cal-muted-foreground);">${todayTodos.length} 项</span>
    </div>
    
    <div class="no-scrollbar" style="flex:1; overflow-y:auto; padding:4px 16px 16px;">
      ${todayTodos.length > 0 ? todayTodos.map(todo => `
        <div style="display:flex; align-items:center; gap:10px; padding:8px 12px; margin-bottom:6px; background:var(--cal-muted); border-radius:var(--cal-radius-medium);">
          <span style="width:8px; height:8px; border-radius:50%; background:${getPriorityColor(todo.priority)}; flex-shrink:0;"></span>
          <span class="cal-body-xs" style="font-weight:500; color:${todo.completed ? 'var(--cal-muted-foreground)' : 'var(--cal-primary)'}; white-space:nowrap;">
            ${todo.time || '全天'}
          </span>
          <span class="cal-body-xs" style="${todo.completed ? 'text-decoration:line-through;' : ''} color:var(--cal-foreground); overflow:hidden; text-overflow:ellipsis;">
            ${todo.title}
          </span>
        </div>
      `).join('') : `
        <div style="padding:20px; text-align:center; color:var(--cal-muted-foreground); font-size:13px;">
          今日暂无待办
        </div>
      `}
    </div>
  `;
}

// 渲染待办列表
function renderTodoList() {
  const todos = AppState.todos;
  
  return `
    <div style="padding:12px 20px; border-bottom:1px solid var(--cal-border-subtle);">
      <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
        <div style="display:flex; align-items:center; gap:6px;">
          <button class="btn btn-sm btn-ghost">全部 <span style="color:var(--cal-muted-foreground);margin-left:4px;">20</span></button>
          <button class="btn btn-sm btn-primary">今日 <span style="display:inline-flex; height:16px; min-width:16px; align-items:center; justify-content:center; background:rgba(255,255,255,0.22); border-radius:9999px; padding:0 4px; font-size:10px; font-weight:600;">8</span></button>
          <button class="btn btn-sm btn-ghost">本周 <span style="color:var(--cal-muted-foreground);margin-left:4px;">15</span></button>
          <button class="btn btn-sm btn-ghost">逾期 <span style="color:var(--state-error);margin-left:4px;">2</span></button>
        </div>
        
        <div style="display:flex; align-items:center; gap:8px;">
          <a href="#week-view" class="btn btn-sm" style="background:var(--state-info-muted); color:var(--cal-primary); gap:6px;">
            <i data-lucide="sparkles" style="width:14px;height:14px;"></i>
            <span>周视图</span>
          </a>
          
          <button class="btn btn-sm btn-outline" style="gap:6px;">
            <i data-lucide="arrow-down-up" style="width:14px;height:14px;"></i>
            <span>截止时间</span>
          </button>
          
          <div style="display:flex; border:1px solid var(--cal-border-subtle); border-radius:var(--cal-radius-medium); padding:2px;">
            <button class="btn btn-sm btn-icon" style="background:var(--cal-muted); color:var(--cal-foreground);">
              <i data-lucide="list" style="width:16px;height:16px;"></i>
            </button>
            <button class="btn btn-sm btn-icon" style="color:var(--cal-muted-foreground);">
              <i data-lucide="calendar" style="width:16px;height:16px;"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="no-scrollbar" style="flex:1; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:8px;">
      ${todos.map(todo => renderTodoItem(todo)).join('')}
    </div>
  `;
}

// 渲染单个待办项
function renderTodoItem(todo) {
  const borderColor = todo.completed ? 'var(--state-success)' : getPriorityColor(todo.priority);
  const sourceIcon = getSourceIcon(todo.source);
  
  return `
    <div class="todo-item ${todo.completed ? 'completed' : ''}" 
         style="border-left-color:${borderColor};" 
         data-todo-id="${todo.id}">
      <button class="todo-checkbox ${todo.completed ? 'checked' : ''}" aria-label="标记完成">
        ${todo.completed ? '<i data-lucide="check" style="width:12px;height:12px;color:var(--state-success-foreground);"></i>' : ''}
      </button>
      
      <div class="todo-content">
        <p class="todo-title">${todo.title}</p>
        <div class="todo-meta">
          ${todo.tags.map(tag => `<span class="tag"><i data-lucide="hash" style="width:12px;height:12px;"></i>${tag}</span>`).join('')}
          <span style="display:flex; align-items:center; gap:4px; font-size:11px; color:var(--cal-muted-foreground); white-space:nowrap;">
            <i data-lucide="clock" style="width:12px;height:12px;"></i>
            ${formatDate(todo.date)} ${todo.time || ''}
          </span>
        </div>
      </div>
      
      <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px; padding-left:8px;">
        <span class="badge ${todo.completed ? 'badge-success' : (todo.priority === 'urgent' ? 'badge-error' : (todo.priority === 'secondary' ? 'badge-warning' : 'badge-info'))}">
          <span style="width:6px; height:6px; border-radius:50%; background:currentColor;"></span>
          ${todo.completed ? '已完成' : (todo.priority === 'urgent' ? '紧急' : (todo.priority === 'secondary' ? '次要' : '正常'))}
        </span>
        <span style="display:flex; align-items:center; gap:4px; font-size:11px; color:var(--cal-muted-foreground);">
          <i data-lucide="${sourceIcon}" style="width:12px;height:12px;"></i>
          ${todo.source === 'feishu' ? '飞书' : (todo.source === 'email' ? '邮件' : (todo.source === 'wechat' ? '微信' : '手动'))}
        </span>
      </div>
    </div>
  `;
}

// 绑定日历事件
function bindCalendarEvents() {
  // 点击日期切换待办列表
}

// 绑定待办事件
function bindTodoEvents() {
  // 点击复选框切换完成状态
  document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
    checkbox.addEventListener('click', (e) => {
      const todoItem = e.target.closest('.todo-item');
      const todoId = parseInt(todoItem.dataset.todoId);
      const todo = AppState.todos.find(t => t.id === todoId);
      
      if (todo) {
        todo.completed = !todo.completed;
        todo.priority = 'completed';
        
        // 重新渲染
        renderMonthView();
      }
    });
  });
}