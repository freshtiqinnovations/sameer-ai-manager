'use strict';
(() => {
  const search=document.getElementById('svcSearch');
  const grid=document.getElementById('svcGrid');
  const count=document.getElementById('svcResultCount');
  const empty=document.getElementById('svcNoResults');
  const chips=[...document.querySelectorAll('.svc-filter')];
  if(!search||!grid||!count||!empty)return;
  const cards=[...grid.querySelectorAll('.svc-card')];
  const params=new URLSearchParams(window.location.search);
  let currentGroup='all';
  const safeQuery=(params.get('q')||'').trim().slice(0,100);
  if(safeQuery)search.value=safeQuery;
  const update=()=>{
    const query=search.value.toLocaleLowerCase().trim();
    let visible=0;
    for(const card of cards){
      const category=card.dataset.group;
      const content=card.dataset.search||'';
      const show=(currentGroup==='all'||category===currentGroup)&&(!query||content.includes(query));
      card.hidden=!show;
      if(show)visible++;
    }
    count.textContent=visible+' of '+cards.length+' services shown';
    empty.hidden=visible>0;
  };
  for(const chip of chips){
    chip.addEventListener('click',()=>{
      currentGroup=chip.dataset.filter||'all';
      for(const sibling of chips){
        const active=sibling===chip;
        sibling.classList.toggle('is-active',active);
        sibling.setAttribute('aria-pressed',String(active));
      }
      update();
    });
  }
  search.addEventListener('input',update);
  update();
})();
