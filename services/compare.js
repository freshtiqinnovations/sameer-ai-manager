(()=>{'use strict';
const $=id=>document.getElementById(id);
const MARKET_CURRENCY={India:'INR',USA:'USD','United Kingdom':'GBP',Eurozone:'EUR',Australia:'AUD',Denmark:'DKK'};
const TIERS=[['standard','Basic'],['professional','Pro'],['premium','Elite']];
const params=new URLSearchParams(location.search);
let catalog=null,selected='';
const status=t=>{$('status').textContent=t};
function text(el,value){$(el).textContent=String(value)}
function setFeatures(target,arr){
 const list=$(target);list.replaceChildren();
 for(const item of arr||[]){const li=document.createElement('li');li.textContent=item;list.append(li)}
}
function urlFor(key,tier,market){
 return 'https://portal.freshtiqautomation.com/store?'+new URLSearchParams({service:key,market,tier}).toString()+'#services'
}
function draw(){
 if(!catalog)return;
 const product=catalog.products[selected];if(!product)return;
 const market=$('countrySelect').value;
 text('productTitle',product.name);
 text('productSummary','Three independently scoped packages. Illustrations and the interactive demo let you explore the customer journey before requesting a final quotation.');
 status('Verified catalogue record · '+Object.values(catalog.products).filter(x=>!x.internal_only).length+' published Freshtiq services');
 const imgbase='/images/service-illustrations/';
 for(let i=1;i<=3;i++){
 const img=$('image'+i);
 img.src=imgbase+encodeURIComponent(selected)+'-'+i+'.svg';
 img.alt=product.name+' — illustrative workflow visual '+i+' of 3';
 }
 for(const [code,label] of TIERS){
 const suffix=code==='standard'?'Basic':code==='professional'?'Pro':'Elite';
 const rate=Number(product.regional_prices?.[market]?.[code]);
 const isOther=market==='other'||!Object.hasOwn(MARKET_CURRENCY,market);
 const labelRate=!isOther&&Number.isFinite(rate)&&rate>0
   ?new Intl.NumberFormat(market==='India'?'en-IN':'en-US',{style:'currency',currency:MARKET_CURRENCY[market],maximumFractionDigits:0}).format(rate)
   :'Custom written quote';
 text('price'+suffix,labelRate+(product.billing_unit==='/month'&&!isOther?' / month':''));
 setFeatures('features'+suffix,product.features?.[code]||[]);
 const btn=$('buy'+suffix);
 if(isOther){
   btn.href='https://wa.me/918381848389?text='+encodeURIComponent('Hello Freshtiq, I need a country-specific '+label+' quote for '+product.name+'. Please confirm requirements and pricing.');
   btn.textContent='Request '+label+' custom quote →';
 }else{
   btn.href=urlFor(selected,code,market);
   btn.textContent='Choose '+label+' & request quote →';
 }
 }
 const demoBase=selected==='real_estate_ai'
  ?'https://freshtiqautomation.com/demo/real-estate-workflow.html'
  :'https://portal.freshtiqautomation.com/service-demo?'+new URLSearchParams({service:selected,market:market==='other'?'India':market,tier:'standard'}).toString();
 $('demoLink').href=demoBase;
 $('whatsappLink').href='https://wa.me/918381848389?text='+encodeURIComponent('Hello Freshtiq, I am interested in '+product.name+'. My business market: '+(market==='other'?'Other country':market)+'. Please help me choose a package.');
 $('chargeNote').textContent=(market==='other'
   ?'Saudi Arabia, UAE and other markets: country-specific scope, compliance, tax and payment arrangements must be quoted and approved separately.'
   :'These are fixed published market starting prices, not live exchange-rate conversions. ') +
   (selected==='real_estate_ai'
   ?'Real Estate setup fee is before applicable GST and external provider charges.'
   :'Your final store estimate/quote specifies whether applicable taxes are included and any external API or messaging costs.');
 const suffix=selected==='real_estate_ai'?' Real Estate':'';document.title=product.name+' Plans & Demo | Freshtiq Automation';
 history.replaceState(null,'','/services/compare.html?'+new URLSearchParams({service:selected,market}).toString());
}
async function init(){
 try{
  const res=await fetch('/commercial-pricing.json',{cache:'no-store'});
  if(!res.ok)throw Error('Product catalogue unavailable');
  catalog=await res.json();
  const all=Object.entries(catalog.products||{}).filter(([key,p])=>!p.internal_only&&p.regional_prices&&p.features);
  if(all.length!==27)throw Error('Catalogue review required: '+all.length+' published services');
  const select=$('serviceSelect');select.replaceChildren();
  for(const [key,p] of all){const opt=document.createElement('option');opt.value=key;opt.textContent=p.name;select.append(opt)}
  selected=all.some(([key])=>key===params.get('service'))?params.get('service'):'whatsapp_automation';
  select.value=selected;$('countrySelect').value=Object.hasOwn(MARKET_CURRENCY,params.get('market'))?params.get('market'):'India';
  select.addEventListener('change',()=>{selected=select.value;draw()});
  $('countrySelect').addEventListener('change',draw);
  draw();
 }catch(e){status('Could not verify current catalogue: '+String(e.message).slice(0,110));$('serviceSelect').disabled=true;console.error('[Freshtiq Service Explorer]',e.message)}
}
init();
})();
