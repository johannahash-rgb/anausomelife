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
    const tracked = event.target.closest('a[data-aal-track],button[data-aal-track]');
    if (tracked) {
      window.AALAnalytics.track('site_action', {
        action_name: tracked.dataset.aalTrack,
        link_url: tracked.href || '',
        link_text: (tracked.textContent || '').trim()
      });
    }
    const link = event.target.closest('a[href]');
    if (!link) return;
    let url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    if (url.origin !== location.origin && /^https?:$/.test(url.protocol)) {
      window.AALAnalytics.track('outbound_click', {
        destination_domain: url.hostname,
        link_text: (link.textContent || '').trim()
      });
    }
    if (/\.(pdf|docx?|xlsx?|pptx?|zip)(\?|#|$)/i.test(url.pathname + url.search + url.hash)) {
      window.AALAnalytics.track('file_download', {
        file_extension: (url.pathname.match(/\.([a-z0-9]+)$/i) || [,''])[1],
        file_name: url.pathname.split('/').pop() || ''
      });
    }
  });

  document.addEventListener('submit', event => {
    const form = event.target.closest('form[role="search"],form[action*="library"]');
    if (!form) return;
    window.AALAnalytics.track('site_search', { search_surface: form.id || form.className || 'site_search' });
  });

  const thresholds = new Set();
  function recordDepth() {
    const max = Math.max(document.documentElement.scrollHeight - innerHeight, 1);
    const percent = Math.round((scrollY / max) * 100);
    [50, 90].forEach(mark => {
      if (percent >= mark && !thresholds.has(mark)) {
        thresholds.add(mark);
        window.AALAnalytics.track('scroll_depth', { percent_scrolled: mark });
      }
    });
    if (thresholds.size === 2) removeEventListener('scroll', recordDepth);
  }
  addEventListener('scroll', recordDepth, { passive: true });
})();