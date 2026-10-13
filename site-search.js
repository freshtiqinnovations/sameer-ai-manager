'use strict';
/* Freshtiq public website global search (2026-10-12, owner-approved Phase A).
   PUBLIC content only — never queries or reveals private CRM data. */
(function () {
  var INDEX = [
    { t: 'Earn with Freshtiq — Sales Executive Opportunity', u: '/earn-freshtiq.html', k: 'earn sales executive job apply commission recruitment training earning' },
    { t: 'Services overview', u: '/services.html', k: 'services automation ai whatsapp website crm erp' },
    { t: 'WhatsApp AI Sales Bot', u: '/services/whatsapp-automation.html', k: 'whatsapp business api automation bot chatbot sales' },
    { t: 'AI Agents', u: '/services/ai-agents.html', k: 'ai agent automation assistant support' },
    { t: 'Website Development', u: '/services/website-development.html', k: 'website development landing page' },
    { t: 'CRM / ERP', u: '/services/crm-erp-development.html', k: 'crm erp pipeline leads' },
    { t: 'Workflow Automation', u: '/services/workflow-automation.html', k: 'workflow automation integration' },
    { t: 'Appointment Booking Automation', u: '/services/appointment-booking-automation.html', k: 'appointment booking clinic salon restaurant scheduling' },
    { t: 'Industries', u: '/industries.html', k: 'industries clinic salon restaurant real estate travel manufacturing' },
    { t: 'Pricing', u: '/pricing.html', k: 'pricing cost price how much plans starting price currency' },
    { t: 'Portfolio / Work', u: '/portfolio/', k: 'work portfolio case studies examples' },
    { t: 'Reviews', u: '/reviews.html', k: 'reviews testimonials feedback' },
    { t: 'Insights', u: '/insights/', k: 'insights blog guides articles' },
    { t: 'Track Project', u: '/track.html', k: 'track project status order' },
    { t: 'Contact', u: '/contact.html', k: 'contact support help email phone whatsapp' },
    { t: 'About Freshtiq', u: '/about.html', k: 'about company freshtiq innovations' },
    { t: 'Privacy Policy', u: '/privacy-policy.html', k: 'privacy data policy consent' },
    { t: 'Terms & Conditions', u: '/terms-and-conditions.html', k: 'terms conditions legal' },
    { t: 'FAQ — is there a fixed salary?', u: '/earn-freshtiq.html#apply', k: 'faq salary commission guaranteed income' },
    { t: 'FAQ — how is commission calculated?', u: '/earn-freshtiq.html#apply', k: 'faq commission calculation payout collected' },
    { t: 'Customer Login', u: 'https://portal.freshtiqautomation.com/customer', k: 'login customer portal account sign in invoice project' },
    { t: 'Sales Executive Login', u: 'https://portal.freshtiqautomation.com/se', k: 'login sales executive se dashboard training leads' },
    { t: 'Partner programme (Sales Partner / Reseller)', u: '/partners.html', k: 'partner reseller referral commission programme' }
  ];
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function search(q) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    var terms = q.split(/\s+/).filter(Boolean);
    var out = [];
    for (var i = 0; i < INDEX.length; i++) {
      var e = INDEX[i]; var hay = (e.t + ' ' + e.k).toLowerCase(); var score = 0;
      for (var j = 0; j < terms.length; j++) { if (hay.indexOf(terms[j]) !== -1) score++; else { score = -1; break; } }
      if (score < 0) continue;
      if (e.t.toLowerCase().indexOf(q) === 0) score += 2;
      out.push({ e: e, s: score });
    }
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 8).map(function (x) { return x.e; });
  }
  function build() {
    var host = document.getElementById('ftqSiteSearch');
    if (!host) return;
    host.innerHTML = '<div class="ftq-ss-wrap" style="position:relative"><label class="ftq-ss-label" for="ftqSsInput" style="position:absolute;left:-9999px">Search Freshtiq</label>' +
      '<input id="ftqSsInput" type="search" autocomplete="off" placeholder="Search" aria-label="Search Freshtiq services, pricing and FAQs" style="min-height:40px;border-radius:10px;border:1px solid rgba(120,150,170,.5);background:rgba(255,255,255,.06);color:inherit;padding:8px 12px;min-width:210px"/>' +
      '<div id="ftqSsResults" role="listbox" style="position:absolute;top:46px;left:0;right:0;background:#0d2639;border:1px solid #355568;border-radius:12px;z-index:60;max-height:60vh;overflow:auto;display:none"></div></div>';
    var input = document.getElementById('ftqSsInput'), box = document.getElementById('ftqSsResults');
    function render() {
      var r = search(input.value);
      if (!r.length) { box.style.display = input.value.trim() ? 'block' : 'none'; box.innerHTML = input.value.trim() ? '<div style="padding:12px;color:#acc5d6;font-size:13px">No public results. Try “pricing”, “WhatsApp”, “Earn Freshtiq”.</div>' : ''; return; }
      box.style.display = 'block';
      box.innerHTML = r.map(function (e) { return '<a href="' + esc(e.u) + '" style="display:block;padding:11px 13px;color:#e9f6ff;text-decoration:none;border-bottom:1px solid #1e3a50;font-size:14px">' + esc(e.t) + '</a>'; }).join('');
    }
    input.addEventListener('input', render);
    input.addEventListener('focus', render);
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') box.style.display = 'none'; if (e.key === 'Enter') { var f = box.querySelector('a'); if (f) { e.preventDefault(); location.href = f.getAttribute('href'); } } });
    document.addEventListener('click', function (e) { if (!host.contains(e.target)) box.style.display = 'none'; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
