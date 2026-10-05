(function () {
  'use strict';
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
  const money = value => '₹' + Number(value).toLocaleString('en-IN');
  function cardHTML(offer) {
    const tiers = offer.tiers.slice(0, 3), bonus = tiers[2].bonus || {};
    return '<div class="ftq-bundle-shell"><div class="ftq-bundle-heading"><div><span class="ftq-bundle-kicker">INDIA STARTER AUTOMATION BUNDLE</span><h2>' + escape(offer.title) + '</h2><p>Start with the workflows your business needs. Add useful modules as you grow.</p></div><a class="ftq-bundle-audit" href="/build.html?utm_source=website&amp;utm_medium=bundle_card&amp;utm_campaign=starter_bundle">Get a Free Workflow Audit →</a></div>' +
      '<div class="ftq-bundle-grid">' + tiers.map((tier, index) => '<article class="ftq-bundle-tier' + (index === 2 ? ' ftq-bundle-featured' : '') + '"><h3>' + escape(tier.label) + '</h3><div class="ftq-bundle-price"><small>From</small><strong>' + money(tier.price) + '</strong><span>' + (index ? 'bundle total' : 'one-time starter scope') + '</span></div><p>' + (index === 0 ? 'One core workflow with a clear written scope.' : index === 1 ? 'Two eligible starter modules working together.' : 'Three eligible modules for a connected workflow.') + '</p>' + (index === 2 ? '<div class="ftq-bundle-bonus">+ ' + escape(bonus.label || '1 eligible Quick Add-on') + ' for <strong>' + money(bonus.price) + '</strong></div>' : '') + '</article>').join('') + '</div>' +
      '<p class="ftq-bundle-modules">Eligible modules: ' + (offer.eligible_modules || []).map(escape).join(' · ') + '</p>' +
      '<div class="ftq-bundle-footer"><strong>Free Workflow Audit · Written Scope · Human Support</strong><p>The ' + money(bonus.price) + ' benefit is one eligible Quick Add-on with the 3-module bundle. Full CRM/ERP, large website/app, complex integrations and third-party/API/BSP/Meta/hosting/licence/ad costs are separate. Final scope, eligibility and taxes are confirmed in writing.</p><a href="/pricing.html#automation-bundle">See bundle scope and pricing →</a></div></div>';
  }
  function adjustHeader() {
    const strip = document.getElementById('ft-bundle-offer-bar');
    document.documentElement.style.setProperty('--ftq-offer-strip-height', strip ? Math.ceil(strip.getBoundingClientRect().height) + 'px' : '0px');
  }
  function render(config) {
    const offer = config && config.bundle_offer;
    const hosts = [...document.querySelectorAll('[data-ftq-bundle]')];
    if (!offer?.active || !Array.isArray(offer.tiers) || offer.tiers.length < 3 || offer.tiers.slice(0,3).some(t => !Number.isFinite(Number(t.price)) || Number(t.price) < 0) || !Number.isFinite(Number(offer.tiers[2].bonus?.price))) {
      hosts.forEach(host => { host.hidden = true; });
      document.getElementById('ft-bundle-offer-bar')?.remove();
      document.body.classList.remove('ftq-with-offer'); adjustHeader(); return;
    }
    hosts.forEach(host => { host.innerHTML = cardHTML(offer); host.hidden = false; host.dataset.pricingVersion = config.version || ''; });
    let strip = document.getElementById('ft-bundle-offer-bar');
    if (!strip) { strip = document.createElement('aside'); strip.id = 'ft-bundle-offer-bar'; strip.className = 'ftq-offer-strip'; strip.setAttribute('aria-label', 'India starter automation offer'); document.body.prepend(strip); }
    const third = offer.tiers[2];
    strip.innerHTML = '<span>🇮🇳 <strong>' + escape(offer.title) + '</strong> · 3 modules from <strong>' + money(third.price) + '</strong> + eligible Quick Add-on <strong>' + money(third.bonus.price) + '</strong></span><a href="/pricing.html#automation-bundle">View offer →</a>';
    strip.dataset.pricingVersion = config.version || '';
    document.body.classList.add('ftq-with-offer'); adjustHeader();
    window.FreshtiqBundleOffer.config = config;
    window.dispatchEvent(new CustomEvent('ft:offer-ready', {detail:{version:config.version}}));
  }
  async function refresh() {
    try { const response = await fetch('https://portal.freshtiqautomation.com/api/public/commercial-pricing', {cache:'no-store', signal:AbortSignal.timeout(6500)}); if (response.ok) render(await response.json()); } catch (_) {}
  }
  window.FreshtiqBundleOffer = {render, refresh, cardHTML};
  window.addEventListener('resize', adjustHeader, {passive:true});
  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(adjustHeader);
    window.addEventListener('ft:offer-ready', () => { const strip=document.getElementById('ft-bundle-offer-bar'); if(strip) observer.observe(strip); }, {once:true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', refresh, {once:true}); else refresh();
})();
