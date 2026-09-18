(function(){
  'use strict';
  const root=document.getElementById('currency-converter'); if(!root) return;
  const amount=document.getElementById('fxAmount'), from=document.getElementById('fxFrom'), to=document.getElementById('fxTo'), out=document.getElementById('fxOutput'), meta=document.getElementById('fxMeta'), swap=document.getElementById('fxSwap');
  const currencies=[
    ['INR','🇮🇳 Indian Rupee'],['SAR','🇸🇦 Saudi Riyal'],['AED','🇦🇪 UAE Dirham'],['USD','🇺🇸 US Dollar'],['EUR','🇪🇺 Euro'],['GBP','🇬🇧 British Pound'],['CAD','🇨🇦 Canadian Dollar'],['AUD','🇦🇺 Australian Dollar'],['QAR','🇶🇦 Qatari Riyal'],['KWD','🇰🇼 Kuwaiti Dinar'],['BHD','🇧🇭 Bahraini Dinar'],['OMR','🇴🇲 Omani Rial']
  ];
  const symbols={INR:'₹',SAR:'SAR ',AED:'AED ',USD:'$',EUR:'€',GBP:'£',CAD:'C$',AUD:'A$',QAR:'QAR ',KWD:'KWD ',BHD:'BHD ',OMR:'OMR '};
  currencies.forEach(([code,name])=>{for(const el of [from,to]){const o=document.createElement('option');o.value=code;o.textContent=name+' ('+code+')';el.appendChild(o)}});
  const savedTo=localStorage.getItem('freshtiq_fx_to'); from.value='USD'; to.value=savedTo&&currencies.some(x=>x[0]===savedTo)?savedTo:'SAR';
  let timer=null, controller=null;
  function format(code,value){try{return new Intl.NumberFormat(undefined,{style:'currency',currency:code,maximumFractionDigits:['KWD','BHD','OMR'].includes(code)?3:2}).format(value)}catch(_){return (symbols[code]||code+' ')+Number(value).toLocaleString(undefined,{maximumFractionDigits:2})}}
  async function convert(){
    const a=Number(amount.value), f=from.value, t=to.value;
    if(!Number.isFinite(a)||a<=0){out.innerHTML='<div class="fx-result-main">—</div><div class="fx-rate fx-error">Enter a valid amount.</div>';return;}
    if(f===t){out.innerHTML='<div class="fx-result-main">'+format(t,a)+'</div><div class="fx-rate">1 '+f+' = 1 '+t+'</div>';return;}
    if(controller) controller.abort(); controller=new AbortController();
    out.classList.add('fx-loading'); out.innerHTML='<div class="fx-result-main">…</div><div class="fx-rate">Checking live rate…</div>';
    try{
      const u='https://portal.freshtiqautomation.com/api/fx?from='+encodeURIComponent(f)+'&to='+encodeURIComponent(t)+'&amount='+encodeURIComponent(a);
      const r=await fetch(u,{signal:controller.signal,headers:{'Accept':'application/json'}}); const d=await r.json(); if(!r.ok||!d.success) throw new Error(d.error||'Rate unavailable');
      out.innerHTML='<div class="fx-result-main">'+format(t,d.converted)+'</div><div class="fx-rate">1 '+f+' ≈ '+Number(d.rate).toLocaleString(undefined,{maximumFractionDigits:6})+' '+t+'</div>';
      const stamp=d.rate_date?new Date(d.rate_date).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'}):'latest available daily rate';
      meta.innerHTML='Rate updated: <strong>'+stamp+'</strong>. Indicative conversion only; final project scope, taxes and payment terms are confirmed in the written proposal. <a href="https://www.exchangerate-api.com" target="_blank" rel="noopener">Rates by Exchange Rate API</a>.'+(d.warning?' <span class="fx-error">'+d.warning+'</span>':'');
      localStorage.setItem('freshtiq_fx_to',t);
      try{if(window.gtag) gtag('event','currency_convert',{from_currency:f,to_currency:t});}catch(_){}
    }catch(e){if(e.name==='AbortError')return;out.innerHTML='<div class="fx-result-main">—</div><div class="fx-rate fx-error">Live rate is temporarily unavailable.</div>';meta.textContent='Your published INR, SAR and AED package tables below remain available. Final project pricing is confirmed in writing.';}
    finally{out.classList.remove('fx-loading')}
  }
  function schedule(){clearTimeout(timer);timer=setTimeout(convert,250)}
  amount.addEventListener('input',schedule); from.addEventListener('change',convert); to.addEventListener('change',convert);
  swap.addEventListener('click',()=>{const x=from.value;from.value=to.value;to.value=x;convert()});
  document.querySelectorAll('[data-fx]').forEach(b=>b.addEventListener('click',()=>{to.value=b.dataset.fx;if(to.value===from.value)from.value=to.value==='USD'?'INR':'USD';convert()}));
  convert();
})();
