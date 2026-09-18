(function(){
  'use strict';
  const KEY='ftq_analytics_consent_v1', ID='G-Y80ZGMYR1Y';
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};
  let loaded=false;
  function loadAnalytics(){
    if(loaded)return; loaded=true;
    window.gtag('consent','update',{analytics_storage:'granted'});
    const s=document.createElement('script'); s.async=true; s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(ID); document.head.appendChild(s);
    window.gtag('js',new Date()); window.gtag('config',ID,{anonymize_ip:true});
  }
  function setChoice(v){try{localStorage.setItem(KEY,v)}catch(_){}; if(v==='granted')loadAnalytics(); removeBanner();}
  function removeBanner(){document.getElementById('ftq-consent')?.remove()}
  window.FreshtiqCookieSettings=function(){try{localStorage.removeItem(KEY)}catch(_){};showBanner(true)};
  function showBanner(force){
    if(!force){try{const v=localStorage.getItem(KEY);if(v==='granted'){loadAnalytics();return}if(v==='denied')return}catch(_){}}
    if(document.getElementById('ftq-consent'))return;
    const d=document.createElement('div');d.id='ftq-consent';d.setAttribute('role','dialog');d.setAttribute('aria-label','Analytics preference');
    d.innerHTML='<div class="ftq-consent-copy"><strong>Privacy choice</strong><span>Essential site functions always work. Optional analytics helps us understand visits and improve the website.</span><a href="/privacy.html#analytics">Privacy details</a></div><div class="ftq-consent-actions"><button type="button" data-choice="denied">Essential only</button><button type="button" class="primary" data-choice="granted">Allow analytics</button></div>';
    d.addEventListener('click',e=>{const b=e.target.closest('[data-choice]');if(b)setChoice(b.dataset.choice)});document.body.appendChild(d);
  }
  window.gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>showBanner(false),{once:true});else showBanner(false);
})();
