/* RSS copying only; no collection, storage, or automatic navigation. */
(() => {
 'use strict';
 const button=document.getElementById('copy-journal-feed');
 const input=document.getElementById('journal-feed-address');
 const status=document.getElementById('feed-copy-status');
 if(!button || !input || !status)return;
 button.hidden=false;
 button.addEventListener('click',async()=>{
  try {
   if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
   await navigator.clipboard.writeText(input.value);
   status.textContent='Feed address copied. Add it to your preferred feed reader.';
   window.AALAnalytics?.track('site_action',{action_name:'rss_copy'});
  } catch (_) {
   input.focus();input.select();
   status.textContent='The feed address is selected. Copy it and add it to your reader.';
  }
 });
})();
