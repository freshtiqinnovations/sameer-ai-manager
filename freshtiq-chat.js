// === WEBSITE AI CHAT WIDGET — Freshtiq Automation AI Business Brain ===
// Self-contained widget injected into any Freshtiq page.
// Uses same Business Brain + DeepSeek as WhatsApp bot.

(function() {
  if (document.getElementById('ft-chat-loading')) return;
  const already = document.getElementById('ft-chat-widget');
  if (already) already.remove();

  // ─── CONFIG ───
  const API = window.location.hostname === 'freshtiqautomation.com' || window.location.hostname.includes('87.76')
    ? '/api/chat'
    : 'http://87.76.199.39/api/chat';
  const BRAIN_PROMPT = `You are Freshtiq Automation AI — a senior business automation consultant at Freshtiq Innovations OPC Private Limited.

## IDENTITY
- Name: Freshtiq Automation AI (never say "I am Sameer")
- Company: Freshtiq Innovations OPC Private Limited
- Handoff: +91 8381848389 (only for qualified leads)

## SERVICES
- Websites & E-commerce Stores
- WhatsApp Business Bots (support, sales, order, booking)
- AI Agents (sales, accountant, manager, HR, receptionist, travel, restaurant)
- CRM & ERP Systems
- Mobile Apps (iOS & Android)
- Travel Automation (flight/hotel/visa booking bots)
- Restaurant Automation (menu, order, table booking, delivery)
- Sales Automation (lead tracking, follow-ups, quotations)
- Customer Support Automation (ticket, FAQ, chatbot)
- Custom Software & AI Business Factory

## BEHAVIOR
1. FIRST MESSAGE: Ask about their business in a friendly way.
2. Understand what they need — website, bot, app, CRM, agent, or custom.
3. Ask what problem they're trying to solve.
4. Only ask country after understanding the need.
5. Ask budget naturally after understanding scope.
6. NEVER send IP addresses, server URLs, portal links, or technology details.
7. NEVER start with pricing or services list.
8. Reply warmly in 2-3 lines. Ask ONE question at a time.

## OBJECTION HANDLING
- Budget low: "No problem! We can start with a basic version and upgrade later."
- Need demo: "Of course! I can arrange a demo. What feature would you like to see?"
- Price: "Pricing depends on scope. Tell me what you need and I'll share options."
- Payment: "Payment details shared after we finalize scope."
- Saudi/UAE: "Great! We work across KSA and UAE. Support in Arabic available."

## LANGUAGE RULES
- Arabic → reply in Arabic
- Hindi → reply in Hindi
- Hinglish → reply in SIMPLE ENGLISH
- English → reply in English`;

  // ─── SESSION ID (per visitor) ───
  const SID = 'web_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();

  // ─── STYLES ───
  const style = document.createElement('style');
  style.textContent = `
#ft-chat-widget{position:fixed;bottom:90px;right:24px;z-index:2147483640;width:380px;max-width:calc(100vw - 32px);background:#0b0f19;border:1px solid rgba(108,99,255,0.2);border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.6);display:none;flex-direction:column;font-family:'Inter','Segoe UI',sans-serif;overflow:hidden;animation:ftFadeIn 0.3s ease}
#ft-chat-widget.open{display:flex}
#ft-chat-header{display:flex;align-items:center;gap:12px;padding:16px 20px;background:#6C63FF;color:white;cursor:pointer;user-select:none}
#ft-chat-header .ft-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0}
#ft-chat-header .ft-info{flex:1;min-width:0}
#ft-chat-header .ft-info strong{display:block;font-size:0.9rem}
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
<div class="ft-quick-actions">
  <button class="ft-quick-btn" data-action="website">🌐 Website</button>
  <button class="ft-quick-btn" data-action="bot">🤖 WhatsApp Bot</button>
  <button class="ft-quick-btn" data-action="agent">🧠 AI Agent</button>
  <button class="ft-quick-btn" data-action="crm">📊 CRM</button>
  <button class="ft-quick-btn" data-action="demo">📅 Book Demo</button>
</div>
<div id="ft-chat-messages"></div>
<div id="ft-chat-input">
  <input type="text" id="ft-msg-input" placeholder="Type your message..." autocomplete="off">
  <button id="ft-send-btn">➤</button>
</div>
`;

  document.body.appendChild(widget);

  // ─── STATE ───
  let isOpen = false;
  let isSending = false;
  let chatHistory = [];

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
    // Convert markdown-like bold to HTML
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/```([\s\S]*?)```/g, '<code>$1</code>');
    return text;
  }

  // ─── SEND MESSAGE ───
  async function sendMessage(text) {
    text = text.trim();
    if (!text || isSending) return;

    addMessage(text, 'user');
    chatHistory.push({ role: 'user', content: text });
    msgInput.value = '';
    setBusy(true);
    showTyping();

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: SID,
          history: chatHistory,
          brain: BRAIN_PROMPT
        })
      });
      const data = await res.json();
      hideTyping();

      if (data.reply) {
        const reply = formatReply(data.reply);
        addMessage(reply, 'bot');
        chatHistory.push({ role: 'assistant', content: data.reply });

        // If lead captured, show notification
        if (data.lead_id) {
          console.log('[Freshtiq Chat] Lead #' + data.lead_id + ' captured');
        }
      } else {
        addMessage('Sorry, I hit a glitch. Could you rephrase that? 🤔', 'bot');
      }
    } catch(e) {
      hideTyping();
      addMessage('Connection issue. Please try again or WhatsApp me at +91 8381848389.', 'bot');
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
      msgInput.focus();
      // Welcome message on first open
      if (chatHistory.length === 0) {
        const welcome = "Hey there! 👋 Welcome to Freshtiq Automation AI. I'm your senior business consultant. Tell me about your business — what are you looking to build or automate?";
        setTimeout(() => {
          addMessage(welcome, 'bot');
          chatHistory.push({ role: 'assistant', content: welcome });
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
        website: "I need a website for my business. Can you help?",
        bot: "I want a WhatsApp bot for my business. What do you suggest?",
        agent: "I need an AI agent for my business. Tell me more.",
        crm: "I need a CRM system for my business.",
        demo: "I'd like to book a demo. What do I need to do?"
      };
      const msg = prompts[action] || "I need help with " + action;
      sendMessage(msg);
      if (!widget.classList.contains('open')) {
        // Open widget first
        isOpen = true;
        widget.classList.add('open');
        toggleBtn.innerHTML = '✕';
        setTimeout(() => sendMessage(msg), 300);
      }
    });
  });

  console.log('[Freshtiq Chat] Widget loaded — session ' + SID + ' 🤖');
})();
