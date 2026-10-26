/* Accessible multi-topic browsing; all entries and links are present in HTML. */
(() => {
  'use strict';
  const fold=value=>(value||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  document.querySelectorAll('[data-collection]').forEach(collection=>{
    const form=collection.querySelector('form'),q=form.elements.q,kind=form.elements.kind||form.elements.role,sort=form.elements.sort;
    const topics=[...form.querySelectorAll('[name=topic]')],box=collection.querySelector('[data-collection-results]'),cards=[...box.children];
    const order=new Map(cards.map((card,i)=>[card,i])),status=collection.querySelector('[data-collection-status]'),empty=collection.querySelector('[data-collection-empty]'),more=collection.querySelector('[data-collection-more]');
    const care=collection.dataset.collection==='support',pageSize=care?8:12;
    let limit=pageSize;
    function readURL(){
      const params=new URLSearchParams(location.search);q.value=params.get('q')||'';kind.value=params.get(care?'role':'kind')||'';sort.value=params.get('sort')||'featured';
      const selected=params.getAll('topic');topics.forEach(input=>{input.checked=selected.includes(input.value);});limit=pageSize;
    }
    function apply(mode){
      const selected=topics.filter(input=>input.checked).map(input=>input.value),words=fold(q.value.trim()).split(/\s+/).filter(Boolean);
      const hits=cards.filter(card=>{
        const tags=(card.dataset.topics||'').split(' '),kinds=(card.dataset.kinds||'').split(' '),roles=(card.dataset.roles||'').split(' ').filter(Boolean);
        return selected.every(tag=>tags.includes(tag))&&(!kind.value||(care?(!roles.length||roles.includes(kind.value)):kinds.includes(kind.value)))&&words.every(word=>fold(card.textContent).includes(word));
      }).sort((a,b)=>sort.value==='az'?a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent):order.get(a)-order.get(b));
      cards.forEach(card=>{card.hidden=true;});hits.forEach((card,i)=>{box.append(card);card.hidden=i>=limit;});
      status.textContent=hits.length+' '+(care?(hits.length===1?'guide':'guides'):(hits.length===1?'story or note':'stories & notes'))+(hits.length>limit?' · showing '+limit:'');empty.hidden=!!hits.length;more.hidden=hits.length<=limit;
      if(mode){const params=new URLSearchParams();if(q.value.trim())params.set('q',q.value.trim());if(kind.value)params.set(care?'role':'kind',kind.value);selected.forEach(tag=>params.append('topic',tag));if(sort.value!=='featured')params.set('sort',sort.value);history[mode==='push'?'pushState':'replaceState']({},'',location.pathname+(params.size?'?'+params:'')+'#'+collection.id);}
      return hits;
    }
    form.addEventListener('submit',event=>{event.preventDefault();limit=pageSize;apply('push');});
    q.addEventListener('input',()=>{limit=pageSize;apply('replace');});
    [kind,sort,...topics].forEach(input=>input.addEventListener('change',()=>{limit=pageSize;apply('push');}));
    function clear(){form.reset();q.focus();}
    form.addEventListener('reset',event=>{event.preventDefault();q.value='';kind.value='';sort.value='featured';topics.forEach(input=>{input.checked=false;});limit=pageSize;apply('push');});
    collection.querySelector('[data-collection-clear]').addEventListener('click',clear);
    more.addEventListener('click',()=>{const previous=limit;limit+=pageSize;const hits=apply();hits[previous]?.querySelector('h3 a')?.focus();});
    window.addEventListener('popstate',()=>{readURL();apply();});readURL();apply();
  });
})();
