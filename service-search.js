/* ═══════════════════════════════════════════
   FRESHTIQ SERVICE SEARCH — v1.0
   Premium client-side search engine
   ═══════════════════════════════════════════ */

(function() {
  'use strict';

  const SEARCH_DATA = [
    { id:'clinic', icon:'🏥', name:'Clinic / Hospital', cat:'Industry',
      desc:'Appointment booking bot, patient reminders, digital records, AI symptom triage.',
      price:'₹8K – ₹70K+', q:'clinic hospital doctor patient appointment medical' },
    { id:'restaurant', icon:'🍽️', name:'Restaurant / Cafe', cat:'Industry',
      desc:'QR menu ordering, WhatsApp order alerts, table booking bot, automated billing.',
      price:'₹8K – ₹70K+', q:'restaurant cafe food menu ordering kitchen billing' },
    { id:'hotel', icon:'🏨', name:'Hotel / Resort', cat:'Industry',
      desc:'WhatsApp booking bot, automated guest messages, room service, feedback collection.',
      price:'₹8K – ₹70K+', q:'hotel resort booking guest room hospitality' },
    { id:'travel', icon:'✈️', name:'Travel Agency', cat:'Industry',
      desc:'Flight/hotel search bot, automated itinerary builder, WhatsApp trip updates.',
      price:'₹8K – ₹70K+', q:'travel agency flight hotel itinerary booking trip' },
    { id:'factory', icon:'🏭', name:'Factory / Manufacturing', cat:'Industry',
      desc:'Inventory ERP bot, production tracking dashboard, WhatsApp stock alerts.',
      price:'₹15K – ₹70K+', q:'factory manufacturing production inventory erp stock' },
    { id:'hr', icon:'👥', name:'HR & Payroll Automation', cat:'Industry',
      desc:'HR bot for leave/attendance, automated payroll, employee portal, WhatsApp helpdesk.',
      price:'₹15K – ₹70K+', q:'hr human resources payroll attendance leave employee staff' },
    { id:'accountant', icon:'💰', name:'Accountant / Finance', cat:'Industry',
      desc:'Invoice automation, payment reminders, expense tracking, GST-compliant reports.',
      price:'₹10K – ₹70K+', q:'accountant finance invoice gst billing payment expense' },
    { id:'sales', icon:'📊', name:'Sales Executive Tracking', cat:'Industry',
      desc:'CRM bot with GPS check-in, lead tracking dashboard, daily performance reports.',
      price:'₹10K – ₹70K+', q:'sales executive team tracking crm gps lead performance' },
    { id:'realestate', icon:'🏠', name:'Real Estate', cat:'Industry',
      desc:'Property enquiry bot, WhatsApp listing broadcast, CRM integration, visit scheduler.',
      price:'₹10K – ₹70K+', q:'real estate property broker enquiry listing visit' },
    { id:'ecommerce', icon:'🛒', name:'E-commerce / Retail', cat:'Industry',
      desc:'Order management bot, WhatsApp tracking, cart recovery, inventory sync dashboard.',
      price:'₹10K – ₹70K+', q:'ecommerce retail shop store order cart inventory' },
    { id:'laundry', icon:'🧺', name:'Laundry', cat:'Industry',
      desc:'Order management bot with pickup scheduling, WhatsApp status tracking, delivery alerts.',
      price:'₹8K – ₹50K+', q:'laundry dryclean wash iron pickup delivery' },
    { id:'qr', icon:'📱', name:'QR Customer Service', cat:'Industry',
      desc:'Scan QR → WhatsApp chatbot → auto-resolution or human handoff. 24/7 support.',
      price:'₹8K – ₹60K+', q:'qr customer service support scan code whatsapp' },
    { id:'whatsappbot', icon:'💬', name:'WhatsApp Automation', cat:'Service',
      desc:'AI sales bots, FAQ auto-reply, lead capture, CRM integration. Works 24/7.',
      price:'Starts ₹15,000', q:'whatsapp bot automation chat sales support lead' },
    { id:'telegrambot', icon:'✈️', name:'Telegram Bot Development', cat:'Service',
      desc:'Custom Telegram bots for support, sales, CRM, ERP. Multi-language, multi-user.',
      price:'Starts ₹8,000', q:'telegram bot automation support crm erp' },
    { id:'aiagent', icon:'🧠', name:'AI Agents', cat:'Service',
      desc:'Custom AI agents trained on your business data. DeepSeek/GPT powered.',
      price:'Starts ₹25,000', q:'ai agent artificial intelligence gpt deepseek chatbot' },
    { id:'website', icon:'🌐', name:'Website Development', cat:'Service',
      desc:'Premium custom websites. Business, e-commerce, travel. AI chat built-in.',
      price:'Starts ₹10,000', q:'website development design business ecommerce travel' },
    { id:'crm', icon:'📊', name:'ERP / CRM Software', cat:'Service',
      desc:'Sales CRM, inventory ERP, HR systems, factory management. Custom-built.',
      price:'Starts ₹25,000', q:'crm erp software sales inventory management system' },
    { id:'mobileapp', icon:'📱', name:'Mobile Apps', cat:'Service',
      desc:'iOS & Android apps with AI, WhatsApp, portal sync, dashboards.',
      price:'Starts ₹50,000', q:'mobile app ios android flutter react native' },
    { id:'seo', icon:'📈', name:'SEO & Digital Marketing', cat:'Service',
      desc:'SEO, Google Business Profile, content marketing, lead generation ads.',
      price:'Starts ₹3,000', q:'seo digital marketing google business lead ads' },
    { id:'automation', icon:'⚡', name:'Business Automation', cat:'Service',
      desc:'Custom automation workflows, email automation, invoice systems, reporting bots.',
      price:'Custom Quote', q:'business automation workflow email invoice reporting' },
    { id:'reseller', icon:'🤝', name:'Reseller Program', cat:'Partner',
      desc:'Sell ready automation products. No coding. No team. Earn commission.',
      price:'Join Free', q:'reseller partner affiliate commission sell program' },
    { id:'investor', icon:'💎', name:'Investor Relations', cat:'Partner',
      desc:'Invest in Freshtiq Automation. Revenue share model with transparent dashboard.',
      price:'Revenue Share', q:'investor investment fund capital revenue share' },
    { id:'roi', icon:'📈', name:'ROI Calculator', cat:'Tool',
      desc:'Calculate how much you save with AI automation. See your ROI in seconds.',
      price:'Free', q:'roi calculator return on investment savings automation' },
    { id:'tracking', icon:'📦', name:'Tracking Portal', cat:'Tool',
      desc:'Real-time order/shipment tracking portal for your customers.',
      price:'Starts ₹10,000', q:'tracking portal order shipment delivery status' }
  ];

  /* ─── DOM refs ─── */
  let input, results, noResult, tags, recent, clearBtn;
  let active = false;

  function init() {
    input = document.getElementById('siteSearch');
    if (!input) return;
    results = document.getElementById('searchResults');
    noResult = document.getElementById('searchNoResult');
    tags = document.getElementById('searchTags');
    recent = document.getElementById('searchRecent');
    clearBtn = document.getElementById('searchClear');

    input.addEventListener('input', onInput);
    input.addEventListener('focus', function() { if (this.value.trim()) showResults(); });
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.search-section')) hideResults();
    });
    if (clearBtn) clearBtn.addEventListener('click', clearSearch);
    if (tags) tags.addEventListener('click', function(e) {
      const tag = e.target.closest('.search-tag');
      if (tag && tag.dataset.q) {
        input.value = tag.dataset.q;
        onInput();
        input.focus();
      }
    });

    loadRecent();
  }

  function onInput() {
    const v = input.value.trim().toLowerCase();
    if (v.length === 0) {
      hideResults();
      if (clearBtn) clearBtn.style.display = 'none';
      loadRecent();
      return;
    }
    if (clearBtn) clearBtn.style.display = 'block';
    filterAndRender(v);
  }

  function filterAndRender(q) {
    const terms = q.split(/[\s,]+/).filter(Boolean);
    const matches = SEARCH_DATA.filter(function(item) {
      return terms.every(function(t) {
        return item.name.toLowerCase().includes(t) || item.cat.toLowerCase().includes(t) || item.q.toLowerCase().includes(t);
      });
    });

    if (matches.length === 0) {
      results.innerHTML = '';
      results.classList.remove('has-results');
      showNoResult(q);
      return;
    }

    hideNoResult();
    renderResults(matches);
    results.classList.add('has-results');
    saveRecent(q);
  }

  function renderResults(items) {
    var html = '';
    items.forEach(function(item) {
      var waText = 'Hi%20Freshtiq!%20I%20need%20' + encodeURIComponent(item.name) + '%20automation';
      var viewHref = item.cat === 'Industry' ? '#industries' :
                     item.id === 'reseller' ? '#reseller' :
                     item.id === 'investor' ? '#investor' :
                     item.id === 'roi' ? '#roi-calc' :
                     item.id === 'tracking' ? '#tracking' :
                     '/ai-store.html';
      var viewLabel = (item.cat === 'Industry' || item.cat === 'Partner' || item.cat === 'Tool') ? 'View Section' : 'View in AI Store';
      html += '<div class="search-result-card">' +
        '<div class="sr-header">' +
          '<span class="sr-title">' + item.icon + ' ' + item.name + '</span>' +
          '<span class="sr-category">' + item.cat + '</span>' +
        '</div>' +
        '<div class="sr-desc">' + item.desc + '</div>' +
        '<div class="sr-footer">' +
          '<span class="sr-price">' + item.price + '</span>' +
          '<div class="sr-ctas">' +
            '<a href="https://wa.me/918381848389?text=' + waText + '" target="_blank" class="sr-cta sr-cta-wa">💬 WhatsApp Quote</a>' +
            '<a href="' + viewHref + '" class="sr-cta sr-cta-view">👁️ ' + viewLabel + '</a>' +
          '</div>' +
        '</div>' +
      '</div>';
    });
    results.innerHTML = html;
  }

  function showNoResult(q) {
    if (!noResult) {
      noResult = document.getElementById('searchNoResult');
      if (!noResult) {
        var div = document.createElement('div');
        div.id = 'searchNoResult';
        div.className = 'search-no-result';
        results.parentNode.insertBefore(div, results.nextSibling);
        noResult = div;
      }
    }
    noResult.className = 'search-no-result visible';
    noResult.innerHTML = '<p>❌ Couldn\'t find "<strong>' + escapeHtml(q) + '</strong>" in our services.</p><p>Tell us on WhatsApp — we can build custom automation for your business.</p><a href="https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20need%20custom%20automation%20for%20' + encodeURIComponent(q) + '" target="_blank">💬 Ask on WhatsApp</a>';
  }

  function hideNoResult() {
    if (noResult) noResult.className = 'search-no-result';
  }

  function showResults() {
    if (results) results.classList.add('has-results');
  }

  function hideResults() {
    if (results) results.classList.remove('has-results');
    hideNoResult();
  }

  function clearSearch() {
    input.value = '';
    if (clearBtn) clearBtn.style.display = 'none';
    hideResults();
    loadRecent();
    input.focus();
  }

  function saveRecent(q) {
    try {
      var recents = JSON.parse(localStorage.getItem('ft_search_recent') || '[]');
      recents = recents.filter(function(r) { return r !== q; });
      recents.unshift(q);
      if (recents.length > 5) recents = recents.slice(0, 5);
      localStorage.setItem('ft_search_recent', JSON.stringify(recents));
      renderRecent(recents);
    } catch(e) {}
    trackSearch(q);
  }

  function loadRecent() {
    try {
      var recents = JSON.parse(localStorage.getItem('ft_search_recent') || '[]');
      renderRecent(recents);
    } catch(e) {}
  }

  function renderRecent(items) {
    if (!recent) return;
    if (items.length === 0) { recent.className = 'search-recent'; recent.innerHTML = ''; return; }
    recent.className = 'search-recent visible';
    var html = '<span class="search-recent-label">🕐 Recent:</span>';
    items.forEach(function(r) {
      html += '<span class="search-recent-tag" data-q="' + escapeAttr(r) + '">' + escapeHtml(r) + '</span>';
    });
    recent.innerHTML = html;
    recent.addEventListener('click', function(e) {
      var tag = e.target.closest('.search-recent-tag');
      if (tag && tag.dataset.q) {
        input.value = tag.dataset.q;
        onInput();
        input.focus();
      }
    });
  }

  function trackSearch(q) {
    if (typeof gtag === 'function') {
      try { gtag('event', 'search', { search_term: q, page: window.location.pathname }); } catch(e) {}
    }
  }

  function escapeHtml(s) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(s));
    return div.innerHTML;
  }

  function escapeAttr(s) {
    return s.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
