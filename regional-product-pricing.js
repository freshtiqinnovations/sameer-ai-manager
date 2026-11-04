(()=>{'use strict';
/* Product pages use the same approved commercial price data as the premium portal.
   Never derive AED/SAR prices or treat a starting estimate as a checkout amount. */
const nodes=[...document.querySelectorAll('.ftq-regional-product-price[data-product]')];
if(!nodes.length)return;
const catalogUrl='https://portal.freshtiqautomation.com/api/public/commercial-pricing';
const storeUrl='https://portal.freshtiqautomation.com/store';
function addLink(el,key){
 const link=document.createElement('a');
 const url=new URL(storeUrl);
 url.searchParams.set('service',key);
 link.href=url.toString();
 link.textContent='View current packages in the premium store';
 link.style.cssText='display:inline-block;margin-top:7px;font-weight:750;text-decoration:underline';
 el.appendChild(document.createElement('br'));
 el.appendChild(link);
}
function unavailable(el,key){
 el.replaceChildren(document.createTextNode('Live prices are temporarily unavailable. Please request a current written quotation.'));
 addLink(el,key);
}
function fmt(amount,currency,locale){
 return new Intl.NumberFormat(locale,{style:'currency',currency,maximumFractionDigits:0}).format(amount);
}
function show(el,key,catalog){
 const product=catalog.products[key];
 const india=Number(product?.regional_prices?.India?.standard);
 const usa=Number(product?.regional_prices?.USA?.standard);
 if(!product || product.internal_only || !Number.isFinite(india) || india<=0 || !Number.isFinite(usa) || usa<=0){
  unavailable(el,key);return;
 }
 const date=String(catalog.effective_date||'');
 const line='Basic starting estimate ('+date+'): India '+fmt(india,'INR','en-IN')+' · USA '+fmt(usa,'USD','en-US')+'.';
 const small=document.createElement('small');
 small.textContent='Other countries including UAE and Saudi Arabia: request a written quote. Taxes, third-party charges and final scope are confirmed before payment.';
 small.style.cssText='display:block;margin-top:5px;line-height:1.5;opacity:.85';
 el.replaceChildren(document.createTextNode(line),small);
 addLink(el,key);
}
const controller=new AbortController();
const timer=setTimeout(()=>controller.abort(),8500);
fetch(catalogUrl,{mode:'cors',credentials:'omit',cache:'no-store',signal:controller.signal})
 .then(response=>{if(!response.ok)throw new Error('Pricing API HTTP '+response.status);return response.json()})
 .then(data=>{
   if(!data||!data.products||typeof data.products!=='object'||!data.regions||!data.effective_date||Object.keys(data.products).length<27)throw new Error('Incomplete published price catalog');
   for(const el of nodes){
     const key=String(el.getAttribute('data-product')||'');
     if(!/^[a-z][a-z0-9_]{1,65}$/.test(key)){el.textContent='Please request a written quote.';continue;}
     show(el,key,data);
   }
 })
 .catch(()=>{
   for(const el of nodes){
     const key=String(el.getAttribute('data-product')||'');
     if(/^[a-z][a-z0-9_]{1,65}$/.test(key))unavailable(el,key);
     else el.textContent='Please request a written quote.';
   }
 }).finally(()=>clearTimeout(timer));
})();
