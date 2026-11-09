'use strict';
// Public, client-only presentation: consent-aware analytics is managed separately.
// All commercial amounts are fetched read-only from the approved India catalogue.
(()=>{
 const root=document.documentElement;
 const lang=root.lang==='hi'?'hi':root.lang==='hi-Latn'?'hinglish':'en';
 const langDrop=document.getElementById('ftLangSelect');
 if(langDrop){
  document.addEventListener('pointerdown',event=>{
   if(langDrop.open&&!langDrop.contains(event.target))langDrop.open=false;
  });
  document.addEventListener('keydown',event=>{
   if(event.key==='Escape'&&langDrop.open){langDrop.open=false;langDrop.querySelector('summary')?.focus();}
  });
 }
 const menu=document.getElementById('ftMenu');
 const nav=document.getElementById('ftNav');
 if(menu&&nav){
  const close=()=>{nav.dataset.open='false';menu.setAttribute('aria-expanded','false');};
  menu.addEventListener('click',()=>{
   const open=nav.dataset.open!=='true';nav.dataset.open=String(open);menu.setAttribute('aria-expanded',String(open));
  });
  nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close();});
  window.addEventListener('resize',()=>{if(innerWidth>850)close();});
 }
 const text={
  en:{start:'Basic starting price',unavailable:'View verified INR pricing in store',finder:'Suggested service',details:'Explore packages'},
  hi:{start:'मूल पैकेज की शुरुआती कीमत',unavailable:'स्टोर में रुपये की स्वीकृत कीमत देखें',finder:'आपके लिए सुझाई गई सेवा',details:'पैकेज देखें'},
  hinglish:{start:'Basic package ki starting price',unavailable:'Store mein verified INR price dekhein',finder:'Aapke liye suggested service',details:'Packages Dekhein'}
 }[lang];
 const finderButtons=[...document.querySelectorAll('.ft-finder-buttons [data-find]')];
 const target=document.getElementById('ftFinderTitle');
 const desc=document.getElementById('ftFinderDesc');
 const link=document.getElementById('ftFinderLink');
 const hint=document.getElementById('ftFinderEyebrow');
 const localeUrl=new URL('https://portal.freshtiqautomation.com/store');
 localeUrl.searchParams.set('market','India');localeUrl.searchParams.set('lang',lang);
 const match=q=>{const el=document.querySelector('.ft-service[data-service="'+q+'"]');return el};
 function select(key){
  const card=match(key);if(!card)return;
  const name=card.querySelector('h3')?.textContent.trim();
  const summary=card.querySelector('p')?.textContent.trim();
  if(!name||!summary)return;
  finderButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.find===key)));
  if(target)target.textContent=name;
  if(desc)desc.textContent=summary;
  if(hint)hint.textContent=text.finder;
  const u=new URL(localeUrl);u.searchParams.set('service',key);
  if(link){link.href=u.toString();link.textContent=text.details+' →';}
 }
 finderButtons.forEach(b=>b.addEventListener('click',()=>select(b.dataset.find)));
 select('website');
 // Never infer prices from a phone location, guessed FX or prior archived products.
 const priceEls=[...document.querySelectorAll('[data-live-price]')];
 if(priceEls.length){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),7500);
  fetch('https://portal.freshtiqautomation.com/api/public/commercial-pricing',{cache:'no-store',mode:'cors',credentials:'omit',signal:controller.signal})
   .then(r=>{if(!r.ok)throw Error('unavailable');return r.json()})
   .then(data=>{
    if(Object.keys(data?.products||{}).length!==27||!data?.regions?.India)return;
    const approved=new Set(priceEls.map(x=>x.dataset.livePrice));
    if(approved.size!==8)return;
    for(const el of priceEls){
     const amount=Number(data.products[el.dataset.livePrice]?.regional_prices?.India?.standard);
     if(Number.isSafeInteger(amount)&&amount>0&&amount<1e9){
      el.replaceChildren();
      const caption=document.createElement('span');caption.textContent=text.start;
      const value=document.createElement('strong');value.textContent='₹'+amount.toLocaleString('en-IN');
      el.append(caption,value);
     }else{
      el.textContent=text.unavailable;
     }
    }
   }).catch(()=>{for(const el of priceEls)el.textContent=text.unavailable;})
   .finally(()=>clearTimeout(timer));
 }
})();
