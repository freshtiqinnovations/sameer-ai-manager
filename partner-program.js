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
      setNotice('appResult','🎉 Congratulations! Registration COMPLETE. Your reference: '+data.reseller_id+'. Private 30-day training access key (save this securely): '+data.application_key+'. Open https://portal.freshtiqautomation.com/join?role=partner to start training. Verified commissions and withdrawals require signed terms and collected payment. To speak with the bot, tap WhatsApp and send JOIN PARTNER.','success');
      byId('statusPartnerId').value=data.reseller_id;
      byId('statusApplicationKey').value=data.application_key;
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
    const showByCurrency=key=>{
      const rows=me.stats.byCurrency||[];
      if(!rows.length)return money(0);
      return rows.map(r=>{
        const amount=Number(r[key]||0),currency=r.currency||'INR';
        try{return new Intl.NumberFormat('en-IN',{style:'currency',currency,maximumFractionDigits:0}).format(amount);}
        catch(_){return currency+' '+amount.toFixed(2);}
      }).join(' · ');
    };
    byId('partnerPending').textContent=showByCurrency('eligible');
    byId('partnerPaid').textContent=showByCurrency('paid');
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
    const wd=byId('partnerWithdrawals');
    if(wd){
      wd.replaceChildren();
      try{
        const records=await request('/api/reseller/my-withdrawals',{key:auth.key});
        for(const r of records.requests||[]){
          const entry=document.createElement('p');
          entry.textContent='Request #'+r.id+' · '+r.currency+' '+(Number(r.amount_minor)/100).toFixed(2)+' · '+r.status;
          wd.appendChild(entry);
        }
        for(const p of records.eligible||[]){
          const holder=document.createElement('div');holder.className='res-row';
          const label=document.createElement('span');label.textContent='Verified '+p.currency+' '+Number(p.commission_amount).toLocaleString('en-IN')+' · payout #'+p.id;
          const btn=document.createElement('button');btn.type='button';btn.className='cta secondary';btn.textContent='Request withdrawal →';
          btn.addEventListener('click',async()=>{
            if(!confirm('Request withdrawal of this already-verified eligible commission? No automatic bank transfer happens.'))return;
            btn.disabled=true;
            try{await request('/api/reseller/my-withdrawals/request',{method:'POST',key:auth.key,body:{payout_id:p.id}});await refresh()}
            catch(err){setNotice('accessResult',err.message||'Withdrawal request unavailable.','error');btn.disabled=false}
          });
          holder.append(label,btn);wd.appendChild(holder);
        }
        if(!wd.childNodes.length){const p=document.createElement('p');p.textContent='No eligible payout yet. A booked project is not a payable commission.';wd.append(p)}
      }catch(_){const p=document.createElement('p');p.textContent='Withdrawal information temporarily unavailable. Your existing referrals remain intact.';wd.append(p)}
    }
    byId('partnerDashboard').hidden=false;
  }
  byId('applicationStatusForm')?.addEventListener('submit',async e=>{
    e.preventDefault();
    const reseller_id=value('statusPartnerId').toUpperCase(),application_key=value('statusApplicationKey');
    try{
      const data=await request('/api/reseller/application-status',{method:'POST',body:{reseller_id,application_key}});
      setNotice('applicationStatusResult','Application '+data.application.reseller_id+': '+data.application.status.toUpperCase()+'. '+data.next_step,'success');
    }catch(err){setNotice('applicationStatusResult',err.message||'Cannot check status.','error');}
  });
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
