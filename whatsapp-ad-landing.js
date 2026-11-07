'use strict';
// Marketing landing: no redirect, no payments, no automatic WhatsApp messages.
(()=>{
 const path=location.pathname;
 if(path!=='/services/whatsapp-automation.html')return;
 const params=new URLSearchParams(location.search);
 const permit=['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','gbraid','wbraid'];
 for(const el of document.querySelectorAll('[data-ftq-carry-utm]')){
  const url=new URL(el.getAttribute('href'),location.origin);
  for(const field of permit){
   const value=params.get(field);
   if(value&&value.length<=150&&/^[a-zA-Z0-9._%+ -]+$/.test(value))url.searchParams.set(field,value);
  }
  // Never remove an already-present purpose-specific service selector.
  el.href=url.toString();
 }
 const priceEl=document.getElementById('ftqWhatsappPrice');
 if(priceEl){
  const timeout=new AbortController();
  const timer=setTimeout(()=>timeout.abort(),8000);
  fetch('https://portal.freshtiqautomation.com/api/public/commercial-pricing',{cache:'no-store',credentials:'omit',signal:timeout.signal})
    .then(r=>{if(!r.ok)throw Error('Not available');return r.json()})
    .then(d=>{
      const item=d?.products?.whatsapp_ai_sales_bot;
      if(Object.keys(d?.products||{}).length!==8||!d?.regions?.India||!item)return;
      const n=Number(item.regional_prices?.India?.standard);
      if(Number.isSafeInteger(n)&&n>0&&n<10000000){priceEl.textContent='₹'+n.toLocaleString('en-IN')}
      else priceEl.textContent='See verified INR store pricing';
    }).catch(()=>{priceEl.textContent='See verified INR store pricing'})
    .finally(()=>clearTimeout(timer));
 }
})();
