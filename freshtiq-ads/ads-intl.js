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