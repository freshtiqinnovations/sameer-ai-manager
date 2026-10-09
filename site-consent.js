(function(){
  'use strict';
  const KEY='ftq_analytics_consent_v1', ID='G-Y80ZGMYR1Y';
  const ADS_KEY='ftq_openai_measurement_consent_v1';
  function adsEnabled(){return !!(window.FreshtiqOpenAIMeasurement && window.FreshtiqOpenAIMeasurement.enabled)}
  function storedAdsChoice(){try{return localStorage.getItem(ADS_KEY)}catch(_){return null}}
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};

  // Advanced consent mode: Google tag loads with storage denied until the visitor chooses.
  // This preserves the user's privacy choice while allowing privacy-preserving measurement pings.
  window.gtag('consent','default',{
    analytics_storage:'denied',
    ad_storage:'denied',
    ad_user_data:'denied',
    ad_personalization:'denied',
    wait_for_update:500
  });
  window.gtag('set','ads_data_redaction',true);
  window.gtag('set','url_passthrough',true);

  let loaded=false;
  function loadGoogleTag(){
    if(loaded)return; loaded=true;
    const s=document.createElement('script');
    s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(ID);
    document.head.appendChild(s);
    window.gtag('js',new Date());
    window.gtag('config',ID,{anonymize_ip:true,send_page_view:true});
  }
  function applyChoice(v){
    const granted=v==='granted';
    window.gtag('consent','update',{
      analytics_storage:granted?'granted':'denied',
      ad_storage:granted?'granted':'denied',
      ad_user_data:granted?'granted':'denied',
      ad_personalization:'denied'
    });
  }
  function setChoice(v){
    const analytics=v==='granted'||v==='measurement';
    const choice=analytics?'granted':'denied';
    try{localStorage.setItem(KEY,choice)}catch(_){}
    applyChoice(choice);
    if(adsEnabled()) window.FreshtiqOpenAIMeasurement.setConsent(v==='measurement');
    removeBanner();
  }
  function removeBanner(){document.getElementById('ftq-consent')?.remove()}
  window.FreshtiqCookieSettings=function(){showBanner(true)};

  function showBanner(force){
    if(!force){
      try{
        const v=localStorage.getItem(KEY);
        if(v==='granted'||v==='denied'){
          applyChoice(v);
          if(!adsEnabled()||storedAdsChoice()==='granted'||storedAdsChoice()==='denied')return;
        }
      }catch(_){}
    }
    if(document.getElementById('ftq-consent'))return;
    const d=document.createElement('div');
    d.id='ftq-consent';
    d.setAttribute('role','dialog');
    d.setAttribute('aria-label','Privacy preference');
    if(adsEnabled()) d.classList.add('ftq-consent-measurement');
    const copy=adsEnabled()?'Essential site functions always work. Optional analytics measures visits. Separate OpenAI ad measurement connects successful enquiries to our ads.':'Essential site functions always work. Optional analytics helps us understand visits and improve the website.';
    const buttons=adsEnabled()?'<button type="button" data-choice="denied">Essential only</button><button type="button" data-choice="granted">Analytics only</button><button type="button" class="primary" data-choice="measurement">Allow analytics + ad measurement</button>':'<button type="button" data-choice="denied">Essential only</button><button type="button" class="primary" data-choice="granted">Allow analytics</button>';
    const locale=(document.documentElement.lang||'en').toLowerCase().slice(0,2);
    const ui={
      ar:{title:'خيارات الخصوصية',copy:'تعمل الوظائف الأساسية دائماً. التحليلات اختيارية وتساعدنا في تحسين الموقع. قد تُستخدم بيانات قياس الإعلانات بعد موافقتك.',essential:'الضروري فقط',analytics:'السماح بالتحليلات',analyticsOnly:'التحليلات فقط',measurement:'السماح بالتحليلات وقياس الإعلانات',privacy:'تفاصيل الخصوصية (بالإنجليزية)'},
      hi:{title:'गोपनीयता विकल्प',copy:'ज़रूरी वेबसाइट सुविधाएँ हमेशा चलती हैं। वैकल्पिक विश्लेषण से वेबसाइट बेहतर बनाने में मदद मिलती है। विज्ञापन मापने की अनुमति अलग से ली जाती है।',essential:'केवल ज़रूरी',analytics:'विश्लेषण की अनुमति दें',analyticsOnly:'सिर्फ़ विश्लेषण',measurement:'विश्लेषण और विज्ञापन मापन की अनुमति',privacy:'गोपनीयता विवरण (अंग्रेज़ी में)'},
      ur:{title:'رازداری کا انتخاب',copy:'ویب سائٹ کی ضروری سہولتیں ہمیشہ کام کرتی ہیں۔ اختیاری تجزیہ ویب سائٹ کو بہتر بناتا ہے۔ اشتہاری پیمائش آپ کی اجازت سے ہوتی ہے۔',essential:'صرف ضروری',analytics:'تجزیے کی اجازت دیں',analyticsOnly:'صرف تجزیہ',measurement:'تجزیے اور اشتہاری پیمائش کی اجازت',privacy:'رازداری کی تفصیل (انگریزی میں)'}
    }[locale];
    if(ui){
      const localizedButtons=adsEnabled()
        ? '<button type="button" data-choice="denied">'+ui.essential+'</button><button type="button" data-choice="granted">'+ui.analyticsOnly+'</button><button type="button" class="primary" data-choice="measurement">'+ui.measurement+'</button>'
        : '<button type="button" data-choice="denied">'+ui.essential+'</button><button type="button" class="primary" data-choice="granted">'+ui.analytics+'</button>';
      d.setAttribute('aria-label',ui.title);
      d.innerHTML='<div class="ftq-consent-copy"><strong>'+ui.title+'</strong><span>'+ui.copy+'</span><a href="/privacy.html#analytics">'+ui.privacy+'</a></div><div class="ftq-consent-actions">'+localizedButtons+'</div>';
    }else{
    d.innerHTML='<div class="ftq-consent-copy"><strong>Privacy choice</strong><span>'+copy+'</span><a href="/privacy.html#analytics">Privacy details</a></div><div class="ftq-consent-actions">'+buttons+'</div>';
    }
    d.addEventListener('click',e=>{const b=e.target.closest('[data-choice]');if(b)setChoice(b.dataset.choice)});
    document.body.appendChild(d);
  }

  const measurement=document.createElement('script');
  measurement.async=true;
  measurement.src='/openai-lead-measurement.js?v=20261005lead1';
  measurement.onload=function(){
    if(adsEnabled()&&storedAdsChoice()!=='granted'&&storedAdsChoice()!=='denied'){
      const refresh=function(){removeBanner();showBanner(true)};
      if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',refresh,{once:true});
      else refresh();
    }
  };
  document.head.appendChild(measurement);
  loadGoogleTag();
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>showBanner(false),{once:true});
  else showBanner(false);
})();
