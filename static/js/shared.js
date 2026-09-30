/* shared.js — common utilities used across all pages */

// ── Toast notifications ──────────────────────────────────────────────────────
(function () {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.style.cssText = [
    'position:fixed', 'bottom:1.5rem', 'right:1.5rem', 'z-index:9999',
    'display:flex', 'flex-direction:column', 'gap:0.6rem', 'pointer-events:none'
  ].join(';');
  document.body.appendChild(container);

  window.showToast = function (msg, type, duration) {
    type = type || 'info';
    duration = duration || 3500;
    const colors = {
      info:    { bg:'rgba(56,189,248,0.15)',  border:'rgba(56,189,248,0.4)',  icon:'fa-info-circle',        color:'#7dd3fc' },
      success: { bg:'rgba(52,211,153,0.15)',  border:'rgba(52,211,153,0.4)',  icon:'fa-check-circle',       color:'#6ee7b7' },
      error:   { bg:'rgba(248,113,113,0.15)', border:'rgba(248,113,113,0.4)', icon:'fa-exclamation-circle', color:'#fca5a5' },
      warning: { bg:'rgba(251,191,36,0.15)',  border:'rgba(251,191,36,0.4)',  icon:'fa-exclamation-triangle',color:'#fde68a'},
    };
    const c = colors[type] || colors.info;
    const toast = document.createElement('div');
    toast.style.cssText = [
      'background:' + c.bg,
      'border:1px solid ' + c.border,
      'color:' + c.color,
      'padding:0.75rem 1.1rem',
      'border-radius:10px',
      'backdrop-filter:blur(20px)',
      'font-size:0.88rem',
      'display:flex',
      'align-items:center',
      'gap:0.6rem',
      'pointer-events:all',
      'max-width:320px',
      'animation:toastIn 0.3s ease',
      'box-shadow:0 4px 20px rgba(0,0,0,0.3)'
    ].join(';');
    toast.innerHTML = '<i class="fas ' + c.icon + '"></i><span>' + msg + '</span>';
    container.appendChild(toast);
    setTimeout(function () {
      toast.style.animation = 'toastOut 0.3s ease forwards';
      setTimeout(function () { toast.remove(); }, 300);
    }, duration);
  };

  const style = document.createElement('style');
  style.textContent = [
    '@keyframes toastIn  { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }',
    '@keyframes toastOut { from{opacity:1;transform:translateX(0)} to{opacity:0;transform:translateX(20px)} }'
  ].join('');
  document.head.appendChild(style);
})();

// ── Demo badge injection ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/demo-status')
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (!d.demo_mode) return;
      var existing = document.querySelector('.demo-badge');
      if (!existing) {
        var nav = document.querySelector('.navbar');
        if (nav) {
          var badge = document.createElement('span');
          badge.className = 'demo-badge';
          badge.textContent = 'Demo Mode';
          nav.appendChild(badge);
        }
      }
    })
    .catch(function () {});
});

// ── Mobile hamburger menu ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  var navLinks = document.querySelector('.nav-links');
  if (!navLinks) return;

  // Create hamburger button
  var burger = document.createElement('button');
  burger.id = 'nav-burger';
  burger.innerHTML = '<i class="fas fa-bars"></i>';
  burger.style.cssText = [
    'display:none', 'background:none', 'border:1px solid var(--glass-border)',
    'color:var(--text-primary)', 'padding:0.4rem 0.7rem', 'border-radius:8px',
    'cursor:pointer', 'font-size:1rem'
  ].join(';');

  var navbar = document.querySelector('.navbar');
  if (navbar) navbar.appendChild(burger);

  // Mobile styles
  var mobileStyle = document.createElement('style');
  mobileStyle.textContent = [
    '@media(max-width:768px){',
    '#nav-burger{display:block!important}',
    '.nav-links{',
      'display:none;flex-direction:column;position:absolute;',
      'top:64px;left:0;right:0;z-index:200;',
      'background:rgba(10,10,26,0.97);backdrop-filter:blur(20px);',
      'border-bottom:1px solid var(--glass-border);',
      'padding:1rem 1.5rem;gap:0.75rem;',
    '}',
    '.nav-links.open{display:flex!important}',
    '.nav-links a{padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.05)}',
    '}'
  ].join('');
  document.head.appendChild(mobileStyle);

  burger.addEventListener('click', function () {
    navLinks.classList.toggle('open');
    burger.innerHTML = navLinks.classList.contains('open')
      ? '<i class="fas fa-times"></i>'
      : '<i class="fas fa-bars"></i>';
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!navbar.contains(e.target)) {
      navLinks.classList.remove('open');
      burger.innerHTML = '<i class="fas fa-bars"></i>';
    }
  });
});

// ── Smooth page transitions ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.3s ease';
  requestAnimationFrame(function () { document.body.style.opacity = '1'; });

  document.querySelectorAll('a[href]').forEach(function (link) {
    var href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('javascript')) return;
    link.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      var target = href;
      document.body.style.opacity = '0';
      setTimeout(function () { window.location.href = target; }, 280);
    });
  });
});

// ── Animated score counters ──────────────────────────────────────────────────
window.animateCounter = function (el, target, duration, suffix) {
  suffix = suffix || '';
  var start = 0;
  var step = target / (duration / 16);
  var timer = setInterval(function () {
    start = Math.min(start + step, target);
    el.textContent = Math.round(start) + suffix;
    if (start >= target) clearInterval(timer);
  }, 16);
};

// Auto-animate elements with data-count attribute
document.addEventListener('DOMContentLoaded', function () {
  var counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        var target = parseFloat(el.dataset.count);
        var suffix = el.dataset.suffix || '';
        animateCounter(el, target, 1200, suffix);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  counters.forEach(function (el) { observer.observe(el); });
});
