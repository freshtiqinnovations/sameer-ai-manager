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
    else { try { localStorage.setItem(ADS_KEY,v==='measurement'?'granted':'denied'); } catch(_){} }
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
    const copy=adsEnabled()?'Essential features always work. Choose optional visit analytics and OpenAI ad measurement.':'Essential features always work. Visit analytics is optional.';
    const buttons=adsEnabled()?'<button type="button" data-choice="denied">Essential only</button><button type="button" data-choice="granted">Analytics only</button><button type="button" class="primary" data-choice="measurement">Allow analytics + ad measurement</button>':'<button type="button" data-choice="denied">Essential only</button><button type="button" class="primary" data-choice="granted">Allow analytics</button>';
    const locale=(document.documentElement.lang||'en').toLowerCase().slice(0,2);
    const ui={
      es:{title:'Preferencias de privacidad',copy:'Las funciones esenciales siempre funcionan. El análisis es opcional y nos ayuda a mejorar el sitio. La medición publicitaria requiere su consentimiento.',essential:'Solo lo necesario',analytics:'Permitir análisis',analyticsOnly:'Solo análisis',measurement:'Permitir análisis y medición de anuncios',privacy:'Detalles de privacidad (en inglés)'},
      fr:{title:'Choix de confidentialité',copy:'Les fonctions essentielles restent actives. Les analyses facultatives améliorent le site. Le suivi publicitaire nécessite votre consentement.',essential:'Fonctions essentielles',analytics:'Autoriser les analyses',analyticsOnly:'Analyses uniquement',measurement:'Autoriser analyses et mesure publicitaire',privacy:'Détails de confidentialité (en anglais)'},
      pt:{title:'Preferências de privacidade',copy:'As funções essenciais sempre funcionam. A análise opcional ajuda a melhorar o site. A medição de anúncios exige seu consentimento.',essential:'Apenas o necessário',analytics:'Permitir análise',analyticsOnly:'Apenas análise',measurement:'Permitir análise e medição de anúncios',privacy:'Detalhes de privacidade (em inglês)'},
      de:{title:'Datenschutzeinstellungen',copy:'Notwendige Funktionen sind immer aktiv. Optionale Analysen helfen, die Website zu verbessern. Die Werbemessung erfordert Ihre Einwilligung.',essential:'Nur notwendige Funktionen',analytics:'Analysen erlauben',analyticsOnly:'Nur Analysen',measurement:'Analysen und Werbemessung erlauben',privacy:'Datenschutzhinweise (Englisch)'},
      id:{title:'Pilihan privasi',copy:'Fungsi penting selalu aktif. Analitik opsional membantu meningkatkan situs. Pengukuran iklan memerlukan persetujuan Anda.',essential:'Hanya yang diperlukan',analytics:'Izinkan analitik',analyticsOnly:'Analitik saja',measurement:'Izinkan analitik dan pengukuran iklan',privacy:'Detail privasi (Bahasa Inggris)'},
      ml:{title:'സ്വകാര്യതാ തിരഞ്ഞെടുപ്പ്',copy:'അത്യാവശ്യ സേവനങ്ങൾ എപ്പോഴും പ്രവർത്തിക്കും. ഐച്ഛിക അനലിറ്റിക്സ് സൈറ്റ് മെച്ചപ്പെടുത്താൻ സഹായിക്കും. പരസ്യ അളവെടുപ്പിന് നിങ്ങളുടെ അനുമതി ആവശ്യമാണ്.',essential:'അത്യാവശ്യം മാത്രം',analytics:'അനലിറ്റിക്സ് അനുവദിക്കുക',analyticsOnly:'അനലിറ്റിക്സ് മാത്രം',measurement:'അനലിറ്റിക്സും പരസ്യ അളവെടുപ്പും അനുവദിക്കുക',privacy:'സ്വകാര്യതാ വിശദാംശങ്ങൾ (ഇംഗ്ലീഷിൽ)'},
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
