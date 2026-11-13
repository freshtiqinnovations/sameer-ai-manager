(() => {
  'use strict';

  const consentKey = 'ftq_analytics_consent_v1';
  const storageKey = 'ftq_form_attribution_v1';
  const campaignFields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const marketplaceSources = new Set(['upwork', 'fiverr', 'freelancer', 'freelancercom', 'peopleperhour', 'pph']);
  const clickFields = ['gclid', 'gbraid', 'wbraid'];
  const fields = [...campaignFields, ...clickFields];
  const query = new URLSearchParams(location.search);
  const currentTags = Object.fromEntries(fields.map(key => [
    key, (query.get(key) || '').trim().slice(0, clickFields.includes(key) ? 200 : 120)
  ]));

  function externalOrigin(referrer) {
    try {
      const url = new URL(referrer);
      const host = url.hostname;
      if (!['https:', 'http:'].includes(url.protocol) || url.origin === location.origin ||
          host === 'freshtiqautomation.com' || host.endsWith('.freshtiqautomation.com')) return '';
      return url.origin;
    } catch (_) {
      return '';
    }
  }

  function marketplaceTag(source) {
    const key = String(source || '').toLowerCase().replace(/[^a-z0-9]/g, '');
    return marketplaceSources.has(key) ? key : '';
  }

  const current = {
    ...currentTags,
    referrer: externalOrigin(document.referrer),
    landing_page: location.origin + location.pathname
  };

  function allowed() {
    try { return localStorage.getItem(consentKey) === 'granted'; }
    catch (_) { return false; }
  }

  function capture() {
    if (!allowed()) {
      try { sessionStorage.removeItem(storageKey); } catch (_) {}
      return { ...Object.fromEntries(fields.map(key => [key, ''])), referrer: '' };
    }

    try {
      const saved = JSON.parse(sessionStorage.getItem(storageKey) || 'null');
      // A new external visit or tagged campaign starts a new attribution context.
      // Untagged internal links keep the existing source, including paid click IDs.
      const newEntry = current.referrer || fields.some(key => current[key]);
      const attribution = newEntry || !saved ? current : saved;
      sessionStorage.setItem(storageKey, JSON.stringify(attribution));
      return attribution;
    } catch (_) {
      return current;
    }
  }

  function getContext(previous = {}) {
    const attribution = capture();
    // The existing marketplace handoff restriction also applies without analytics.
    const restrictedSource = marketplaceTag(currentTags.utm_source) || marketplaceTag(previous.utm_source);
    return restrictedSource ? { ...attribution, utm_source: restrictedSource } : attribution;
  }

  window.FreshtiqFormAttribution = { getContext };
  capture();

  // The consent UI saves the choice before the click bubbles to document.
  document.addEventListener('click', event => {
    if (event.target.closest?.('#ftq-consent [data-choice]')) capture();
  });
  window.addEventListener('storage', event => {
    if (event.key === consentKey || event.key === null) capture();
  });
})();
