// === WEBSITE AI CHAT WIDGET — Freshtiq Automation AI Assistant ===
// Hybrid: tries API first, falls back to smart static assistant with local responses

(function() {
  if (document.getElementById('ft-chat-loading')) return;
  const already = document.getElementById('ft-chat-widget');
  if (already) already.remove();

  // ─── CONFIG ───
  const API = window.location.hostname === 'freshtiqautomation.com' || window.location.hostname.includes('87.76')
    ? '/api/chat'
    : 'http://87.76.199.39/api/chat';
  const WA = 'https://wa.me/918381848389?text=';

  // ─── STATIC KNOWLEDGE BASE (fallback when API is down) ───
  const KB = {
    website: { name: 'Website', min: '₹10,000', monthly: '₹0', delivery: '3-7 days' },
    'business website': { name: 'Business Website', min: '₹10,000+', monthly: '₹0', delivery: '3-5 days' },
    'premium website': { name: 'Premium Website', min: '₹25,000+', monthly: '₹0', delivery: '5-7 days' },
    'booking website': { name: 'Booking Website', min: '₹45,000+', monthly: '₹0', delivery: '7-10 days' },
    ecommerce: { name: 'E-commerce Website', min: '₹60,000+', monthly: '₹0', delivery: '7-14 days' },
    shop: { name: 'E-commerce Website', min: '₹60,000+', monthly: '₹0', delivery: '7-14 days' },
    'whatsapp bot': { name: 'Lead Capture Bot', min: '₹25,000', monthly: '₹8,000/mo', delivery: '5-7 days' },
    'whatsapp': { name: 'WhatsApp Bot', min: '₹25,000', monthly: '₹8,000/mo', delivery: '5-7 days' },
    bot: { name: 'WhatsApp Bot', min: '₹25,000', monthly: '₹8,000/mo', delivery: '5-7 days' },
    'sales bot': { name: 'Sales Automation Bot', min: '₹30,000', monthly: '₹10,000/mo', delivery: '7-10 days' },
    'crm bot': { name: 'Full WhatsApp CRM Bot', min: '₹70,000', monthly: '₹20,000/mo', delivery: '10-14 days' },
    'telegram bot': { name: 'Telegram Bot', min: '₹8,000', monthly: '₹3,000/mo', delivery: '3-5 days' },
    telegram: { name: 'Telegram Bot', min: '₹8,000', monthly: '₹3,000/mo', delivery: '3-5 days' },
    'ai agent': { name: 'Custom AI Agent', min: '₹25,000', monthly: '₹10,000/mo', delivery: '7-14 days' },
    agent: { name: 'AI Agent', min: '₹25,000', monthly: '₹10,000/mo', delivery: '7-14 days' },
    crm: { name: 'Mini CRM', min: '₹25,000+', monthly: '₹0', delivery: '7-10 days' },
    erp: { name: 'Branch ERP', min: '₹75,000+', monthly: '₹0', delivery: '14-21 days' },
    seo: { name: 'SEO Starter', min: '₹5,000/mo', monthly: '', delivery: 'Ongoing' },
    'social media': { name: 'Social Media Management', min: '₹10,000/mo', monthly: '', delivery: 'Ongoing' },
    'mobile app': { name: 'Mobile App', min: '₹50,000+', monthly: '₹0', delivery: '14-21 days' },
    app: { name: 'Mobile App', min: '₹50,000+', monthly: '₹0', delivery: '14-21 days' },
    demo: null, // special handler
    hi: null, hello: null, hey: null,
    thanks: null, thank: null
  };

  function getLocalReply(text) {
    const lower = text.toLowerCase().trim();

    // Greetings
    if (/^(hi|hello|hey|hii|hlo)\b/.test(lower)) {
      return "Hey there! 👋 Welcome to Freshtiq. I'm your business automation consultant. What are you looking to build?";
    }
    if (/\b(thanks|thank you|thx)\b/.test(lower)) {
      return "You're welcome! 😊 Feel free to explore our services at freshtiqautomation.com or message me anytime. You can also WhatsApp me directly at +91 8381848389.";
    }

    // Pricing requests
    if (/price|cost|rate|kitna|charges|how much|fee/i.test(lower)) {
      // Check for specific product mention
      for (const [key, val] of Object.entries(KB)) {
        if (!val) continue;
        if (lower.includes(key)) {
          return `**${val.name} Pricing:**\nStarting at ${val.min}${val.monthly ? ' + ' + val.monthly : ''}\nDelivery: ${val.delivery}\n\nWant detailed quote? 👉 <a href="${WA}Hi%20Freshtiq!%20I%20want%20${encodeURIComponent(val.name)}%2C%20please%20send%20details." target="_blank" style="color:#818cf8;font-weight:600">WhatsApp par details bhejein</a>`;
        }
      }
      // General pricing
      return `**Our Services & Pricing:**\n\n🌐 Website: ₹10,000+\n🤖 WhatsApp Bot: ₹25,000+\n🧠 AI Agent: ₹25,000+\n📊 CRM: ₹25,000+\n✈️ Telegram Bot: ₹8,000+\n🔍 SEO: ₹5,000/mo\n📱 Mobile App: ₹50,000+\n\n👉 <a href="${WA}Hi%20Freshtiq!%20I%20want%20pricing%20details." target="_blank" style="color:#818cf8;font-weight:600">WhatsApp par details bhejein</a>`;
    }

    // WhatsApp bot specific
    if (lower.includes('whatsapp') && (lower.includes('bot') || lower.includes('price') || lower.includes('cost'))) {
      return `**WhatsApp Bot Pricing:**\n\n🥇 Starter (Lead Capture): ₹25,000 + ₹8,000/mo\n🥈 Business (Sales Auto): ₹30,000 + ₹10,000/mo\n🥇 Full CRM Bot: ₹70,000 + ₹20,000/mo\n\nAll include: 24/7 AI, Lead capture, Multi-language, Analytics\n\n👉 <a href="${WA}Hi%20Freshtiq!%20I%20want%20WhatsApp%20bot%20details." target="_blank" style="color:#818cf8;font-weight:600">WhatsApp par details bhejein</a>`;
    }

    // Website specific
    if (lower.includes('website') && (lower.includes('price') || lower.includes('cost') || lower.includes('kitna'))) {
      return `**Website Pricing:**\n\n🌐 Business Website: ₹10,000+\n✨ Premium Website: ₹25,000+\n📅 Booking Website: ₹45,000+\n🛒 E-commerce: ₹60,000+\n\nAll include: Mobile responsive, SEO, AI Chat widget, WhatsApp integration\n\n👉 <a href="${WA}Hi%20Freshtiq!%20I%20want%20website%20details." target="_blank" style="color:#818cf8;font-weight:600">WhatsApp par details bhejein</a>`;
    }

    // Demo request
    if (/\bdemo\b/i.test(lower)) {
      return "Of course! I'd love to show you what we can build. 📅\n\nPlease WhatsApp me at +91 8381848389 and I'll arrange a live demo of our work.\n\n👉 <a href='https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20want%20to%20book%20a%20demo.' target='_blank' style='color:#818cf8;font-weight:600'>Book Demo on WhatsApp</a>";
    }

    // No match — generic help
    return "I'm here to help! 🤖\n\nI can tell you about:\n• **Pricing** — services & rates\n• **Websites** — business, e-commerce, booking\n• **WhatsApp Bots** — sales, support, CRM\n• **AI Agents** — custom AI for your business\n• **CRM/ERP** — manage customers and operations\n\nWhat would you like to know? Or 👉 <a href='https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20need%20help%20with%20automation.' target='_blank' style='color:#818cf8;font-weight:600'>Chat on WhatsApp</a>";
  }

  // ─── SESSION ID ───
  const SID = 'web_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();

  // ─── STYLES ───
  const style = document.createElement('style');
  style.textContent = `
#ft-chat-widget{position:fixed;bottom:90px;right:24px;z-index:2147483640;width:380px;max-width:calc(100vw - 32px);background:#0b0f19;border:1px solid rgba(91,141,239,0.2);border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.6);display:none;flex-direction:column;font-family:'Inter','Segoe UI',sans-serif;overflow:hidden;animation:ftFadeIn 0.3s ease}
#ft-chat-widget.open{display:flex}
#ft-chat-header{display:flex;align-items:center;gap:12px;padding:16px 20px;background:linear-gradient(135deg,#5b8def 0%,#8b5cf6 100%);color:white;cursor:pointer;user-select:none}
#ft-chat-header .ft-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0}
#ft-chat-header .ft-info{flex:1;min-width:0}
#ft-chat-header .ft-info strong{display:block;font-size:0.9rem}
#ft-chat-header .ft-info span{font-size:0.75rem;opacity:0.8}
#ft-chat-header .ft-close{background:none;border:none;color:white;font-size:1.3rem;cursor:pointer;padding:4px;opacity:0.7;transition:opacity 0.2s}
#ft-chat-header .ft-close:hover{opacity:1}
#ft-chat-messages{flex:1;min-height:320px;max-height:400px;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px;background:#0b0f19;scroll-behavior:smooth;-webkit-overflow-scrolling:touch}
#ft-chat-messages::-webkit-scrollbar{width:4px}
#ft-chat-messages::-webkit-scrollbar-track{background:transparent}
#ft-chat-messages::-webkit-scrollbar-thumb{background:rgba(91,141,239,0.3);border-radius:4px}
.ft-msg{max-width:88%;padding:10px 14px;border-radius:16px;font-size:0.85rem;line-height:1.55;animation:ftFadeIn 0.3s ease;word-wrap:break-word}
.ft-msg.bot{align-self:flex-start;background:rgba(91,141,239,0.12);border:1px solid rgba(91,141,239,0.15);color:#e2e8f0;border-bottom-left-radius:4px}
.ft-msg.user{align-self:flex-end;background:linear-gradient(135deg,#5b8def,#8b5cf6);color:white;border-bottom-right-radius:4px}
.ft-msg .ft-time{font-size:0.65rem;opacity:0.5;margin-top:4px;text-align:right}
.ft-msg a{color:#818cf8;text-decoration:underline}
.ft-typing{align-self:flex-start;display:flex;gap:4px;padding:12px 16px;background:rgba(91,141,239,0.08);border-radius:16px;border-bottom-left-radius:4px;align-items:center}
.ft-typing span{width:6px;height:6px;border-radius:50%;background:#5b8def;animation:ftTyping 1.4s infinite;opacity:0.3}
.ft-typing span:nth-child(2){animation-delay:0.2s}
.ft-typing span:nth-child(3){animation-delay:0.4s}
@keyframes ftTyping{0%,80%,100%{opacity:0.3;transform:translateY(0)} 40%{opacity:1;transform:translateY(-4px)}}
#ft-chat-input{display:flex;gap:8px;padding:12px 16px;border-top:1px solid rgba(91,141,239,0.1);background:#0b0f19}
#ft-chat-input input{flex:1;padding:10px 14px;border-radius:50px;border:1px solid rgba(91,141,239,0.15);background:rgba(255,255,255,0.04);color:white;font-size:0.85rem;outline:none;transition:border 0.2s;font-family:inherit}
#ft-chat-input input:focus{border-color:#5b8def}
#ft-chat-input input::placeholder{color:#64748b}
#ft-chat-input button{width:40px;height:40px;border-radius:50%;border:none;background:linear-gradient(135deg,#5b8def,#8b5cf6);color:white;font-size:1.2rem;cursor:pointer;transition:transform 0.2s;flex-shrink:0;display:flex;align-items:center;justify-content:center}
#ft-chat-input button:hover{transform:scale(1.05)}
#ft-chat-input button:disabled{opacity:0.4;cursor:default;transform:none}
#ft-chat-toggle{position:fixed;bottom:24px;right:24px;z-index:2147483641;width:56px;height:56px;border-radius:50%;border:none;background:linear-gradient(135deg,#5b8def 0%,#8b5cf6 100%);color:white;font-size:1.6rem;cursor:pointer;box-shadow:0 4px 20px rgba(91,141,239,0.4);transition:all 0.3s cubic-bezier(0.16,1,0.3,1);display:flex;align-items:center;justify-content:center}
#ft-chat-toggle:hover{transform:scale(1.08);box-shadow:0 6px 30px rgba(91,141,239,0.5)}
.ft-quick-actions{display:flex;flex-wrap:wrap;gap:6px;padding:12px 16px 0;background:#0b0f19}
.ft-quick-btn{padding:6px 12px;font-size:0.72rem;border-radius:50px;border:1px solid rgba(91,141,239,0.2);background:rgba(91,141,239,0.06);color:#818cf8;cursor:pointer;transition:all 0.2s;white-space:nowrap}
.ft-quick-btn:hover{background:rgba(91,141,239,0.15);border-color:#5b8def}
@keyframes ftFadeIn{from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)}}
@media(max-width:500px){
  #ft-chat-widget{right:8px;bottom:80px;width:calc(100vw - 16px);border-radius:20px}
  #ft-chat-toggle{bottom:12px;right:12px;width:48px;height:48px;font-size:1.4rem}
}
`;
  document.head.appendChild(style);

  // ─── BUILD DOM ───
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
<div class="ft-quick-actions">
  <button class="ft-quick-btn" data-action="pricing">💰 Pricing</button>
  <button class="ft-quick-btn" data-action="website">🌐 Website</button>
  <button class="ft-quick-btn" data-action="bot">🤖 WhatsApp Bot</button>
  <button class="ft-quick-btn" data-action="demo">📅 Demo</button>
</div>
<div id="ft-chat-messages"></div>
<div id="ft-chat-input">
  <input type="text" id="ft-msg-input" placeholder="Ask me about pricing, services..." autocomplete="off">
  <button id="ft-send-btn">➤</button>
</div>`;
  document.body.appendChild(widget);

  // ─── STATE ───
  let isOpen = false;
  let isSending = false;
  let isOffline = false; // tracks if API is unavailable

  const msgContainer = document.getElementById('ft-chat-messages');
  const msgInput = document.getElementById('ft-msg-input');
  const sendBtn = document.getElementById('ft-send-btn');
  const closeBtn = document.getElementById('ft-chat-close');

  // ─── HELPERS ───
  function scrollDown() {
    setTimeout(() => { msgContainer.scrollTop = msgContainer.scrollHeight; }, 50);
  }

  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'ft-msg ' + role;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    div.innerHTML = text.replace(/\n/g, '<br>') + '<div class="ft-time">' + time + '</div>';
    msgContainer.appendChild(div);
    scrollDown();
  }

  function showTyping() {
    if (document.getElementById('ft-typing-indicator')) return;
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

  function formatReply(text) {
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/```([\s\S]*?)```/g, '<code>$1</code>');
    return text;
  }

  // ─── SEND (Hybrid: API first, static fallback) ───
  async function sendMessage(text) {
    text = text.trim();
    if (!text || isSending) return;

    addMessage(text, 'user');
    msgInput.value = '';
    setBusy(true);
    showTyping();

    try {
      // Always try API first (even on new session)
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: SID,
          history: []
        }),
        signal: AbortSignal.timeout(8000) // 8s timeout
      });
      const data = await res.json();
      hideTyping();

      if (data.reply) {
        isOffline = false;
        addMessage(formatReply(data.reply), 'bot');
        setBusy(false);
        return;
      }
    } catch(e) {
      // API failed — silent fallback
    }

    // Fallback: local static reply
    hideTyping();
    isOffline = true;
    const reply = getLocalReply(text);
    addMessage(reply, 'bot');

    // If this is the first fallback, show a note
    if (!window._ftOfflineNoted) {
      window._ftOfflineNoted = true;
      setTimeout(() => {
        addMessage('💡 *Tip:* You can also WhatsApp me directly for immediate response — <a href="https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20need%20help." target="_blank">Chat on WhatsApp →</a>', 'bot');
      }, 800);
    }
    setBusy(false);
  }

  // ─── EVENTS ───
  toggleBtn.addEventListener('click', () => {
    isOpen = !isOpen;
    widget.classList.toggle('open', isOpen);
    toggleBtn.innerHTML = isOpen ? '✕' : '💬';
    if (isOpen) {
      msgInput.focus();
      if (msgContainer.children.length === 0) {
        setTimeout(() => {
          addMessage("Hey there! 👋 Welcome to Freshtiq Automation AI. I'm your business consultant. Ask me about our services, pricing, or anything automation!", 'bot');
        }, 400);
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

  // Quick action buttons
  document.querySelectorAll('.ft-quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      const prompts = {
        pricing: "What are your prices?",
        website: "Tell me about websites",
        bot: "WhatsApp bot price batao",
        demo: "I want a demo"
      };
      const msg = prompts[action] || "I need help";
      if (!widget.classList.contains('open')) {
        isOpen = true;
        widget.classList.add('open');
        toggleBtn.innerHTML = '✕';
        setTimeout(() => {
          msgContainer.innerHTML = '';
          sendMessage(msg);
        }, 400);
      } else {
        sendMessage(msg);
      }
    });
  });

  console.log('[Freshtiq Chat] v2 — Hybrid mode loaded ✅');
})();