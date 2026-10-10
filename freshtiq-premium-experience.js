/* Freshtiq Premium Experience v1 — accessible persistent dark/light user choice.
   No tracking, network calls, or access to business private data. */
(()=>{'use strict';
 const html=document.documentElement;
 function setTheme(){
   // One stable premium identity for every visitor and every device.
   html.setAttribute('data-ftq-theme','light');
   html.style.colorScheme='light';
   const meta=document.querySelector('meta[name="theme-color"]');
   if(meta)meta.setAttribute('content','#edf4f8');
 }
 setTheme();
 function init(){
  document.getElementById('ftq-theme-control')?.remove();
  // Some in-app browsers request a desktop-sized 980px layout on a real 390px
  // phone. Detect that mismatch without affecting genuine desktop/tablet widths.
  const sw=window.screen?.width||0;
  const vw=window.innerWidth||0;
  if(sw>250&&sw<=600&&vw>=730&&vw/sw>1.45&&
    window.matchMedia?.('(pointer: coarse)').matches){
     const ratio=Math.min(3,Math.max(1.45,vw/sw));
     document.body.classList.add('ftq-compact-device-view');
     const vars={
       '--ftq-phone-text':Math.round(16*ratio)+'px',
       '--ftq-phone-small':Math.round(14*ratio)+'px',
       '--ftq-phone-heading':Math.round(26*ratio)+'px',
       '--ftq-phone-card-heading':Math.round(19*ratio)+'px',
       '--ftq-phone-navheight':Math.round(60*ratio)+'px',
       '--ftq-phone-ctaheight':Math.round(70*ratio)+'px',
       '--ftq-phone-pad':Math.round(18*ratio)+'px',
       '--ftq-phone-gap':Math.round(12*ratio)+'px'
     };
     for(const [key,value] of Object.entries(vars))
       document.documentElement.style.setProperty(key,value);
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
  setTheme();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
 else init();
})();
