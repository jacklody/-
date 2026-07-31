/**
 * 日历助手 - 主应用入口
 * 智能待办管理系统
 */

// 应用状态
const AppState = {
  currentPage: 'month-view',
  theme: localStorage.getItem('theme') || 'light',
  sidebarOpen: false,
  currentDate: new Date(),
  
  // 待办数据
  todos: [
    {
      id: 1,
      title: '核对Q3钢材采购报价单',
      priority: 'urgent',
      source: 'feishu',
      date: '2026-07-31',
      time: '14:00',
      tags: ['钢材采购', '报价核对'],
      completed: false
    },
    {
      id: 2,
      title: '提交供应商付款审批流程',
      priority: 'urgent',
      source: 'email',
      date: '2026-07-31',
      time: '16:30',
      tags: ['付款审批'],
      completed: false
    },
    {
      id: 3,
      title: '整理铝锭月度成本分析报告',
      priority: 'secondary',
      source: 'feishu',
      date: '2026-08-01',
      time: '10:00',
      tags: ['成本分析', '铝锭'],
      completed: false
    },
    {
      id: 4,
      title: '跟进物流旺季运费谈判',
      priority: 'normal',
      source: 'wechat',
      date: '2026-08-02',
      time: '14:00',
      tags: ['物流', '运费谈判'],
      completed: false
    },
    {
      id: 5,
      title: '更新供应商评估评分表',
      priority: 'normal',
      source: 'manual',
      date: '2026-08-03',
      time: null,
      tags: ['供应商'],
      completed: false
    },
    {
      id: 6,
      title: '确认铜材到货验收单',
      priority: 'normal',
      source: 'feishu',
      date: '2026-07-29',
      time: '09:30',
      tags: ['到货验收'],
      completed: true
    },
    {
      id: 7,
      title: '准备月度采购成本汇报PPT',
      priority: 'normal',
      source: 'manual',
      date: '2026-08-05',
      time: null,
      tags: ['成本汇报', 'PPT'],
      completed: false
    }
  ]
};

// 路由配置
const routes = {
  'month-view': renderMonthView,
  'week-view': renderWeekView,
  'reminder': renderReminder,
  'smart-import': renderSmartImport,
  'integration': renderIntegration
};

// 初始化应用
function initApp() {
  // 应用主题
  document.documentElement.setAttribute('data-theme', AppState.theme);
  
  // 渲染布局
  renderLayout();
  
  // 初始化路由
  handleRoute();
  
  // 初始化图标
  lucide.createIcons();
  
  // 监听路由变化
  window.addEventListener('hashchange', handleRoute);
}

// 渲染布局
function renderLayout() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="app-layout">
      <!-- 侧边栏 -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <i data-lucide="calendar-check"></i>
          </div>
          <span class="cal-h3">日历助手</span>
        </div>
        
        <nav class="sidebar-nav" role="navigation" aria-label="主导航">
          <a href="#month-view" class="nav-item" data-page="month-view" data-active="false">
            <i data-lucide="layout-dashboard"></i>
            <span>工作台</span>
          </a>
          <a href="#smart-import" class="nav-item" data-page="smart-import" data-active="false">
            <i data-lucide="download"></i>
            <span>智能导入</span>
          </a>
          <a href="#reminder" class="nav-item" data-page="reminder" data-active="false">
            <i data-lucide="bell"></i>
            <span>提醒中心</span>
          </a>
          <a href="#integration" class="nav-item" data-page="integration" data-active="false">
            <i data-lucide="plug"></i>
            <span>集成设置</span>
          </a>
        </nav>
        
        <div class="sidebar-footer">
          <div class="user-avatar">马</div>
          <div class="user-info">
            <div class="user-name">马工</div>
            <div class="user-role">采购成本分析</div>
          </div>
          <button class="settings-btn" aria-label="设置" id="settingsBtn">
            <i data-lucide="settings"></i>
          </button>
        </div>
      </aside>
      
      <!-- 主内容区 -->
      <div class="main-wrapper">
        <header class="top-header" id="topHeader">
          <!-- 动态内容由各页面填充 -->
        </header>
        <main id="mainContent" style="flex:1; overflow-y: auto; padding: 24px;">
          <!-- 页面内容 -->
        </main>
      </div>
    </div>
  `;
  
  // 设置按钮事件
  document.getElementById('settingsBtn').addEventListener('click', toggleTheme);
}

// 处理路由
function handleRoute() {
  const hash = window.location.hash.slice(1) || 'month-view';
  const page = routes[hash] ? hash : 'month-view';
  
  AppState.currentPage = page;
  
  // 更新导航激活状态
  document.querySelectorAll('.nav-item').forEach(item => {
    const isActive = item.dataset.page === page || 
                     (page === 'week-view' && item.dataset.page === 'month-view');
    item.dataset.active = isActive;
  });
  
  // 渲染页面
  routes[page]();
  
  // 重新初始化图标
  lucide.createIcons();
}

// 渲染通用头部
function renderHeader(title, dateText) {
  const header = document.getElementById('topHeader');
  header.innerHTML = `
    <div class="header-left">
      <h2 class="cal-h2">${title}</h2>
      ${dateText ? `<span class="badge badge-info">
        <i data-lucide="calendar-days" style="width:12px;height:12px;"></i>
        ${dateText}
      </span>` : ''}
    </div>
    <div class="header-actions">
      <div class="search-wrapper">
        <i data-lucide="search" class="search-icon" style="width:16px;height:16px;"></i>
        <input type="text" class="search-input" placeholder="搜索待办..." aria-label="搜索待办">
      </div>
      <button class="btn btn-primary">
        <i data-lucide="plus" style="width:16px;height:16px;"></i>
        <span>新建待办</span>
      </button>
      <button class="btn btn-ghost">
        <i data-lucide="download" style="width:16px;height:16px;"></i>
        <span>导出</span>
      </button>
      <button class="btn btn-ghost">
        <i data-lucide="upload" style="width:16px;height:16px;"></i>
        <span>导入</span>
      </button>
    </div>
  `;
}

// 切换主题
function toggleTheme() {
  AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', AppState.theme);
  localStorage.setItem('theme', AppState.theme);
}

// 获取优先级颜色
function getPriorityColor(priority) {
  const colors = {
    urgent: 'var(--state-error)',
    secondary: 'var(--state-warning)',
    normal: 'var(--state-info)',
    completed: 'var(--state-success)'
  };
  return colors[priority] || colors.normal;
}

// 获取来源图标
function getSourceIcon(source) {
  const icons = {
    feishu: 'message-square',
    email: 'mail',
    wechat: 'message-circle',
    manual: 'hand'
  };
  return icons[source] || 'circle';
}

// 格式化日期
function formatDate(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  if (date.toDateString() === today.toDateString()) {
    return '今天';
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return '明天';
  } else {
    return `${date.getMonth() + 1}月${date.getDate()}日`;
  }
}

// 渲染统计卡片
function renderStats() {
  const today = new Date().toISOString().split('T')[0];
  const todayTodos = AppState.todos.filter(t => t.date === today && !t.completed);
  const urgentCount = todayTodos.filter(t => t.priority === 'urgent').length;
  const completedCount = AppState.todos.filter(t => t.completed).length;
  const overdueCount = AppState.todos.filter(t => t.date < today && !t.completed).length;
  
  return `
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--state-info-muted); color: var(--state-info);">
          <i data-lucide="list-todo"></i>
        </div>
        <div>
          <div class="stat-label">今日待办</div>
          <div class="stat-value">${todayTodos.length}</div>
          <span style="font-size:11px; color: var(--state-error); font-weight:500;">${urgentCount} 紧急</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--state-success-muted); color: var(--state-success);">
          <i data-lucide="check-circle-2"></i>
        </div>
        <div>
          <div class="stat-label">已完成</div>
          <div class="stat-value">${completedCount}</div>
          <span style="font-size:11px; color: var(--cal-muted-foreground);">本周</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--state-error-muted); color: var(--state-error);">
          <i data-lucide="alarm-clock"></i>
        </div>
        <div>
          <div class="stat-label">逾期</div>
          <div class="stat-value" style="color: var(--state-error);">${overdueCount}</div>
          <span style="font-size:11px; color: var(--state-error);">需立即处理</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--state-info-muted); color: var(--cal-primary);">
          <i data-lucide="trending-up"></i>
        </div>
        <div style="flex:1;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="stat-label">本周完成率</div>
            <span style="font-size:22px; font-weight:600; color: var(--cal-primary);">76%</span>
          </div>
          <div style="margin-top:8px; height:6px; background: var(--cal-muted); border-radius:9999px; overflow:hidden;">
            <div style="height:100%; width:76%; background: var(--cal-primary); border-radius:9999px;"></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 页面路由将在后续文件中实现
// 导出供其他模块使用
window.AppState = AppState;
window.renderHeader = renderHeader;
window.renderStats = renderStats;
window.getPriorityColor = getPriorityColor;
window.getSourceIcon = getSourceIcon;
window.formatDate = formatDate;
window.lucide = lucide;

// 启动应用
document.addEventListener('DOMContentLoaded', initApp);