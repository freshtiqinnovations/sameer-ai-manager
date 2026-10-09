'use strict';
(function () {
  const API='https://portal.freshtiqautomation.com';
  const byId=id=>document.getElementById(id);
  const money=n=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(Math.max(0,Number(n)||0));
  const setNotice=(id,text,kind='')=>{const el=byId(id);if(!el)return;el.className='notice'+(kind?' '+kind:'');el.textContent=text;};
  const value=id=>(byId(id)?.value||'').trim();
  let auth=null;
  async function request(path,{method='GET',body,key}={}) {
    const response=await fetch(API+path,{method,mode:'cors',credentials:'omit',cache:'no-store',
      headers:{'Content-Type':'application/json',...(key?{'x-partner-key':key}:{})},
      ...(body?{body:JSON.stringify(body)}:{})});
    const data=await response.json().catch(()=>({}));
    if(!response.ok || !data.success) throw new Error(data.error||'Could not complete request. Please try again.');
    return data;
  }
  function calculate() {
    const base=Number(value('eligibleValue')||0);
    const percent=Number(value('eligibleRate')||0);
    byId('exampleCommission').textContent=money(base*percent/100);
  }
  byId('eligibleValue')?.addEventListener('change',calculate);
  byId('eligibleRate')?.addEventListener('change',calculate);
  calculate();
  byId('partnerApplication')?.addEventListener('submit',async e=>{
    e.preventDefault();
    const btn=byId('appSubmit'),name=value('appName'),phone=value('appPhone'),email=value('appEmail'),
      country=value('appCountry'),city=value('appCity'),kind=value('appKind'),experience=value('appExperience');
    if(!name||!phone||!country || !byId('appAccept').checked){
      setNotice('appResult','Please enter your name, phone, country and accept the terms.','error');return;
    }
    btn.disabled=true;btn.textContent='Submitting…';
    setNotice('appResult','Sending your application securely…');
    try{
      const data=await request('/api/reseller/register',{method:'POST',body:{
        name,phone,email,country,city,partner_kind:kind,experience,
        business_type:kind,referral_source:'freshtiq_partner_page',accept_terms:true,
        website:value('appWebsite')
      }});
      setNotice('appResult','Application saved! Your partner reference: '+data.reseller_id+'. Status: PENDING OWNER REVIEW. Freshtiq will contact you using the provided details. No joining fee.','success');
      byId('partnerApplication').reset();
    }catch(err){setNotice('appResult',err.message||'Submission failed. Try again or contact us on WhatsApp.','error');}
    finally{btn.disabled=false;btn.textContent='Send partner application →';}
  });
  function addRow(target,title,detail) {
    const parent=byId(target),row=document.createElement('div'),label=document.createElement('strong'),v=document.createElement('span');
    row.className='res-row';label.textContent=title;v.textContent=detail;row.append(label,v);parent?.appendChild(row);
  }
  async function refresh(){
    if(!auth)return;
    const id=encodeURIComponent(auth.id);
    const [me,list]=await Promise.all([
      request('/api/reseller/stats/'+id,{key:auth.key}),
      request('/api/reseller/leads/'+id,{key:auth.key})
    ]);
    byId('partnerWelcome').textContent='Welcome, '+(me.partner.name||'Partner')+' · '+me.partner.reseller_id;
    byId('partnerTotal').textContent=String(me.stats.totalReferrals||0);
    byId('partnerPending').textContent=money(me.stats.eligibleAwaitingOwnerPayout);
    byId('partnerPaid').textContent=money(me.stats.paidCommission);
    const link='https://freshtiqautomation.com/?partner='+encodeURIComponent(auth.id);
    byId('partnerShare').href=link;
    byId('partnerShare').textContent='Your referral link';
    const container=byId('partnerReferrals');container.replaceChildren();
    if(!list.referrals?.length){
      const p=document.createElement('p');p.textContent='No customer referrals recorded yet.';container.appendChild(p);
    }else {
      list.referrals.forEach(row=>addRow('partnerReferrals',
        (row.public_ref||('Referral '+row.id))+' · '+(row.service||'Enquiry'),
        (row.status||'awaiting review')+' · '+(row.country||'')));
    }
    byId('partnerDashboard').hidden=false;
  }
  byId('partnerAccess')?.addEventListener('submit',async e=>{
    e.preventDefault();
    const id=value('partnerId').toUpperCase(),key=value('partnerKey');
    if(!/^FTQ-RS-\d{4,12}$/.test(id)||!key){
      setNotice('accessResult','Enter a valid partner ID and the access key issued by Freshtiq.','error');return;
    }
    auth={id,key};
    setNotice('accessResult','Checking your approved partner account…');
    try{await refresh();setNotice('accessResult','Approved partner access verified. Keep your key private.','success');}
    catch(err){auth=null;byId('partnerDashboard').hidden=true;setNotice('accessResult',err.message||'Access failed.','error');}
  });
  byId('copyPartnerLink')?.addEventListener('click',async ()=>{
    if(!auth)return;
    const link='https://freshtiqautomation.com/?partner='+encodeURIComponent(auth.id);
    try{await navigator.clipboard.writeText(link);byId('copyPartnerLink').textContent='Copied ✓';}
    catch(_){byId('copyPartnerLink').textContent='Copy failed — open your link above';}
  });
  byId('partnerLeadForm')?.addEventListener('submit',async e=>{
    e.preventDefault();
    if(!auth){setNotice('leadResult','Please open your approved partner account first.','error');return;}
    if(!byId('clientPermission').checked){setNotice('leadResult','Customer permission is required.','error');return;}
    const btn=byId('submitPartnerLead');btn.disabled=true;btn.textContent='Saving…';
    try{
      const data=await request('/api/reseller/lead',{method:'POST',key:auth.key,body:{
        name:value('clientName'),phone:value('clientPhone'),service:value('clientService'),
        country:value('clientCountry'),message:value('clientMessage'),client_permission:true
      }});
      setNotice('leadResult','Referral received! Reference: '+data.lead_ref+'. Commission is NOT yet earned; eligibility starts after a verified paid project.','success');
      byId('partnerLeadForm').reset();
      await refresh();
    }catch(err){setNotice('leadResult',err.message||'Lead submission failed.','error');}
    finally{btn.disabled=false;btn.textContent='Submit customer referral →';}
  });
})();
