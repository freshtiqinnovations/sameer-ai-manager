'use strict';(()=>{const input=document.getElementById('serviceSearch');const cards=[...document.querySelectorAll('#serviceCards .card')];const none=document.getElementById('noResults');if(!input)return;input.addEventListener('input',()=>{const q=input.value.toLocaleLowerCase().trim();let visible=0;for(const card of cards){const match=!q||((card.dataset.match||'')+' '+card.textContent).toLocaleLowerCase().includes(q);card.hidden=!match;if(match)visible++}none.hidden=visible>0;});})();
/* Preserve non-sensitive ad source parameters across the website → private quote-shop hop.
   Do not send contact details or tracking tokens to analytics. */
(()=>{
 const params=new URLSearchParams(location.search);
 const allowed=['utm_source','utm_medium','utm_campaign','utm_content'];
 const carry={};
 for(const name of allowed){
   const value=(params.get(name)||'').trim();
   if(/^[A-Za-z0-9_.-]{1,80}$/.test(value))carry[name]=value;
 }
 for(const link of document.querySelectorAll('a[href*="portal.freshtiqautomation.com/store"]')){
   try{
     const u=new URL(link.href);
     if(u.hostname!=='portal.freshtiqautomation.com'||u.pathname!=='/store')continue;
     for(const [k,v] of Object.entries(carry))u.searchParams.set(k,v);
     link.href=u.href;
     link.addEventListener('click',()=>{
       try{window.gtag?.('event','select_content',{content_type:'service_shop',item_id:'freshtiq_services'});}catch(_){}
     });
   }catch(_){}
 }
 for(const link of document.querySelectorAll('a[href*="wa.me/"]')){
   link.addEventListener('click',()=>{
     try{window.gtag?.('event','contact',{method:'whatsapp'});}catch(_){}
   });
 }
 document.getElementById('ftqPrivacyChoice')?.addEventListener('click',e=>{
   e.preventDefault();
   if(typeof window.FreshtiqCookieSettings==='function')window.FreshtiqCookieSettings();
 });
})();
