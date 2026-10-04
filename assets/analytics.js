/* An AUsome Life — privacy-light analytics bridge.
   Add a valid GA4 measurement ID to /data/site-config.json to activate GA4.
   Site features can call window.AALAnalytics.track() before GA has loaded. */
(() => {
  'use strict';
  if (window.AALAnalytics) return;

  const queued = [];
  let live = false;
  const clean = value => {
    if (value == null) return value;
    if (typeof value === 'string') return value.slice(0, 120);
    if (typeof value === 'number' || typeof value === 'boolean') return value;
    return String(value).slice(0, 120);
  };
  const safeParams = params => Object.fromEntries(
    Object.entries(params || {}).map(([key, value]) => [key, clean(value)])
  );

  const early = Array.isArray(window.__AAL_PENDING_EVENTS__) ? window.__AAL_PENDING_EVENTS__.splice(0) : [];

  window.AALAnalytics = {
    track(name, params = {}) {
      const event = { name: String(name || '').replace(/[^a-zA-Z0-9_]/g, '_').slice(0, 40), params: safeParams(params) };
      if (!event.name) return;
      if (live && typeof window.gtag === 'function') window.gtag('event', event.name, event.params);
      else queued.push(event);
    },
    get active() { return live; }
  };

  early.forEach(event => window.AALAnalytics.track(event.name, event.params));

  if (navigator.doNotTrack === '1') return;

  fetch('/data/site-config.json?v=20261004', { credentials: 'same-origin' })
    .then(response => response.ok ? response.json() : {})
    .then(config => {
      const id = (config.ga4MeasurementId || '').trim();
      if (!/^G-[A-Z0-9]+$/i.test(id)) return;

      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function(){ dataLayer.push(arguments); };
      gtag('js', new Date());
      gtag('consent', 'default', {
        analytics_storage: 'granted',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
      gtag('config', id, {
        send_page_view: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false
      });

      const script = document.createElement('script');
      script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
      script.onload = () => {
        live = true;
        document.documentElement.dataset.aalAnalytics = 'active';
        queued.splice(0).forEach(event => gtag('event', event.name, event.params));
      };
      document.head.append(script);
    })
    .catch(() => { /* The site must keep working even when analytics does not. */ });

  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-aal-track],button[data-aal-track]');
    if (!link) return;
    window.AALAnalytics.track('site_action', {
      action_name: link.dataset.aalTrack,
      link_url: link.href || '',
      link_text: (link.textContent || '').trim()
    });
  });
})();