'use strict';
// India-only public customer enquiry, with explicit consent. No payment initiated.
// The server remains authoritative for lead acceptance, deduplication and tracking.
(()=>{
 const form=document.getElementById('ftq-india-enquiry');if(!form)return;
 const labelsEl=document.getElementById('ftq-india-contact-labels');if(!labelsEl)return;
 let labels;try{labels=JSON.parse(labelsEl.textContent)}catch(_){return}
 const out=document.getElementById('ftq-enquiry-status'),button=form.querySelector('button[type=submit]');
 function show(message,state){out.textContent=message;out.dataset.status=state}
 form.addEventListener('submit',async e=>{
  e.preventDefault();
  if(button.disabled)return;
  const f=form.elements,name=f.namedItem('name').value.trim(),phone=f.namedItem('phone').value.trim(),
   business=f.namedItem('industry').value,requirement=f.namedItem('requirement').value.trim();
  if(f.namedItem('website').value.trim())return;
  if(name.length<2||phone.replace(/\D/g,'').length<10||!business||requirement.length<12||
    !f.namedItem('india_business').checked||!f.namedItem('contact_consent').checked){
   show(labels.invalid,'error');return;
  }
  button.disabled=true;button.textContent=labels.sending;show('','');
  const code=form.dataset.locale==='hi'?'hi':'hi-Latn';
  const q=new URLSearchParams(location.search);
  let sid='';try{sid=sessionStorage.getItem('ft_chat_sid_v2')||'';}catch(_){}
  if(!sid){sid='site_'+Date.now()+'_'+Math.random().toString(36).slice(2,9);try{sessionStorage.setItem('ft_chat_sid_v2',sid)}catch(_){}}
  const payload={name,phone,email:'',country:'India',currency:'INR',
   service:'Current 8 India-based automation services',message:requirement+'\nBusiness category: '+business,
   preferred_contact:'WhatsApp',source:'FreshTiq India '+code+' customer enquiry',
   whatsapp_opt_in:true,contact_permission:true,marketing_opt_in:false,
   locale:code,session_id:sid,page_url:location.href,landing_page:location.href,
   utm_source:q.get('utm_source')||'',utm_medium:q.get('utm_medium')||'',utm_campaign:q.get('utm_campaign')||''};
  try{
   const res=await fetch('https://portal.freshtiqautomation.com/api/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
   const data=await res.json().catch(()=>({}));
   if(!res.ok||!data.success)throw Error('Lead not accepted');
   const ref=String(data.lead_ref||'');
   show(labels.success+(ref||''),'success');
   if(ref){try{sessionStorage.setItem('ft_lead_ref_v1',ref)}catch(_){}}
   form.reset();
  }catch(_){show(labels.failed,'error')}
  finally{button.disabled=false;button.textContent=labels.submit}
 });
})();
