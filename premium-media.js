'use strict';
(()=> {
 const button=document.querySelector('[data-motion-toggle]');
 const stack=document.querySelector('.workflow-motion .media-stack');
 if(!button||!stack)return;
 button.addEventListener('click',()=>{
  const paused=stack.classList.toggle('is-paused');
  button.textContent=paused?'Play animation':'Pause animation';
  button.setAttribute('aria-label',paused?'Play animated workflow example':'Pause animated workflow example');
  button.setAttribute('aria-pressed',String(paused));
 });
})();
