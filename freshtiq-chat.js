// === WEBSITE AI CHAT WIDGET — Freshtiq Automation AI Business Brain ===
// Self-contained widget injected into any Freshtiq page.
// Uses Freshtiq server-side Business Brain + approved website knowledge.

(function() {
  if (document.getElementById('ft-chat-loading')) return;
  const already = document.getElementById('ft-chat-widget');
  if (already) already.remove();

  // ─── CONFIG ───
  const API = window.location.hostname.includes('87.76')
    ? '/api/chat'
    : 'https://portal.freshtiqautomation.com/api/chat';
  const LEAD_API = API.replace('/api/chat','/api/lead');

  // ─── SESSION ID (per visitor) ───
  const SID = (() => { const k='ft_chat_sid_v2'; let v=''; try{v=sessionStorage.getItem(k)||'';}catch(_){} if(!v){v='web_'+Math.random().toString(36).substring(2,10)+'_'+Date.now();try{sessionStorage.setItem(k,v);}catch(_){}} return v; })();

  // ─── CONNECTED JOURNEY CONTEXT ───
  const PAGE_META = (() => {
    const qs = new URLSearchParams(location.search);
    const attrKey = 'ft_attribution_v1';
    const landingKey = 'ft_landing_v1';
    let saved = {};
    try { saved = JSON.parse(sessionStorage.getItem(attrKey) || '{}') || {}; } catch(_) {}
    const current = {
      utm_source: qs.get('utm_source') || '', utm_medium: qs.get('utm_medium') || '',
      utm_campaign: qs.get('utm_campaign') || '', utm_content: qs.get('utm_content') || '',
      utm_term: qs.get('utm_term') || ''
    };
    if (Object.values(current).some(Boolean)) {
      saved = Object.assign({}, saved, current);
      try { sessionStorage.setItem(attrKey, JSON.stringify(saved)); } catch(_) {}
    }
    let landing = '';
    try { landing = sessionStorage.getItem(landingKey) || ''; if(!landing){ landing=location.href; sessionStorage.setItem(landingKey,landing); } } catch(_) { landing=location.href; }
    const path = location.pathname.toLowerCase();
    const market = path.startsWith('/saudi-arabia') ? 'Saudi Arabia' : path.startsWith('/uae') ? 'UAE' : path.startsWith('/india') ? 'India' : '';
    let service = '';
    if (/whatsapp/.test(path)) service='WhatsApp Automation';
    else if (/ai-chatbot|chatbot/.test(path)) service='AI Chatbot';
    else if (/crm-erp/.test(path)) service='CRM / ERP';
    else if (path.includes('/services/website-development')) service='Website';
    else if (path.includes('/services/web-app-development')) service='';
    else if (/appointment|booking/.test(path)) service='Booking Automation';
    else if (/lead-follow-up|lead-generation/.test(path)) service='Lead Generation & Follow-up';
    else if (/ai-agent/.test(path)) service='AI Agent';
    else if (path.includes('/pricing')) service='Pricing';
    else if (path.includes('/demo')) service='Interactive Demo';
    return Object.assign({}, saved, {
      session_id: SID, page_url: location.href, page_title: document.title,
      landing_page: landing, referrer: document.referrer || '',
      locale: document.documentElement.lang || navigator.language || 'en', market, service
    });
  })();
  window.FreshtiqJourney = {
    getSessionId: () => SID,
    getContext: () => Object.assign({}, PAGE_META, { page_url: location.href, page_title: document.title, page_service: PAGE_META.service || '' })
  };

  // ─── STYLES ───
  const style = document.createElement('style');
  style.textContent = `
#ft-chat-widget{position:fixed;bottom:90px;right:24px;z-index:2147483640;width:380px;max-width:calc(100vw - 32px);background:#0b0f19;border:1px solid rgba(108,99,255,0.2);border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.6);display:none;flex-direction:column;font-family:'Inter','Segoe UI',sans-serif;overflow:hidden;animation:ftFadeIn 0.3s ease}
#ft-chat-widget.open{display:flex}
#ft-chat-header{display:flex;align-items:center;gap:12px;padding:16px 20px;background:#6C63FF;color:white;cursor:pointer;user-select:none}
#ft-chat-header .ft-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0}
#ft-chat-header .ft-info{flex:1;min-width:0}
#ft-chat-header .ft-info strong{display:block;font-size:0.9rem}\n.ft-msg.bot a{color:#8be9fd;text-decoration:underline;text-underline-offset:2px;word-break:break-word}.ft-msg.bot a:hover{color:#fff}
#ft-chat-header .ft-info span{font-size:0.75rem;opacity:0.8}
#ft-chat-header .ft-close{background:none;border:none;color:white;font-size:1.3rem;cursor:pointer;padding:4px;opacity:0.7;transition:opacity 0.2s}
#ft-chat-header .ft-close:hover{opacity:1}
#ft-chat-messages{flex:1;min-height:320px;max-height:400px;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px;background:#0b0f19;scroll-behavior:smooth}
#ft-chat-messages::-webkit-scrollbar{width:4px}
#ft-chat-messages::-webkit-scrollbar-track{background:transparent}
#ft-chat-messages::-webkit-scrollbar-thumb{background:rgba(108,99,255,0.3);border-radius:4px}
.ft-msg{max-width:85%;padding:10px 14px;border-radius:16px;font-size:0.88rem;line-height:1.5;animation:ftFadeIn 0.3s ease;word-wrap:break-word}
.ft-msg.bot{align-self:flex-start;background:rgba(108,99,255,0.12);border:1px solid rgba(108,99,255,0.15);color:#e2e8f0;border-bottom-left-radius:4px}
.ft-msg.user{align-self:flex-end;background:#6C63FF;color:white;border-bottom-right-radius:4px}
.ft-msg .ft-time{font-size:0.65rem;opacity:0.5;margin-top:4px;text-align:right}
.ft-typing{align-self:flex-start;display:flex;gap:4px;padding:12px 16px;background:rgba(108,99,255,0.08);border-radius:16px;border-bottom-left-radius:4px;align-items:center}
.ft-typing span{width:6px;height:6px;border-radius:50%;background:#6C63FF;animation:ftTyping 1.4s infinite;opacity:0.3}
.ft-typing span:nth-child(2){animation-delay:0.2s}
.ft-typing span:nth-child(3){animation-delay:0.4s}
@keyframes ftTyping{0%,80%,100%{opacity:0.3;transform:translateY(0)} 40%{opacity:1;transform:translateY(-4px)}}
#ft-chat-input{display:flex;gap:8px;padding:12px 16px;border-top:1px solid rgba(108,99,255,0.1);background:#0b0f19}
#ft-chat-input input{flex:1;padding:10px 14px;border-radius:50px;border:1px solid rgba(108,99,255,0.15);background:rgba(255,255,255,0.04);color:white;font-size:0.88rem;outline:none;transition:border 0.2s}
#ft-chat-input input:focus{border-color:#6C63FF}
#ft-chat-input input::placeholder{color:#64748b}
#ft-chat-input button{width:40px;height:40px;border-radius:50%;border:none;background:#6C63FF;color:white;font-size:1.2rem;cursor:pointer;transition:transform 0.2s;flex-shrink:0;display:flex;align-items:center;justify-content:center}
#ft-chat-input button:hover{transform:scale(1.05)}
#ft-chat-input button:disabled{opacity:0.4;cursor:default;transform:none}
#ft-chat-toggle{position:fixed;bottom:24px;right:24px;z-index:2147483641;width:56px;height:56px;border-radius:50%;border:none;background:#6C63FF;color:white;font-size:1.6rem;cursor:pointer;box-shadow:0 4px 20px rgba(108,99,255,0.3);transition:all 0.3s;display:flex;align-items:center;justify-content:center}
#ft-chat-toggle:hover{transform:scale(1.08);box-shadow:0 6px 30px rgba(108,99,255,0.5)}
#ft-chat-toggle.has-unread::after{content:'';position:absolute;top:-2px;right:-2px;width:12px;height:12px;background:#ef4444;border-radius:50%;border:2px solid #0b0f19}
.ft-quick-actions{display:flex;flex-wrap:wrap;gap:6px;padding:12px 16px 0;background:#0b0f19}
.ft-quick-btn{padding:6px 12px;font-size:0.75rem;border-radius:50px;border:1px solid rgba(108,99,255,0.2);background:rgba(108,99,255,0.06);color:#818cf8;cursor:pointer;transition:all 0.2s;white-space:nowrap}
.ft-quick-btn:hover{background:rgba(108,99,255,0.15);border-color:#6C63FF}
.ft-context-strip{padding:7px 16px 0;background:#0b0f19;color:#94a3b8;font-size:.67rem;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ft-handoff{display:none;margin:10px 14px 0;padding:12px;border:1px solid rgba(108,99,255,.2);border-radius:14px;background:#101827;color:#e2e8f0}.ft-handoff.open{display:block}.ft-handoff-title{font-size:.8rem;font-weight:800;margin-bottom:8px}.ft-handoff-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}.ft-handoff input,.ft-handoff select{width:100%;box-sizing:border-box;padding:8px 9px;border-radius:9px;border:1px solid rgba(148,163,184,.22);background:#0b1220;color:#e2e8f0;font-size:.75rem;outline:none}.ft-handoff input:focus,.ft-handoff select:focus{border-color:#6C63FF}.ft-handoff-wide{grid-column:1/-1}.ft-handoff-consent{display:none;grid-column:1/-1;font-size:.67rem;line-height:1.35;color:#94a3b8}.ft-handoff-consent.show{display:flex;gap:6px;align-items:flex-start}.ft-handoff-consent input{width:auto;margin-top:2px}.ft-handoff-actions{display:flex;gap:7px;margin-top:9px}.ft-handoff-actions button{flex:1;padding:8px;border-radius:9px;border:1px solid rgba(108,99,255,.25);font-weight:800;font-size:.72rem;cursor:pointer}.ft-handoff-save{background:#6C63FF;color:#fff}.ft-handoff-cancel{background:transparent;color:#cbd5e1}.ft-handoff-status{margin-top:7px;font-size:.67rem;color:#94a3b8;line-height:1.35}.ft-chat-privacy{padding:8px 16px 0;background:#0b0f19;color:#64748b;font-size:.68rem;line-height:1.35}
@keyframes ftFadeIn{from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)}}
@media(max-width:500px){
  #ft-chat-widget{right:8px;bottom:80px;width:calc(100vw - 16px);border-radius:20px}
  #ft-chat-toggle{bottom:12px;right:12px;width:48px;height:48px;font-size:1.4rem}
}
`;

  // ─── BUILD DOM ───
  document.head.appendChild(style);

  const toggleBtn = document.createElement('button');
  toggleBtn.id = 'ft-chat-toggle';
  toggleBtn.innerHTML = '💬';
  toggleBtn.title = 'Chat with Freshtiq Automation AI';
  document.body.appendChild(toggleBtn);

  const widget = document.createElement('div');
  widget.id = 'ft-chat-widget';
  widget.innerHTML = `
<div id="ft-chat-header">
  <div class="ft-avatar">🤖</div>
  <div class="ft-info">
    <strong>Freshtiq Automation AI</strong>
    <span>🟢 Online — Business Consultant</span>
  </div>
  <button class="ft-close" id="ft-chat-close">✕</button>
</div>
<div class="ft-context-strip" id="ft-context-strip"></div>
<div class="ft-quick-actions" id="ft-quick-actions"></div>
<div class="ft-handoff" id="ft-handoff">
  <div class="ft-handoff-title">👤 Talk to Freshtiq team</div>
  <div class="ft-handoff-grid">
    <input id="ft-ho-name" class="ft-handoff-wide" type="text" placeholder="Your name" autocomplete="name">
    <select id="ft-ho-method" aria-label="Preferred contact"><option value="Email">Email</option><option value="WhatsApp">WhatsApp</option></select>
    <input id="ft-ho-email" type="email" placeholder="you@company.com" autocomplete="email">
    <input id="ft-ho-phone" class="ft-handoff-wide" type="tel" placeholder="WhatsApp + country code" autocomplete="tel" style="display:none">
    <label class="ft-handoff-consent" id="ft-ho-consent-row"><input id="ft-ho-consent" type="checkbox"><span>Freshtiq may reply to this request on WhatsApp. No marketing unless I separately opt in.</span></label>
  </div>
  <div class="ft-handoff-actions"><button class="ft-handoff-cancel" id="ft-ho-cancel" type="button">Cancel</button><button class="ft-handoff-save" id="ft-ho-save" type="button">Save & hand off</button></div>
  <div class="ft-handoff-status" id="ft-ho-status"></div>
</div>
<div id="ft-chat-messages"></div>
<div class="ft-chat-privacy">🔒 Do not share passwords, OTPs or payment-card details.</div>
<div id="ft-chat-input">
  <input type="text" id="ft-msg-input" placeholder="Type your message..." autocomplete="off">
  <button id="ft-send-btn">➤</button>
</div>
`;

  document.body.appendChild(widget);

  // ─── STATE ───
  let isOpen = false;
  let isSending = false;
  let chatHistory = (()=>{try{const x=JSON.parse(sessionStorage.getItem('ft_chat_history_v2')||'[]');return Array.isArray(x)?x.slice(-18):[]}catch(_){return[]}})();
  let shownLeadRef = (()=>{try{return (window.FreshtiqLead&&window.FreshtiqLead.getRef)?window.FreshtiqLead.getRef():(sessionStorage.getItem('ft_lead_ref_v1')||'');}catch(_){return '';}})();
  function rememberLeadRef(ref){
    ref=String(ref||'').trim(); if(!ref)return '';
    shownLeadRef=ref;
    try{if(window.FreshtiqLead&&window.FreshtiqLead.saveRef)window.FreshtiqLead.saveRef(ref);else sessionStorage.setItem('ft_lead_ref_v1',ref);}catch(_){}
    return ref;
  }

  const msgContainer = document.getElementById('ft-chat-messages');
  const msgInput = document.getElementById('ft-msg-input');
  const sendBtn = document.getElementById('ft-send-btn');
  const closeBtn = document.getElementById('ft-chat-close');
  const quickActions = document.getElementById('ft-quick-actions');
  const contextStrip = document.getElementById('ft-context-strip');
  const handoff = document.getElementById('ft-handoff');
  const hoName = document.getElementById('ft-ho-name');
  const hoMethod = document.getElementById('ft-ho-method');
  const hoEmail = document.getElementById('ft-ho-email');
  const hoPhone = document.getElementById('ft-ho-phone');
  const hoConsent = document.getElementById('ft-ho-consent');
  const hoConsentRow = document.getElementById('ft-ho-consent-row');
  const hoStatus = document.getElementById('ft-ho-status');
  const hoSave = document.getElementById('ft-ho-save');
  const hoCancel = document.getElementById('ft-ho-cancel');

  function marketCurrency(m){ return m==='Saudi Arabia'?'SAR':m==='UAE'?'AED':m==='India'?'INR':''; }
  function pageContextLabel(){
    const ref=shownLeadRef ? ' · Request '+shownLeadRef : '';
    if(PAGE_META.market) return '📍 '+PAGE_META.market+(PAGE_META.service?' · '+PAGE_META.service:'')+(marketCurrency(PAGE_META.market)?' · '+marketCurrency(PAGE_META.market):'')+ref;
    if(PAGE_META.service) return '🧭 Viewing: '+PAGE_META.service+ref;
    return (shownLeadRef?'📋 Connected request: '+shownLeadRef:'🧭 Ask about pricing, scope, demos, integrations or delivery');
  }
  function smartActions(){
    const p=location.pathname.toLowerCase();
    let a;
    if(p.includes('/pricing')||p.includes('/hourly-ai-automation')) a=[['hourly','⏱️ Hourly'],['price','💰 Price'],['quote','🧾 Quote'],['human','👤 Human']];
    else if(p.includes('/demo')) a=[['demo','▶️ Demo'],['consultation','📅 Consultation'],['quote','🧾 Quote'],['human','👤 Human']];
    else if(PAGE_META.market) a=[['localprice','💰 Local Price'],['language','🌐 Language'],['quote','🧾 Quote'],['human','👤 Human']];
    else if(p.includes('/services/')) a=[['scope','🧩 Scope'],['price','💰 Price'],['consultation','📅 Consultation'],['human','👤 Human']];
    else a=[['chatbot','🤖 Chatbot'],['website','🌐 Website/App'],['crm','📊 CRM/ERP'],['quote','🧾 Quote'],['human','👤 Human']];
    if(shownLeadRef) a.unshift(['request','📋 My Request']);
    return a.slice(0,5);
  }
  function renderSmartActions(){
    contextStrip.textContent=pageContextLabel();
    quickActions.innerHTML='';
    smartActions().forEach(([action,label])=>{const b=document.createElement('button');b.type='button';b.className='ft-quick-btn';b.dataset.action=action;b.textContent=label;quickActions.appendChild(b);});
  }
  function actionPrompt(action){
    const service = PAGE_META.service && !['Pricing','Interactive Demo'].includes(PAGE_META.service) ? PAGE_META.service : 'my business automation';
    const market = PAGE_META.market ? ' in '+PAGE_META.market : '';
    return {
      chatbot:'I want an AI chatbot for customer support or sales. Help me scope it.',
      website:'I need a website or app that captures leads and connects to automation.',
      crm:'I need CRM/ERP or operations automation. Help me scope the workflow.',
      audit:'I want a free workflow audit. Help me identify the best first automation.',
      scope:'Help me scope '+service+'. Ask me the minimum useful questions.',
      price:'What is the published price for '+service+market+'?',
      hourly:'I want to hire Freshtiq by the hour. Explain the hourly rate, minimum hours, what hourly work is best for, and help me describe my task.',
      localprice:'Show me the relevant published pricing'+market+' for the service I need.',
      compare:'Compare Standard, Professional and Premium packages and tell me what changes between them.',
      currency:'Show me how to view prices in my currency and explain regional pricing vs FX conversion.',
      demo:'Show me the most relevant interactive demo for my requirement.',
      realestate:'Show me the Dubai real-estate enquiry automation flow and what information it captures.',
      clinic:'Show me the clinic appointment automation flow and human approval option.',
      language:'Can this customer journey work in Arabic, English, Urdu and Hinglish? Explain the handoff.',
      quote:'I want a written quote. Ask me only for the missing details needed to prepare the right scope and price.',
      consultation:'I want a consultation. Ask for my preferred day/time, timezone and contact method, then keep the request linked to this conversation.',
      request:shownLeadRef ? ('My Freshtiq Lead Ref is '+shownLeadRef+'. Summarize what you know from this conversation and tell me the best next step without inventing a status.') : 'Help me continue my existing Freshtiq request.'
    }[action] || 'Help me with '+action+'.';
  }
  function setHandoffMethod(){
    const wa=hoMethod.value==='WhatsApp';hoEmail.style.display=wa?'none':'block';hoPhone.style.display=wa?'block':'none';hoConsentRow.classList.toggle('show',wa);hoStatus.textContent='';
  }
  function openHandoff(){const mb=window.FreshtiqMarketplaceBridge;if(mb&&mb.restricted){addMessage('🔒 Because you reached Freshtiq via **'+mb.label+'**, please keep project communication on '+mb.label+' until the order/contract is active. After that, external contact can be shared according to the platform rules.','bot');return;}handoff.classList.add('open');setHandoffMethod();setTimeout(()=>hoName.focus(),60);}
  function closeHandoff(){handoff.classList.remove('open');hoStatus.textContent='';}

  async function submitHandoff(){
    const name=hoName.value.trim(), method=hoMethod.value, email=hoEmail.value.trim(), phone=hoPhone.value.trim();
    if(name.length<2){hoStatus.textContent='Please enter your name.';return;}
    if(method==='Email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){hoStatus.textContent='Please enter a valid email.';return;}
    if(method==='WhatsApp'&&phone.replace(/\D/g,'').length<8){hoStatus.textContent='Please enter WhatsApp number with country code.';return;}
    if(method==='WhatsApp'&&!hoConsent.checked){hoStatus.textContent='Please confirm WhatsApp reply consent for this request.';return;}
    hoSave.disabled=true;hoStatus.textContent='Saving your request…';
    const recent=chatHistory.slice(-8).map(x=>(x.role==='user'?'Customer: ':'Freshtiq: ')+String(x.content||'').replace(/\s+/g,' ').slice(0,240)).join(' | ').slice(0,1500);
    const meta=window.FreshtiqJourney.getContext();
    const payload=Object.assign({},meta,{
      name, email:method==='Email'?email:'', phone:method==='WhatsApp'?phone:'',
      preferred_contact:method, country:PAGE_META.market||'', service:(PAGE_META.service&&!["Pricing","Interactive Demo"].includes(PAGE_META.service))?PAGE_META.service:'Human Handoff / Automation Enquiry',
      message:'Human handoff requested from website chat.'+(recent?' Recent conversation: '+recent:''), source:'Website Chat Handoff',
      whatsapp_opt_in:method==='WhatsApp'&&hoConsent.checked, marketing_opt_in:false, consent_source:'website_chat_handoff_v1'
    });
    try{
      const r=await fetch(LEAD_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const d=await r.json().catch(()=>({}));
      if(!r.ok||!d.success)throw new Error(d.error||'Could not save request');
      shownLeadRef=rememberLeadRef(d.lead_ref||shownLeadRef);closeHandoff();
      if(method==='WhatsApp'){
        const text=encodeURIComponent('Hello Freshtiq, my Lead Ref is '+(d.lead_ref||'')+'. I requested a human follow-up from the website.');
        addMessage('✅ Handoff saved. Lead Ref: **'+(d.lead_ref||('#'+d.lead_id))+'**. To continue on WhatsApp, tap this link yourself: https://wa.me/918381848389?text='+text,'bot');
      }else addMessage('✅ Handoff saved. Lead Ref: **'+(d.lead_ref||('#'+d.lead_id))+'**. We will reply using the email you provided.','bot');
      try{if(window.gtag)gtag('event','human_handoff_saved',{method,lead_ref:String(d.lead_ref||'')});}catch(_){}
    }catch(e){hoStatus.textContent='Could not save right now. Please try again or use the Contact page.';}
    finally{hoSave.disabled=false;}
  }

  renderSmartActions();
  hoMethod.addEventListener('change',setHandoffMethod);hoCancel.addEventListener('click',closeHandoff);hoSave.addEventListener('click',submitHandoff);

  // ─── HELPERS ───
  function scrollDown() {
    setTimeout(() => { msgContainer.scrollTop = msgContainer.scrollHeight; }, 50);
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch]));
  }

  function formatReply(text) {
    let safe = escapeHtml(text);
    safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/(^|[\s(])\*([^*\n]+)\*(?=$|[\s.,:;!?])/g, '$1<strong>$2</strong>');
    safe = safe.replace(/(https:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    safe = safe.replace(/\n/g, '<br>');
    return safe;
  }

  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'ft-msg ' + role;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const body = role === 'bot' ? formatReply(text) : escapeHtml(text).replace(/\n/g, '<br>');
    div.innerHTML = body + '<div class="ft-time">' + escapeHtml(time) + '</div>';
    msgContainer.appendChild(div);
    scrollDown();
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'ft-typing';
    div.id = 'ft-typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    msgContainer.appendChild(div);
    scrollDown();
  }

  function hideTyping() {
    const el = document.getElementById('ft-typing-indicator');
    if (el) el.remove();
  }

  function setBusy(b) {
    isSending = b;
    sendBtn.disabled = b;
    msgInput.disabled = b;
  }

  function persistHistory(){ try{ sessionStorage.setItem('ft_chat_history_v2',JSON.stringify(chatHistory.slice(-18))); }catch(_){} }
  if(chatHistory.length){ chatHistory.forEach(m=>addMessage(m.content,m.role==='assistant'?'bot':'user')); }

  // ─── SEND MESSAGE ───
  async function sendMessage(text) {
    text = text.trim();
    if (!text || isSending) return;

    addMessage(text, 'user');
    try { if (window.gtag) gtag('event','chat_message_sent',{page:location.pathname}); } catch(_) {}
    chatHistory.push({ role: 'user', content: text });
    persistHistory();
    msgInput.value = '';
    setBusy(true);
    showTyping();

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.assign({}, window.FreshtiqJourney.getContext(), {
          message: text,
          market: PAGE_META.market || '',
          page_service: PAGE_META.service || '',
          marketplace_source: (window.FreshtiqMarketplaceBridge&&window.FreshtiqMarketplaceBridge.source)||'',
          marketplace_restricted: !!(window.FreshtiqMarketplaceBridge&&window.FreshtiqMarketplaceBridge.restricted)
        }))
      });
      const data = await res.json();
      hideTyping();

      if (data.reply) {
        addMessage(data.reply, 'bot');
        chatHistory.push({ role: 'assistant', content: data.reply });
        persistHistory();

        // Show the customer-safe public lead reference once per chat session.
        const publicLeadRef = data.lead_ref || null;
        if (publicLeadRef && publicLeadRef !== shownLeadRef) {
          shownLeadRef = rememberLeadRef(publicLeadRef);
          addMessage('✅ Request saved. Your Freshtiq Lead Ref is **' + publicLeadRef + '**. Keep it for follow-up.', 'bot');
          try { if (window.gtag) gtag('event','chat_lead_captured',{lead_ref:String(publicLeadRef)}); } catch(_) {}
          console.log('[Freshtiq Chat] Lead ref ' + publicLeadRef + ' captured');
        }
      } else {
        addMessage('Sorry, I hit a glitch. Could you rephrase that? 🤔', 'bot');
      }
    } catch(e) {
      hideTyping();
      addMessage('Connection issue. Please try again, tap **Human**, or use https://freshtiqautomation.com/contact.html .', 'bot');
    }
    setBusy(false);
  }

  // ─── EVENTS ───
  toggleBtn.addEventListener('click', () => {
    isOpen = !isOpen;
    widget.classList.toggle('open', isOpen);
    toggleBtn.innerHTML = isOpen ? '✕' : '💬';
    toggleBtn.classList.remove('has-unread');
    if (isOpen) {
      try { if (window.gtag) gtag('event','chat_open',{page:location.pathname}); } catch(_) {}
      msgInput.focus();
      // Welcome message once, synchronously, so it can never race into the middle of a reply.
      if (chatHistory.length === 0) {
        const welcome = shownLeadRef
          ? ("Hi 👋 I’m Freshtiq AI Business Consultant. Your website request **"+shownLeadRef+"** is connected to this chat for this visit. Ask me about scope, pricing, timelines, demos, integrations or the best next step. You can write in English, Hinglish, Arabic or Urdu.")
          : "Hi 👋 I’m Freshtiq AI Business Consultant. Ask me about services, pricing, timelines, demos, integrations, websites/apps, chatbots or CRM/ERP. You can write in English, Hinglish, Arabic or Urdu. What are you looking to build or improve?";
        addMessage(welcome, 'bot');
        chatHistory.push({ role: 'assistant', content: welcome });
        persistHistory();
      }
    }
  });

  closeBtn.addEventListener('click', () => {
    isOpen = false;
    widget.classList.remove('open');
    toggleBtn.innerHTML = '💬';
  });

  sendBtn.addEventListener('click', () => sendMessage(msgInput.value));
  msgInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage(msgInput.value);
  });

  // Smart page-aware action buttons
  quickActions.addEventListener('click', (e) => {
    const btn=e.target.closest('.ft-quick-btn'); if(!btn)return;
    const action=btn.dataset.action;
    try{if(window.gtag)gtag('event','chat_quick_action',{action:action,page:location.pathname,lead_ref_present:!!shownLeadRef});}catch(_){}
    if(action==='quote'){try{if(window.gtag)gtag('event','quote_intent',{source:'website_chat',page:location.pathname});}catch(_){}}
    if(action==='consultation'){try{if(window.gtag)gtag('event','consultation_intent',{source:'website_chat',page:location.pathname});}catch(_){}}
    if(action==='human'){openHandoff();return;}
    sendMessage(actionPrompt(action));
  });

  // Website buttons/forms can open the same AI conversation without creating a second funnel.
  window.addEventListener('ft:lead-saved', (e) => {
    const ref=e && e.detail && e.detail.lead_ref; if(ref){shownLeadRef=String(ref);renderSmartActions();}
  });
  window.addEventListener('ft:open-chat', (e) => {
    const prompt=String((e&&e.detail&&e.detail.prompt)||'').trim();
    try{sessionStorage.removeItem('ft_chat_pending_prompt_v1');}catch(_){}
    if(!isOpen) toggleBtn.click();
    if(prompt) setTimeout(()=>sendMessage(prompt),80);
  });
  try{
    const pending=String(sessionStorage.getItem('ft_chat_pending_prompt_v1')||'').trim();
    if(pending){sessionStorage.removeItem('ft_chat_pending_prompt_v1');setTimeout(()=>{if(!isOpen)toggleBtn.click();sendMessage(pending);},120);}
  }catch(_){}

  console.log('[Freshtiq Chat] Widget loaded — session ' + SID + ' 🤖');
})();
