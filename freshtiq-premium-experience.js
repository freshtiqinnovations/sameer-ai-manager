/* Freshtiq Premium Experience v1 — accessible persistent dark/light user choice.
   No tracking, network calls, or access to business private data. */
(()=>{'use strict';
 const KEY='freshtiq_preferred_theme_v1';
 const html=document.documentElement;
 function getSaved(){try{const v=localStorage.getItem(KEY);return v==='light'||v==='dark'?v:'dark'}catch(e){return 'dark'}}
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
  setTheme(getSaved());
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
 window.addEventListener('storage',e=>{if(e.key===KEY)setTheme(getSaved())});
})();