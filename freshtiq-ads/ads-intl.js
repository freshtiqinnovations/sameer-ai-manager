(()=>{'use strict';const f=document.getElementById('adsLeadForm');if(!f)return;
const l=document.documentElement.lang,S=JSON.parse(document.getElementById('ads-i18n').textContent);
const h=document.getElementById('ad-summary'),button=document.getElementById('adsSubmit'),st=document.getElementById('adsLeadStatus');
const qs=new URLSearchParams(location.search);
function plan(){const type=f.elements.ad_type,market=f.elements.market,goal=f.elements.goal,budget=f.elements.budget;
const amt=Number(budget.value);h.textContent=type.options[type.selectedIndex].text+' · '+market.options[market.selectedIndex].text+' · '+goal.options[goal.selectedIndex].text+' · '+(Number.isFinite(amt)&&amt>=1&&amt<=100000?'USD '+amt+' '+S.daily:'—');
return Number.isFinite(amt)&&amt>=1&&amt<=100000;}
['ad_type','market','goal','budget'].forEach(k=>{f.elements[k].addEventListener('input',plan);f.elements[k].addEventListener('change',plan)});plan();
f.addEventListener('submit',async e=>{e.preventDefault();if(f.elements.website.value)return;
const name=f.elements.name.value.trim(),phone=f.elements.phone.value.trim();
if(!name||!/^[+()0-9\s-]{7,22}$/.test(phone)||!f.elements.opt_in.checked||!plan()){st.className='err';st.textContent=S.valid;return;}
button.disabled=true;button.textContent=S.send;st.className='';st.textContent='';
let session='';try{session=sessionStorage.getItem('ft_chat_sid_v2')||'';if(!session){session='intlads_'+Date.now()+'_'+Math.random().toString(36).slice(2,8);sessionStorage.setItem('ft_chat_sid_v2',session)}}catch(e){session='intlads_'+Date.now()}
let country=f.elements.market.value;let promoUrl=f.elements.promo_url.value.trim();if(promoUrl&&!/^https?:\/\/[^\s/]+\.[^\s/]+/i.test(promoUrl)){promoUrl='';}
const b=Number(f.elements.budget.value);const payload={
name,phone,email:'',country,service:'Freshtiq Ads - customer funded advertiser planning',preferred_contact:'WhatsApp',
message:'Requested campaign plan: type='+f.elements.ad_type.value+'; country='+country+'; goal='+f.elements.goal.value+'; daily USD='+b+'; product URL='+(promoUrl||'none')+'; customer language='+l+'; provider funds paid directly; no Freshtiq advance',
source:'Freshtiq Ads Intl '+l,locale:l,session_id:session,page_url:location.href,referrer:document.referrer||'',
utm_source:qs.get('utm_source')||'organic_direct',utm_medium:qs.get('utm_medium')||'',utm_campaign:qs.get('utm_campaign')||'',utm_content:qs.get('utm_content')||'',whatsapp_opt_in:true,marketing_opt_in:false
};
try{let r=await fetch('https://portal.freshtiqautomation.com/api/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await r.json().catch(()=>({}));if(!r.ok||!data.success)throw Error('CRM not confirmed');
const ref=data.lead_ref||String(data.lead_id||'');st.className='ok';st.textContent=S.success;const strong=document.createElement('b');strong.textContent=ref;strong.className='ltr';st.appendChild(strong);st.appendChild(document.createTextNode(' · '+S.ref));f.elements.name.value='';f.elements.phone.value='';f.elements.opt_in.checked=false;
try{if(typeof window.gtag==='function'){window.gtag('event','generate_lead',{lead_source:payload.source,country,service:payload.service,lead_ref_present:!!ref})}}catch(_e){}
}catch(_e){st.className='err';st.textContent=S.fail;}finally{button.disabled=false;button.textContent=S.submit}});
})();
/* FRESHTIQ ADS SAFE CONTACT 20261009
   Separate paid ad-planning workflow remains intact. Manual WhatsApp support
   and visible Indian-company trust badge require no registration or payment.
*/
(function(){
 function ready(){
  const form=document.getElementById('adsLeadForm');
  if(form&&!document.querySelector('.ftq-ads-whatsapp')){
   const row=document.createElement('div');row.className='ftq-ads-whatsapp-row';
   const wa=document.createElement('a');wa.className='ftq-ads-whatsapp';
   const code=document.documentElement.lang||'en';
   const labels={en:'Discuss your business advertising on WhatsApp',hi:'WhatsApp पर विज्ञापन योजना की बात करें',ur:'WhatsApp پر اشتہاری منصوبے کے بارے میں بات کریں',
     ar:'ناقش خطتك الإعلانية عبر واتساب',es:'Hablar de publicidad por WhatsApp',fr:'Discuter de votre publicité sur WhatsApp',
     pt:'Fale sobre publicidade pelo WhatsApp',de:'Werbung über WhatsApp besprechen',id:'Bahas iklan melalui WhatsApp',ml:'WhatsApp വഴി പരസ്യ പദ്ധതി ചർച്ച ചെയ്യാം'};
   wa.textContent=(labels[code]||labels.en)+' ↗';
   wa.href='https://wa.me/918381848389?text='+encodeURIComponent('Hi Freshtiq Ads, I need help planning advertisements for my business. Preferred language: '+code);
   wa.target='_blank';wa.rel='noopener noreferrer';
   row.appendChild(wa);form.insertAdjacentElement('afterend',row);
  }
  if(!document.querySelector('.ftq-made-india')){
   const badge=document.createElement('aside');badge.className='ftq-made-india';
   badge.setAttribute('aria-label','Made in India');
   const flag=document.createElement('img');flag.src='/images/india-flag.svg';flag.alt='Flag of India';flag.width=34;flag.height=23;
   const span=document.createElement('span');span.textContent='Made in India';
   badge.append(flag,span);document.body.appendChild(badge);
  }
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
