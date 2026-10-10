/* Freshtiq Premium Experience v1 — accessible persistent dark/light user choice.
   No tracking, network calls, or access to business private data. */
(()=>{'use strict';
 const KEY='freshtiq_preferred_theme_v1';
 const html=document.documentElement;
 function getSaved(){
  try{const v=localStorage.getItem(KEY);if(v==='light'||v==='dark')return v}catch(e){}
  return window.matchMedia&&window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';
 }
 function setTheme(v,save=false){
   const mode=v==='light'?'light':'dark';
   html.setAttribute('data-ftq-theme',mode);
   html.style.colorScheme=mode;
   const btn=document.getElementById('ftq-theme-control');
   if(btn){btn.setAttribute('aria-pressed',String(mode==='light'));btn.setAttribute('aria-label',mode==='light'?'Switch to dark mode':'Switch to light mode');
    const text=btn.querySelector('.ftq-theme-label');if(text)text.textContent=mode==='light'?'Dark mode':'Light mode';
    const svg=btn.querySelector('.ftq-theme-icon');if(svg)svg.textContent=mode==='light'?'☾':'☼';}
   const m=document.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',mode==='light'?'#f5f9fc':'#071321');
   if(save){try{localStorage.setItem(KEY,mode)}catch(e){}}
 }
 setTheme(getSaved());
 function init(){
  if(document.getElementById('ftq-theme-control'))return;
  const btn=document.createElement('button');btn.id='ftq-theme-control';btn.type='button';btn.className='ftq-theme-control';
  btn.innerHTML='<span class="ftq-theme-icon" aria-hidden="true"></span><span class="ftq-theme-label"></span>';
  btn.addEventListener('click',()=>setTheme(html.getAttribute('data-ftq-theme')==='light'?'dark':'light',true));
  // Prefer stable top navigation; fall back to a compact fixed corner for landing variants.
  let anchor=document.querySelector('#navbar .nav-inner');
  if(anchor){anchor.appendChild(btn);btn.classList.add('ftq-mode-in-nav')}
  else{
    anchor=document.querySelector('header nav, .ftq-nav, header .wrap');
    if(anchor){anchor.appendChild(btn);btn.classList.add('ftq-mode-in-nav')}
    else{document.body.appendChild(btn);btn.classList.add('ftq-mode-floating')}
  }
  // Fixed country badges on small screens obscured readable website content:
  // move them into ordinary page flow instead of covering controls or text.
  if(!document.body.classList.contains('fx-home')){
   const badge=document.querySelector('.ftq-made-india');
   if(badge&&!badge.classList.contains('ftq-inline-country-badge')){
    const heroCopy=document.querySelector('.hero-grid > div:first-child');
    const target=heroCopy||document.querySelector('main')||document.querySelector('article');
    if(target){badge.classList.add('ftq-inline-country-badge');target.insertBefore(badge,target.firstChild)}
   }
  }
  // Give every premium marketing page an accessible contact entry without
  // overlapping text; keep the existing customer/bot chat event handlers.
  if(document.body.classList.contains('fx-premium-page') &&
     !document.querySelector('.ftq-premium-mobile-actions')){
    const strip=document.createElement('nav');
    strip.className='ftq-premium-mobile-actions';
    strip.setAttribute('aria-label','Freshtiq customer help');
    const chat=document.createElement('a');
    chat.href='/#free-audit';chat.className='ftq-open-chat';chat.textContent='AI Assistant';
    const wa=document.createElement('a');
    wa.href='https://wa.me/918381848389?text=Hi%20Freshtiq%2C%20I%20need%20a%20free%20workflow%20audit';
    wa.target='_blank';wa.rel='noopener noreferrer';wa.textContent='WhatsApp';
    strip.append(chat,wa);document.body.appendChild(strip);
    document.body.classList.add('ftq-has-mobile-cta');
  }
  // Preserve keyboard/screen-reader menu state when the legacy nav class toggles.
  const hamburger=document.querySelector('#navbar .hamburger');
  if(hamburger){
   const syncMenu=()=>hamburger.setAttribute('aria-expanded',String(
    hamburger.classList.contains('active')||
    Boolean(document.querySelector('#navbar .nav-links.open'))));
   hamburger.addEventListener('click',()=>requestAnimationFrame(syncMenu));
   syncMenu();
  }
  setTheme(getSaved());
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
 window.addEventListener('storage',e=>{if(e.key===KEY)setTheme(getSaved())});
 if(window.matchMedia){const mq=window.matchMedia('(prefers-color-scheme: light)');
  const changed=()=>{try{if(['light','dark'].includes(localStorage.getItem(KEY)))return}catch(e){}setTheme(getSaved())};
  if(mq.addEventListener)mq.addEventListener('change',changed);
 }
})();