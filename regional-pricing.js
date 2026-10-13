(()=>{'use strict';
/* No FX conversion: these are independent fixed market rate cards in the
   canonical published commercial-pricing.json read by the portal and bot. */
const MAP={USA:{region:'USA',label:'United States',currency:'USD'},
 UAE:{region:'UAE',label:'United Arab Emirates',currency:'AED'},
 SAUDI:{region:'Saudi Arabia',label:'Saudi Arabia',currency:'SAR'},
 INDIA:{region:'India',label:'India',currency:'INR'}};
const TIERS=['standard','professional','premium'];
const grids=[...document.querySelectorAll('[data-market]')];
const tierButtons=[...document.querySelectorAll('[data-tier]')];
const status=document.getElementById('catalog-status');
const marketName=document.getElementById('market-label');
const tbody=document.getElementById('all-services');
let country='INDIA',level=1,catalog=null;
try{
 const q=new URLSearchParams(location.search).get('market')||'';
 const lookup={US:'USA',USA:'USA',AE:'UAE',UAE:'UAE',SA:'SAUDI',SAUDI:'SAUDI',IN:'INDIA',INDIA:'INDIA'};
 if(lookup[q.toUpperCase()]) country=lookup[q.toUpperCase()];
 else {
  const saved=localStorage.getItem('freshtiq_chosen_pricing_market');
  if(Object.prototype.hasOwnProperty.call(MAP,saved))country=saved;
 }
}catch(_){}
const fmt=(n,region)=>new Intl.NumberFormat(region==='India'?'en-IN':'en-US',{
 style:'currency',currency:Object.values(MAP).find(m=>m.region===region)?.currency||'INR',
 maximumFractionDigits:0}).format(n);
function amount(product,region,tier){return Number((product.regional_prices||{})[region]?.[tier]||0)}
function showUnavailable(){
 status.textContent='Prices could not be verified. Please request a free written quote; no estimated currency conversion will be shown.';
 for(const el of document.querySelectorAll('[id^="amount-"],[id^="bundle-"]'))el.textContent='Request quote';
 tbody.replaceChildren();
}
function render(){
 if(!catalog)return showUnavailable();
 const reg=MAP[country].region, tier=TIERS[level];
 marketName.textContent=MAP[country].label+' · '+MAP[country].currency;
 for(const [key,prod]of Object.entries(catalog.products)){
  const el=document.getElementById('amount-'+key);
  if(el){
   const n=amount(prod,reg,tier);
   el.textContent=n>0?fmt(n,reg)+(prod.billing_unit||''):'Request quote';
  }
 }
 for(const [key,bundle]of Object.entries(catalog.regional_bundles||{})){
  const el=document.getElementById('bundle-'+key);
  if(!el)continue;
  const n=Number((bundle.market_prices||{})[reg]||0),
   separately=Number((bundle.standalone_totals||{})[reg]||0);
  el.textContent=n>0&&separately>n?fmt(n,reg):'Request quote';
  const note=document.getElementById('bundle-save-'+key);
  if(note)note.textContent=n>0&&separately>n?
   'Purchased separately '+fmt(separately,reg)+' · bundled setup '+fmt(n,reg)+
   ' · save '+fmt(separately-n,reg):'Scope confirmed in writing';
 }
 tbody.replaceChildren();
 for(const [key,prod]of Object.entries(catalog.products)){
  const tr=document.createElement('tr');
  const title=document.createElement('td');
  title.textContent=String(prod.name||key)+' · '+(/month/i.test(prod.billing_unit||'')?'monthly':'one-time setup');
  tr.appendChild(title);
  for(let i=0;i<TIERS.length;i++){
   const td=document.createElement('td'),value=amount(prod,reg,TIERS[i]);
   td.textContent=value>0?fmt(value,reg)+(prod.billing_unit||''):'Request quote';
   if(i===level)td.setAttribute('aria-current','true');
   tr.appendChild(td);
  }
  tbody.appendChild(tr);
 }
 for(const b of grids){
  const active=b.dataset.market===country;b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;
 }
 for(const b of tierButtons)b.setAttribute('aria-pressed',String(Number(b.dataset.tier)===level));
 status.textContent='Published fixed prices for '+MAP[country].label+' • one-time and monthly fees are labelled. No currency converter is used.';
}
for(const b of grids){
 b.addEventListener('click',()=>{
  country=b.dataset.market;
  try{localStorage.setItem('freshtiq_chosen_pricing_market',country)}catch(_){}
  render();
 });
 b.addEventListener('keydown',e=>{
  if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;
  e.preventDefault();
  const at=grids.indexOf(b),index=e.key==='Home'?0:e.key==='End'?grids.length-1:
   (at+(e.key==='ArrowRight'?1:-1)+grids.length)%grids.length;
  grids[index].focus();grids[index].click();
 });
}
for(const b of tierButtons)b.addEventListener('click',()=>{level=Number(b.dataset.tier)||0;render()});
fetch('/commercial-pricing.json?v=20261013fourmarkets1',{cache:'no-store',signal:AbortSignal.timeout(8000)})
 .then(r=>{if(!r.ok)throw Error('price file unavailable');return r.json()})
 .then(policy=>{
  if(policy.version!=='2026-10-13-four-market-fixed-v2' ||
    !policy.products||Object.keys(policy.products).length!==25 ||
    !policy.regions||!MAP.USA||!policy.regional_bundles)throw Error('rate-card not verified');
  for(const x of Object.values(policy.products)){
   for(const v of Object.values(MAP)){
    for(const tier of TIERS)if(!(amount(x,v.region,tier)>0))throw Error('Incomplete pricing');
   }
  }
  catalog=policy;render();
 }).catch(()=>showUnavailable());
})();
