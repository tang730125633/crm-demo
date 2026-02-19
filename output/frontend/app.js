// ======================================================
// CRM Demo - Shared Utilities (app.js)
// ======================================================

// 自动判断：Railway 上前后端同源，本地开发时用 localhost:8000
const API_BASE_URL = (window.location.port === '8080' || window.location.hostname === 'localhost' && window.location.port === '8080')
  ? 'http://localhost:8000'
  : '';

// ------ Status Config ------
const STATUS_CONFIG = {
  '潜在客户': {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    border: 'border-gray-300',
    dot: 'bg-gray-400',
    bar: '#9CA3AF',
  },
  '意向客户': {
    bg: 'bg-blue-100',
    text: 'text-blue-700',
    border: 'border-blue-300',
    dot: 'bg-blue-500',
    bar: '#3B82F6',
  },
  '成交客户': {
    bg: 'bg-green-100',
    text: 'text-green-700',
    border: 'border-green-300',
    dot: 'bg-green-500',
    bar: '#22C55E',
  },
  '流失客户': {
    bg: 'bg-red-100',
    text: 'text-red-700',
    border: 'border-red-300',
    dot: 'bg-red-400',
    bar: '#EF4444',
  },
};

const FOLLOW_TYPE_CONFIG = {
  '电话': { icon: '📞', color: 'text-blue-600', bg: 'bg-blue-50' },
  '微信': { icon: '💬', color: 'text-green-600', bg: 'bg-green-50' },
  '拜访': { icon: '🤝', color: 'text-purple-600', bg: 'bg-purple-50' },
  '邮件': { icon: '📧', color: 'text-orange-600', bg: 'bg-orange-50' },
};

// ------ API Fetch Wrapper ------
async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }
  const res = await fetch(url, config);
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      msg = err.detail || JSON.stringify(err) || msg;
    } catch (_) {}
    throw new Error(msg);
  }
  // 204 No Content
  if (res.status === 204) return null;
  return res.json();
}

// ------ Date Formatting ------
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// ------ Status Badge HTML ------
function statusBadge(status) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG['潜在客户'];
  return `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.text} border ${cfg.border}">
    <span class="w-1.5 h-1.5 rounded-full ${cfg.dot}"></span>
    ${status || '未知'}
  </span>`;
}

// ------ Toast Notification ------
function showToast(message, type = 'success') {
  const existing = document.getElementById('crm-toast');
  if (existing) existing.remove();

  const colors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-blue-600',
  };

  const toast = document.createElement('div');
  toast.id = 'crm-toast';
  toast.className = `fixed bottom-6 right-6 z-[9999] px-5 py-3 rounded-xl shadow-xl text-white text-sm font-medium flex items-center gap-2 transition-all duration-300 ${colors[type] || colors.info}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'i'}</span>
    <span>${message}</span>
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

// ------ Loading State Helpers ------
function setLoading(el, loading, text = '加载中...') {
  if (!el) return;
  if (loading) {
    el._originalHTML = el.innerHTML;
    el.disabled = true;
    el.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>${text}`;
  } else {
    el.disabled = false;
    el.innerHTML = el._originalHTML || text;
  }
}

// ------ Highlight Active Nav Link ------
function highlightNav() {
  const current = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('[data-nav]').forEach(link => {
    const href = link.getAttribute('href') || '';
    const page = href.split('/').pop();
    if (page === current || (current === '' && page === 'index.html')) {
      link.classList.add('bg-blue-700', 'text-white');
      link.classList.remove('text-blue-100', 'hover:bg-blue-700/60');
    }
  });
}

document.addEventListener('DOMContentLoaded', highlightNav);
