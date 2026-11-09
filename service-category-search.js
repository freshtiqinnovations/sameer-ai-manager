'use strict';
/**
 * Compact 27-service finder used by public homepages and services page.
 * Native details/summary means browsing categories works without JS.
 * This controller only filters existing cards and opens search matches:
 * prices, product URLs, checkout logic, tracking and consent untouched.
 */
(() => {
 const homeSearch=document.getElementById('ftServiceSearch');
 const fullSearch=document.getElementById('svcSearch');
 const search=homeSearch||fullSearch;
 const root=document.getElementById(homeSearch?'serviceCards':'svcGrid');
 if(!root||!search)return;
 const home=Boolean(homeSearch);
 const selector=home?'.ft-service':'.svc-card';
 const groups=[...root.querySelectorAll(home?'.ft-category-group':'.svc-category-group')];
 const cards=[...root.querySelectorAll(selector)];
 const count=document.getElementById(home?'ftCatalogResultCount':'svcResultCount');
 const empty=document.getElementById(home?'ftServiceNoResults':'svcNoResults');
 const lang=document.documentElement.lang;
 if(groups.length!==6||cards.length!==27||!count||!empty)return;
 const text=lang==='hi'
  ? {all:'6 श्रेणियों में 27 सेवाएँ। श्रेणी खोलें या सेवा खोजें।',matches:' सेवाएँ मिलीं। संबंधित श्रेणी खुली है।',none:'कोई सेवा नहीं मिली। दूसरा शब्द डालें।'}
  : lang==='hi-Latn'
  ? {all:'6 categories mein 27 services. Category kholein ya direct search karein.',matches:' matching services. Category khul gayi hai.',none:'Koi matching service nahi. Dusra keyword try karein.'}
  : {all:'27 services in 6 categories. Expand a category or search.',matches:' matching services. Matching categories are open.',none:'No matching service. Try another keyword.'};
 let searching=false;
 const update=()=>{
  const query=search.value.trim().toLocaleLowerCase().slice(0,100);
  const wasSearching=searching;searching=Boolean(query);
  let matching=0;
  for(const group of groups){
   let groupMatches=0;
   for(const card of group.querySelectorAll(selector)){
    const hay=(home?card.dataset.match:card.dataset.search)||card.textContent||'';
    const match=!searching||hay.toLocaleLowerCase().includes(query);
    card.hidden=!match;
    if(match){matching++;groupMatches++;}
   }
   group.hidden=searching&&groupMatches===0;
   if(searching)group.open=groupMatches>0;
   else if(wasSearching)group.open=false;
  }
  count.textContent=searching?matching+text.matches:text.all;
  empty.hidden=matching>0;
  if(!matching)empty.textContent=text.none;
 };
 for(const group of groups){
  group.addEventListener('toggle',()=>{
   if(!group.open||searching)return;
   for(const other of groups)if(other!==group&&other.open)other.open=false;
  });
 }
 search.addEventListener('input',update);
 if(fullSearch){
  const params=new URLSearchParams(location.search);
  const fromUrl=(params.get('q')||'').trim().slice(0,100);
  if(fromUrl&&!search.value)search.value=fromUrl;
 }
 update();
})();
