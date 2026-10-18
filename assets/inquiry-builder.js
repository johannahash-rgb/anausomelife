/* Local email preparation only: no submission, tracking, storage, or network request. */
(() => {
  'use strict';
  const form = document.getElementById('editorial-inquiry');
  if (!form) return;
  const byId = id => document.getElementById(id);
  const purpose = byId('inquiry-purpose');
  const output = byId('inquiry-output');
  const message = byId('inquiry-message');
  const email = byId('inquiry-email');
  const status = byId('inquiry-status');
  const notice = byId('inquiry-output-notice');
  const purposes = {
    product: ['Product review proposal', 'Product or model, the job it does, sample or loan terms, and your suggested testing window.'],
    travel: ['Travel story proposal', 'Property or destination, proposed dates, room configuration, hosting terms, and the story idea.'],
    press: ['Press inquiry', 'Publication or outlet, story angle, deadline with time zone, and interview or image needs.'],
    licensing: ['Photography or content request', 'Story or image, intended channels, duration, edits, and any advertising or exclusivity needs.']
  };
  function updateHelp() {
    byId('inquiry-details-help').textContent = (purposes[purpose.value] || purposes.product)[1];
    // An old preview must never look like it reflects newly edited fields.
    output.hidden = true;
    status.textContent = '';
  }
  purpose.addEventListener('change', updateHelp);
  form.addEventListener('input', () => { output.hidden = true; status.textContent = ''; });
  function prepare() {
    if (!form.reportValidity()) return;
    const value = id => byId(id).value.trim();
    const organization = value('inquiry-organization');
    if (!organization) {
      byId('inquiry-organization').setCustomValidity('Please add your brand, organization, or publication.');
      form.reportValidity();
      return;
    }
    const selected = purposes[purpose.value] || purposes.product;
    const body = [
      'Hello An AUsome Life,', '',
      'Inquiry: ' + selected[0],
      'Brand, organization, or publication: ' + organization,
      'Reference link: ' + (value('inquiry-reference') || 'To discuss'),
      'Timing / deadline and time zone: ' + (value('inquiry-timing') || 'Flexible / to discuss'),
      '', value('inquiry-details') || 'Please let us know whether this is an editorial fit and which details you need.', '',
      'Please confirm fit, scope, any sample or hosting arrangements, timing, and any separate usage rights before we proceed.',
      '', 'Thank you!'
    ].join('\n');
    message.value = body;
    const uri = 'mailto:hello@anausomelife.com?subject=' + encodeURIComponent(selected[0] + ': ' + organization) + '&body=' + encodeURIComponent(body);
    email.href = uri;
    notice.textContent = uri.length > 1800
      ? 'Your draft is ready, not sent. Some email apps shorten long drafts; copy the full request below if needed.'
      : 'Your draft is ready, not sent. Review it, then open your email app or copy it into a message.';
    output.hidden = false;
    status.textContent = 'Email draft prepared. Nothing has been submitted.';
    message.focus();
  }
  byId('inquiry-organization').addEventListener('input', () => byId('inquiry-organization').setCustomValidity(''));
  byId('inquiry-prepare').addEventListener('click', prepare);
  form.addEventListener('submit', event => { event.preventDefault(); prepare(); });
  byId('inquiry-copy').addEventListener('click', async () => {
    const snapshot = message.value;
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(snapshot);
      if (!output.hidden) status.textContent = 'Copied. Paste this into your email and send it when ready.';
    } catch (_) {
      if (!output.hidden) {
        message.focus();
        message.select();
        status.textContent = 'Automatic copying is unavailable. The draft is selected so you can copy it.';
      }
    }
  });
  // Hide the JS-only control without JS; the ordinary email link always works.
  byId('inquiry-prepare').hidden = false;
  updateHelp();
})();
