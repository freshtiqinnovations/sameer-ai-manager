'use strict';
/**
 * Compact 8-service finder used by public homepages and services page.
 * Native details/summary means browsing categories works without JS.
 * This controller only filters existing cards and opens search matches:
 * prices, product URLs, checkout logic, tracking and consent untouched.
 */
(() => {
 const homeSearch=document.getElementById('ftServiceSearch');
 const fullSearch=document.getElementById('svcSearch');
 const search=homeSearch||fullSearch;
 const root=document.getElementById(homeSearch?'serviceCards':'svcGrid');
 if(!root||!search)return;
 const home=Boolean(homeSearch);
 const selector=home?'.ft-service':'.svc-card';
 const groups=[...root.querySelectorAll(home?'.ft-category-group':'.svc-category-group')];
 const cards=[...root.querySelectorAll(selector)];
 const count=document.getElementById(home?'ftCatalogResultCount':'svcResultCount');
 const empty=document.getElementById(home?'ftServiceNoResults':'svcNoResults');
 const lang=document.documentElement.lang;
 if(groups.length!==4||cards.length!==8||!count||!empty)return;
 const text=lang==='hi'
  ? {all:'4 श्रेणियों में 8 सेवाएँ। श्रेणी खोलें या सेवा खोजें।',matches:' सेवाएँ मिलीं। संबंधित श्रेणी खुली है।',none:'कोई सेवा नहीं मिली। दूसरा शब्द डालें।'}
  : lang==='hi-Latn'
  ? {all:'4 categories mein 8 services. Category kholein ya direct search karein.',matches:' matching services. Category khul gayi hai.',none:'Koi matching service nahi. Dusra keyword try karein.'}
  : {all:'8 services in 4 categories. Expand a category or search.',matches:' matching services. Matching categories are open.',none:'No matching service. Try another keyword.'};
 const aliases=Object.freeze({
  website:'वेबसाइट वेबसाइट बनाना वेब साइट',
  ecommerce_website:'ऑनलाइन स्टोर ईकॉमर्स ई-कॉमर्स दुकान शॉपिंग',
  mobile_app:'मोबाइल ऐप मोबाइल एप्लिकेशन',
  basic_bot:'व्हाट्सऐप व्हाट्सएप वॉट्सऐप बेसिक बॉट',
  whatsapp_automation:'व्हाट्सऐप व्हाट्सएप वॉट्सऐप ऑटोमेशन',
  whatsapp_ai_sales_bot:'व्हाट्सऐप व्हाट्सएप एआई बिक्री सेल्स',
  customer_support_ai:'एआई ग्राहक सहायता सपोर्ट चैटबॉट',
  ai_agent:'एआई एजेंट सहायक चैटबॉट',
  ai_voice_calling:'एआई कॉल आवाज वॉइस कॉलिंग रिसेप्शनिस्ट',
  real_estate_ai:'रियल एस्टेट प्रॉपर्टी मकान संपत्ति',
  crm_erp:'सीआरएम ईआरपी ग्राहक प्रबंधन',
  field_sales_crm:'फील्ड सेल्स बिक्री एजेंट',
  factory_erp:'फैक्ट्री कारखाना उद्योग ईआरपी',
  hr_system:'एचआर कर्मचारी स्टाफ वेतन',
  dashboard_reporting:'डैशबोर्ड रिपोर्ट डेटा विश्लेषण',
  restaurant_automation:'रेस्तराँ रेस्टोरेंट भोजन मेन्यू टेबल बुकिंग',
  clinic_automation:'क्लिनिक डॉक्टर मरीज अपॉइंटमेंट बुकिंग',
  travel_automation:'यात्रा ट्रैवल टूर पर्यटन',
  laundry_system:'लॉन्ड्री कपड़ा धुलाई',
  hotel_automation:'होटल अतिथि मेहमान कमरे बुकिंग',
  custom_integration:'ऑटोमेशन इंटीग्रेशन वर्कफ़्लो',
  seo_service:'एसईओ सर्च गूगल रैंकिंग',
  google_business_profile:'गूगल बिजनेस प्रोफाइल',
  content_marketing:'कंटेंट मार्केटिंग पोस्ट प्रचार',
  lead_generation:'लीड जनरेशन संभावित ग्राहक',
  cloud_hosting:'होस्टिंग सर्वर क्लाउड वीपीएस',
  managed_support:'सहायता मेंटेनेंस रखरखाव सपोर्ट'
 });
 function searchKey(card){
  if(home)return card.dataset.service||'';
  try{return new URL(card.getAttribute('href')||'',location.origin).searchParams.get('service')||''}
  catch(_){return ''}
 }
 let searching=false;
 const update=()=>{
  const query=search.value.trim().toLocaleLowerCase().slice(0,100);
  const wasSearching=searching;searching=Boolean(query);
  let matching=0;
  for(const group of groups){
   let groupMatches=0;
   for(const card of group.querySelectorAll(selector)){
    const key=searchKey(card);
    const hay=((home?card.dataset.match:card.dataset.search)||'')+' '+(aliases[key]||'')+' '+(group.dataset.category||'')+' '+card.textContent;
    const match=!searching||hay.toLocaleLowerCase().includes(query);
    card.hidden=!match;
    if(match){matching++;groupMatches++;}
   }
   group.hidden=searching&&groupMatches===0;
   if(searching)group.open=groupMatches>0;
   else if(wasSearching)group.open=false;
  }
  count.textContent=searching?(matching?matching+text.matches:text.none):text.all;
  empty.hidden=matching>0;
  if(!matching)empty.textContent=text.none;
 };
 for(const group of groups){
  group.addEventListener('toggle',()=>{
   if(!group.open||searching)return;
   for(const other of groups)if(other!==group&&other.open)other.open=false;
  });
 }
 search.addEventListener('input',update);
 if(fullSearch){
  const params=new URLSearchParams(location.search);
  const fromUrl=(params.get('q')||'').trim().slice(0,100);
  if(fromUrl&&!search.value)search.value=fromUrl;
 }
 update();
})();
