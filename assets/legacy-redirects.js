/* Recover known old page addresses; unknown addresses retain the useful 404. */
(()=>{'use strict';
  const normalize=path=>path.replace(/\/+$/,'').replace(/\/index\.html$/,'').replace(/\.html$/,'')||'/';
  const resolve=(path,data)=>{
    const key=normalize(path);
    if(Object.prototype.hasOwnProperty.call(data.aliases,key))return data.aliases[key];
    return data.pages.find(page=>normalize(page)===key)||null;
  };
  fetch('/data/legacy-routes.json?v=20261005',{credentials:'same-origin'})
    .then(response=>{if(!response.ok)throw Error('Routes unavailable');return response.json()})
    .then(data=>{
      const target=resolve(window.location.pathname,data);if(!target)return;
      const destination=new URL(target,window.location.origin);
      if(destination.origin!==window.location.origin)return;
      destination.search=window.location.search;
      // Section-specific legacy URLs use their mapped section; other links keep the visitor's anchor.
      if(!destination.hash)destination.hash=window.location.hash;
      if(destination.href!==window.location.href)window.location.replace(destination.href);
    }).catch(()=>{});
})();
