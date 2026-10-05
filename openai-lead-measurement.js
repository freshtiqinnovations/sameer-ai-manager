(function (w, d) {
  'use strict';
  if (w.FreshtiqOpenAIMeasurement) return;
  const PIXEL_ID = '2QUc83F3ByP9PTssFZQtBk';
  const CONSENT_KEY = 'ftq_openai_measurement_consent_v1';
  const enabled = PIXEL_ID.trim().length > 0;
  const allowedPage = !/^\/(?:payment|checkout|cart|customer|privacy|terms|refund|security-policy|404|bot|track)(?:\/|\.|$)/i.test(((w.location || {}).pathname || '/'));
  const seen = new Set();
  let started = false;
  let granted = false;
  let serial = 0;
  try { granted = localStorage.getItem(CONSENT_KEY) === 'granted'; } catch (_) {}

  function start() {
    if (!enabled || !allowedPage || !granted || started) return;
    started = true;
    if (!w.oaiq) {
      const queue = function () { queue.q.push(arguments); };
      queue.q = [];
      w.oaiq = queue;
      const sdk = d.createElement('script');
      sdk.async = true;
      sdk.src = 'https://bzrcdn.openai.com/sdk/oaiq.min.js';
      d.head.appendChild(sdk);
    }
    w.oaiq('consent', false);
    w.oaiq('init', { pixelId: PIXEL_ID });
    w.oaiq('consent', true);
  }

  function setConsent(value) {
    granted = value === true;
    try { localStorage.setItem(CONSENT_KEY, granted ? 'granted' : 'denied'); } catch (_) {}
    if (!enabled) return;
    try {
      if (granted) {
        start();
        if (started && w.oaiq) w.oaiq('consent', true);
      } else if (started && w.oaiq) {
        w.oaiq('consent', false);
      }
    } catch (_) { /* Measurement failure must not interrupt the consent UI. */ }
  }

  function eventId() {
    if (w.crypto && typeof w.crypto.randomUUID === 'function') return w.crypto.randomUUID();
    serial += 1;
    return 'ftq-lead-' + Date.now().toString(36) + '-' + serial.toString(36) + '-' + Math.random().toString(36).slice(2);
  }

  function leadCreated(leadKey) {
    if (!enabled || !allowedPage || !granted || leadKey == null || String(leadKey).trim() === '') return false;
    const key = String(leadKey);
    if (seen.has(key)) return false;
    try {
      start();
      w.oaiq('measure', 'lead_created', { type: 'customer_action' }, { event_id: eventId(), opt_out: true });
      seen.add(key);
      if (seen.size > 500) seen.delete(seen.values().next().value);
      return true;
    } catch (_) {
      return false;
    }
  }

  w.FreshtiqOpenAIMeasurement = Object.freeze({ enabled, setConsent, leadCreated });
  try { start(); } catch (_) { /* Keep the website usable if the SDK fails. */ }
})(window, document);
