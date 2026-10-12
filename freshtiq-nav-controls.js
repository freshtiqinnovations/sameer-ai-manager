'use strict';
/* Freshtiq navigation controls (2026-10-12, owner-approved UI correction)
   - Breadcrumb + Back control on major inner pages
   - Visible Close (x) inside the mobile navigation drawer
   - Escape already handled by script.js; this only adds the visual control
   No data access. Public pages only. */
(function () {
  var path = location.pathname.replace(/\/index\.html$/, '/');
  var isHome = path === '/' || path === '' || /\/index\.html$/.test(location.pathname) && path === '/';
  var titles = {
    '/services.html': 'Services', '/pricing.html': 'Pricing', '/reviews.html': 'Reviews',
    '/about.html': 'About', '/contact.html': 'Contact', '/industries.html': 'Industries',
    '/partners.html': 'Partner programme', '/earn-freshtiq.html': 'Earn with Freshtiq',
    '/ai-store.html': 'AI Store', '/build.html': 'Book a strategy call', '/portfolio/': 'Work',
    '/insights/': 'Insights', '/track.html': 'Track project', '/evidence.html': 'Evidence',
    '/delivery.html': 'Delivery', '/investor.html': 'Investor', '/tools/automation-roi-calculator.html': 'ROI calculator'
  };

  /* 1) Close control inside the mobile navigation drawer */
  function addNavClose() {
    var navLinks = document.querySelector('.nav-links');
    if (!navLinks || navLinks.querySelector('.ftq-nav-close')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ftq-nav-close';
    btn.setAttribute('aria-label', 'Close menu');
    btn.innerHTML = '&times;';
    btn.addEventListener('click', function () {
      var h = document.querySelector('.hamburger');
      if (h) h.classList.remove('active');
      navLinks.classList.remove('open');
      document.body.classList.remove('ftq-nav-open');
      var bd = document.querySelector('.ftq-nav-backdrop');
      if (bd) bd.classList.remove('show');
      var hh = document.querySelector('.hamburger');
      if (hh) hh.focus();
    });
    navLinks.insertBefore(btn, navLinks.firstChild);
  }

  /* 2) Breadcrumb + Back on major inner pages */
  function addBreadcrumb() {
    if (isHome) return;
    if (!titles[path]) return;
    var main = document.querySelector('main');
    if (!main || document.querySelector('.ftq-breadcrumb')) return;
    var label = titles[path];
    var bar = document.createElement('nav');
    bar.className = 'ftq-breadcrumb';
    bar.setAttribute('aria-label', 'Breadcrumb');
    bar.innerHTML =
      '<a class="ftq-crumb-back" href="/">&larr; Back to home</a>' +
      '<span class="ftq-crumb-sep" aria-hidden="true">/</span>' +
      '<a href="/">Home</a>' +
      '<span class="ftq-crumb-sep" aria-hidden="true">/</span>' +
      '<span aria-current="page">' + label + '</span>';
    main.insertBefore(bar, main.firstChild);
  }

  function run() { addNavClose(); addBreadcrumb(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
