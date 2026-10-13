'use strict';
// Freshtiq approved marketing pages without the homepage script.js loader.
// Load the SAME website AI/chat/CRM widget, never a second chatbot instance.
(function(){
 if(document.querySelector('script[src*="/script.js"]')) return; // existing loader owns it
 function load(){
  if(document.querySelector('script[src*="/freshtiq-chat.js"]')||document.getElementById('ft-chat-widget'))return;
  const s=document.createElement('script');
  s.src='/freshtiq-chat.js?v=20261013adsready1';
  s.async=true;
  s.dataset.ftChatLoader='standalone';
  document.body.appendChild(s);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',load,{once:true});
 else load();
 document.addEventListener('click',function(ev){
  const trigger=ev.target&&ev.target.closest?ev.target.closest('.ftq-open-chat'):null;
  if(!trigger)return;
  ev.preventDefault();
  const prompt=location.pathname.includes('/earn-freshtiq')?'/guide sales':
    location.pathname.includes('/partners')?'/guide partner':'/help';
  if(document.getElementById('ft-chat-widget')){
   window.dispatchEvent(new CustomEvent('ft:open-chat',{detail:{prompt}}));
  }else{
   try{sessionStorage.setItem('ft_chat_pending_prompt_v1',prompt)}catch(_){}
   load();
  }
 });
})();
