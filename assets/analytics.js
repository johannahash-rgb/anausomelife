/* Optional, consent-first measurement. Disabled until a reviewed property is configured.
   No pre-consent queue, tool text, inquiry fields, query strings or link bodies. */
(() => {
  'use strict';
  if (window.AALAnalytics) return;
  const KEY = 'aal-measurement-choice-v1';
  const TTL = 180 * 24 * 60 * 60 * 1000;
  const paths = new Set(['/', '/blog.html', '/reviews.html', '/follow.html', '/media/', '/press.html', '/contact.html', '/product-guides.html', '/privacy.html']);
  const goals = new Set(['review_coffee', 'review_kitchen', 'review_records', 'rss_open', 'rss_copy', 'follow_instagram', 'contact_email_open', 'press_facts_open']);
  let configured = false, allowed = false, live = false, loading = false, id = '', canonical = '';
  const seen = new Set();
  const byId = key => document.getElementById(key);
  const blocked = () => navigator.globalPrivacyControl === true || ['1', 'yes'].includes(navigator.doNotTrack) || ['1', 'yes'].includes(window.doNotTrack);
  // Discard old pending values; never replay a visitor's pre-consent activity.
  if (Array.isArray(window.__AAL_PENDING_EVENTS__)) window.__AAL_PENDING_EVENTS__.length = 0;
  function remembered() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY));
      if (data && typeof data.allowed === 'boolean' && Number.isFinite(data.at) && data.at <= Date.now() && Date.now() - data.at < TTL) return data.allowed;
      localStorage.removeItem(KEY);
    } catch (_) { /* Blocked or malformed storage never enables measurement. */ }
    return false;
  }
  function show(text) {
    const state = byId('measurement-state');
    if (state) state.textContent = text;
    const controls = byId('measurement-controls');
    if (controls) controls.hidden = !configured || blocked();
  }
  function save(value) {
    try { localStorage.setItem(KEY, JSON.stringify({allowed:value, at:Date.now()})); }
    catch (_) { /* Choice applies only to this page when storage is unavailable. */ }
  }
  function gtag() { window.dataLayer.push(arguments); }
  function stop() {
    allowed = false; live = false;
    if (id) window['ga-disable-' + id] = true;
    // Do not send consent pings or event history on withdrawal.
    if (loading && window.dataLayer) window.dataLayer.length = 0;
    show(blocked() ? 'Measurement is off because this browser requests privacy protection.' : 'Optional measurement is off.');
  }
  function start() {
    if (!configured || !allowed || blocked() || live || loading) return;
    // Do not reconfigure a different tag or container installed by someone else.
    if (typeof window.gtag === 'function' || document.querySelector('script[src*="googletagmanager.com/gtag"]')) {
      show('Measurement remains off because another tag needs review.'); return;
    }
    loading = true;
    window['ga-disable-' + id] = false;
    window.dataLayer = [];
    window.gtag = gtag;
    gtag('consent', 'default', {analytics_storage:'denied', ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied'});
    gtag('consent', 'update', {analytics_storage:'granted', ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied'});
    gtag('js', new Date());
    gtag('config', id, {send_page_view:false, allow_google_signals:false, allow_ad_personalization_signals:false, page_location:canonical, page_referrer:'', page_title:'An AUsome Life'});
    const script = document.createElement('script');
    script.async = true;
    script.referrerPolicy = 'no-referrer';
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    script.onload = () => {
      if (!allowed || blocked()) { stop(); return; }
      loading = false; live = true;
      gtag('event', 'page_view', {page_location:canonical, page_referrer:'', page_title:'An AUsome Life'});
      show('Optional measurement is on in this browser. You can turn it off here.');
    };
    script.onerror = () => { loading = false; stop(); show('Measurement could not load. The website still works normally.'); };
    document.head.append(script);
  }
  function track(name, params = {}) {
    if (blocked()) { if (allowed) stop(); return false; }
    const goal = name === 'site_action' && params && params.action_name;
    if (!live || !allowed || !goals.has(goal) || seen.has(goal)) return false;
    seen.add(goal);
    gtag('event', 'site_action', {action_name:goal, page_location:canonical, page_referrer:'', page_title:'An AUsome Life'});
    return true;
  }
  window.AALAnalytics = {track, get active() { return live && allowed && !blocked(); }};
  if (blocked()) { show('Measurement is off because this browser requests privacy protection.'); return; }
  const link = document.querySelector('link[rel="canonical"]');
  try {
    const url = new URL(link ? link.href : location.href);
    if (url.origin !== 'https://anausomelife.com' || !paths.has(url.pathname)) return;
    canonical = url.origin + url.pathname;
  } catch (_) { return; }
  fetch('/data/site-config.json?v=20261018-reader-growth-v1', {credentials:'omit', cache:'no-store'})
    .then(response => response.ok ? response.json() : {})
    .then(config => {
      id = typeof config.ga4MeasurementId === 'string' ? config.ga4MeasurementId.trim() : '';
      configured = config.analyticsEnabled === true && config.analyticsPrivacyReviewed === true && /^G-[A-Z0-9]{4,20}$/.test(id);
      if (!configured) { show('Website analytics is not currently enabled. No analytics service is loaded by this site.'); return; }
      allowed = remembered();
      show(allowed ? 'Loading the optional measurement you allowed.' : 'Optional measurement is off unless you allow it.');
      const allow = byId('measurement-allow'), deny = byId('measurement-deny');
      if (allow) allow.addEventListener('click', () => {
        if (blocked()) { stop(); return; }
        allowed = true; save(true);
        if (window.gtag && !live) { show('Permission saved. Reload this page to start measurement.'); return; }
        start();
      });
      if (deny) deny.addEventListener('click', () => { save(false); stop(); });
      start();
    }).catch(() => show('Website analytics is unavailable and remains off.'));
  document.addEventListener('click', event => {
    const target = event.target && typeof event.target.closest === 'function' ? event.target.closest('a[data-aal-goal],button[data-aal-goal]') : null;
    if (target) track('site_action', {action_name:target.dataset.aalGoal});
  });
})();
