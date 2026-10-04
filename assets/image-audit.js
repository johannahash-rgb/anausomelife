/* Editorial image guard: photography is reserved for real camera-roll images supplied by the family.
   Illustrations remain welcome, but should be presented as illustrations rather than simulated documentary photography. */
(()=> {
  'use strict';
  const REAL_PHOTOS=new Set([
    '/assets/book-barn-ct-clean.jpg','/assets/book-barn-ct.jpg',
    '/assets/orchard-afternoon-clean.jpg','/assets/orchard-afternoon.jpg',
    '/assets/york-maine-clean.jpg','/assets/york-maine.jpg',
    '/assets/aquarium-visit.webp',
    '/assets/family-outings/fort-mcclary-waterfront.webp',
    '/assets/family-outings/lexington-ice-cream-family.webp',
    '/assets/family-outings/llbean-freeport-games.webp',
    '/assets/family-outings/wells-beach-family.webp'
  ]);
  const ILLUSTRATION_PARTS=[
    '/venue-illustrations/','/navigation-watercolors/','/editorial/','/favorites/',
    '/event-sketches/','/card-studio/','/story-illustrations/','/weekend-',
    '/catalog-','/gift-','/illustrated-'
  ];
  const BRAND_PARTS=['favicon','logo','emblem','icon','sprite'];
  document.querySelectorAll('img[src]').forEach(img=>{
    let path='';
    try{path=new URL(img.getAttribute('src'),location.origin).pathname}catch(_){path=img.getAttribute('src')||''}
    if(REAL_PHOTOS.has(path)){img.dataset.aalImage='family-photo';return}
    if(ILLUSTRATION_PARTS.some(p=>path.includes(p))){img.dataset.aalImage='illustration';return}
    if(BRAND_PARTS.some(p=>path.toLowerCase().includes(p))){img.dataset.aalImage='brand';return}
    img.dataset.aalImage='unverified';
    if(location.hostname!=='localhost') console.warn('[An AUsome Life] Unverified image asset — confirm it is an uploaded real photo or explicitly presented illustration:',path);
  });
})();