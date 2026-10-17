/* Prepare a reviewable email on the visitor's device. No form submission or storage. */
(() => {
  'use strict';
  const marqueeRoots = typeof document.querySelectorAll === 'function' ? document.querySelectorAll('[data-brand-marquee]') : [];
  marqueeRoots.forEach((reel) => {
    const viewport = reel.querySelector('.brand-marquee');
    if (!viewport) return;
    const distance = () => Math.max(260, Math.round(viewport.clientWidth * 0.78));
    reel.querySelector('[data-brand-scroll="prev"]')?.addEventListener('click', () => {
      viewport.scrollBy({ left: -distance(), behavior: 'smooth' });
    });
    reel.querySelector('[data-brand-scroll="next"]')?.addEventListener('click', () => {
      viewport.scrollBy({ left: distance(), behavior: 'smooth' });
    });
  });
  const form=document.getElementById('brand-request');
  if(!form)return;
  const story=document.getElementById('brand-story');
  const supplied=new URLSearchParams(location.search).get('story');
  if(supplied){try{const url=new URL(supplied);if(url.protocol==='https:'&&['anausomelife.com','www.anausomelife.com'].includes(url.hostname)){url.hash='';url.search='';story.value=url.href;}}catch(_){}}
  async function copy(value,status,field){
    try{if(!navigator.clipboard?.writeText)throw new Error('clipboard-unavailable');await navigator.clipboard.writeText(value);status.textContent='Copied.';}
    catch(_){if(field){field.focus();field.select();status.textContent='Select and copy the message below.';}else{status.textContent='Please select and copy the credit above.';}}
  }
  const credit=document.querySelector('[data-copy-credit]');
  credit?.addEventListener('click',()=>copy(document.getElementById('brand-credit-text').textContent,document.querySelector('[data-credit-status]')));
  const output=document.getElementById('brand-request-output');
  const text=document.getElementById('brand-request-text');
  const email=document.getElementById('brand-email-link');
  form.addEventListener('submit',event=>event.preventDefault());
  document.getElementById('brand-prepare').addEventListener('click',()=>{
    if(!form.reportValidity())return;
    const values=new FormData(form);
    const brand=String(values.get('brand')||'').trim();
    const use=String(values.get('usage')||'');
    const subject=`Content request: ${brand}`;
    const body=`Hello An AUsome Life,\n\nBrand or organization: ${brand}\nStory: ${story.value.trim()||'New collaboration / to discuss'}\nIntended use: ${use}\n\n${String(values.get('details')||'').trim()||'Please let us know what is available and what further details you need.'}\n\nPlease confirm the available files, credit, permission terms, and any licensing fee.\n\nThank you!`;
    text.value=body;
    email.href='mailto:hello@anausomelife.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    output.hidden=false;
    text.focus();
  });
  document.getElementById('brand-copy-request').addEventListener('click',()=>copy(text.value,document.getElementById('brand-copy-status'),text));
})();
