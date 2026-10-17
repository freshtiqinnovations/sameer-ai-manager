(()=>{'use strict';
const $=id=>document.getElementById(id);
const initial=[
{id:1,title:'Sample Lakeside Flat',city:'Bengaluru',intent:'Rent',price:48000,beds:2,visible:true},
{id:2,title:'Sample Garden Apartment',city:'Bengaluru',intent:'Rent',price:36000,beds:3,visible:true},
{id:3,title:'Sample Tech Park Studio',city:'Hyderabad',intent:'Rent',price:28000,beds:1,visible:true},
{id:4,title:'Sample Hyderabad Villa',city:'Hyderabad',intent:'Buy',price:14000000,beds:3,visible:true},
{id:5,title:'Sample Marina Apartment',city:'Dubai',intent:'Rent',price:57000,beds:2,visible:true},
{id:6,title:'Sample Palm Villa',city:'Dubai',intent:'Buy',price:6400000,beds:3,visible:true}
];
let listings=initial.map(x=>({...x})),blocked=new Set(['Sat 2 PM','Sun 11 AM']),selection=null,selectedSlot='Sat 10 AM',serial=7;
const times=['Sat 10 AM','Sat 2 PM','Sun 11 AM','Sun 4 PM'];
const node=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(cls)x.className=cls;return x};
function price(x){return new Intl.NumberFormat('en-IN',{style:'currency',currency:x.city==='Dubai'?'AED':'INR',maximumFractionDigits:0}).format(x.price)}
function oneCard(x,admin){
 const root=node('article',undefined,'listing');const icon=node('div',x.intent==='Rent'?'🏢':'🏡','pic');
 const details=node('div');details.append(node('h4',x.title),node('p',x.city+' · '+x.beds+' bedrooms · '+x.intent),node('strong',price(x)));
 const b=node('button',admin?(x.visible?'Published · Hide':'Hidden · Publish'):(selection===x.id?'Selected':'Select for viewing'));b.type='button';
 b.addEventListener('click',()=>{if(admin){x.visible=!x.visible;renderAdmin();renderMatches()}else{selection=x.id;renderMatches()}$('requestResult').hidden=true});details.append(b);root.append(icon,details);return root;
}
function renderMatches(){
 const list=$('matches');list.replaceChildren();
 const intent=$('intent').value,city=$('city').value,budget=Number($('budget').value),beds=Number($('beds').value);
 const found=listings.filter(x=>x.visible&&x.intent===intent&&x.city===city&&x.price<=budget&&x.beds>=beds);
 if(!found.some(x=>x.id===selection))selection=null;
 if(!found.length){list.append(node('p','No matches in our fictional demo collection. Try another budget, city or bedroom count.','status'));return;}
 list.append(node('p',found.length+' matching approved sample listing(s).','muted'));
 found.forEach(x=>list.append(oneCard(x,false)));
}
function renderAdmin(){const target=$('adminListings');target.replaceChildren();listings.forEach(x=>target.append(oneCard(x,true)))}
function renderSlots(){
 for(const [target,admin] of [['buyerSlots',false],['agentSlots',true]]){
  const dest=$(target);dest.replaceChildren();
  times.forEach(t=>{const blockedNow=blocked.has(t);
   const b=node('button',t+(admin?(blockedNow?' · Blocked':' · Available'):(blockedNow?' · Unavailable':'')),'slot');
   b.type='button';
   if(admin)b.addEventListener('click',()=>{if(blockedNow)blocked.delete(t);else blocked.add(t);if(blocked.has(selectedSlot))selectedSlot=null;renderSlots();$('requestResult').hidden=true});
   else {b.disabled=blockedNow;if(selectedSlot===t&&!blockedNow)b.classList.add('selected');b.addEventListener('click',()=>{selectedSlot=t;renderSlots();$('requestResult').hidden=true})}
   dest.append(b);
  })
 }
}
function switchTab(agent){$('agentPanel').hidden=!agent;$('buyerPanel').hidden=agent;$('agentTab').setAttribute('aria-selected',String(agent));$('buyerTab').setAttribute('aria-selected',String(!agent))}
$('agentTab').addEventListener('click',()=>switchTab(true));
$('buyerTab').addEventListener('click',()=>switchTab(false));
$('filterForm').addEventListener('submit',e=>{e.preventDefault();renderMatches();$('requestResult').hidden=true});
$('newListingForm').addEventListener('submit',e=>{
 e.preventDefault();const title=$('newTitle').value.trim(),amount=Number($('newPrice').value);
 if(title.length<4||!Number.isFinite(amount)||amount<1000||amount>20000000)return;
 listings.unshift({id:serial++,title,city:$('newCity').value,intent:$('newIntent').value,price:amount,beds:Number($('newBeds').value),visible:true});
 $('newTitle').value='';renderAdmin();renderMatches();
});
$('request').addEventListener('click',()=>{
 const out=$('requestResult');out.hidden=false;const x=listings.find(y=>y.id===selection&&y.visible);
 if(!x){out.textContent='Select one of the matching sample properties first. No viewing request was created.';return}
 if(!selectedSlot||blocked.has(selectedSlot)){out.textContent='Choose an unblocked sample time first.';return}
 const name=$('buyerName').value.trim().slice(0,50)||'Sample buyer';
 out.textContent='SAMPLE REQUEST PREPARED: '+name+' · '+x.title+' · '+selectedSlot+'. Agent approval would be required. No WhatsApp message, real calendar booking or production CRM update occurred.';
});
$('resetAll').addEventListener('click',()=>{
 listings=initial.map(x=>({...x}));blocked=new Set(['Sat 2 PM','Sun 11 AM']);selection=null;selectedSlot='Sat 10 AM';serial=7;
 $('filterForm').reset();$('newListingForm').reset();$('buyerName').value='';$('requestResult').hidden=true;
 switchTab(false);renderAdmin();renderSlots();renderMatches();
});
renderAdmin();renderSlots();renderMatches();
})();
