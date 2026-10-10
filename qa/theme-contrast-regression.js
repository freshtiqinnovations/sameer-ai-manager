// Run with: FTQ_BASE_URL=https://freshtiqautomation.com node qa/theme-contrast-regression.js
// Requires Playwright and Google Chrome; fails on unreadable content, overlap or broken CTAs.
const {chromium}=require('playwright');
const url=process.env.FTQ_BASE_URL || 'https://freshtiqautomation.com';
const checks=[];
const ok=(val,name,detail='')=>{checks.push({pass:!!val,name,detail});console.log(val?'PASS':'FAIL',name,detail)};
(async()=>{const br=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for (const route of ['/delivery.html','/services.html','/pricing.html','/security.html','/about.html','/contact.html','/partners.html','/']){
 for(const width of [390,1366]){
 const pg=await br.newPage({viewport:{width,height:844},colorScheme:'dark'});
 try{
  await pg.goto(url+route,{waitUntil:'domcontentloaded',timeout:16000});
  await pg.waitForTimeout(480);
  for(const mode of ['light','dark']){
   await pg.evaluate(v=>localStorage.setItem('freshtiq_preferred_theme_v1',v),mode);
   await pg.reload({waitUntil:'domcontentloaded',timeout:14000});await pg.waitForTimeout(300);
   const stats=await pg.evaluate(()=>{
    const sels=['.step-card','.step-card h3','.step-card p','.policy-box','.policy-box strong','.cta-block','.cta-block h3','.cta-block p','.glass-card','.glass-card h3','.glass-card p'];
    const obj={};for(const s of sels){let e=document.querySelector(s);if(e){let g=getComputedStyle(e);obj[s]={fg:g.color,bg:g.backgroundColor,gradient:g.backgroundImage.slice(0,65)}}}
    let badge=document.querySelector('.ftq-made-india'), bubble=document.querySelector('#ft-chat-toggle');
    const nodeData=(e)=>{if(!e)return null;let r=e.getBoundingClientRect();return {display:getComputedStyle(e).display,position:getComputedStyle(e).position,top:r.top,bottom:r.bottom,parent:e.parentElement.tagName,cls:e.className}};
    return {theme:document.documentElement.dataset.ftqTheme,scrollWidth:document.documentElement.scrollWidth,width:innerWidth,colors:obj,badge:nodeData(badge),bubble:nodeData(bubble),strip:!!document.querySelector('.ftq-premium-mobile-actions'),jsReady:!!document.querySelector('#ftq-theme-control')};
   });
   ok(stats.theme===mode,route+' '+width+' '+mode+' theme applied');
   ok(stats.scrollWidth<=width+2,route+' '+width+' '+mode+' no overflow',stats.scrollWidth);
   if(route==='/delivery.html'){
    function color(str){return (str.match(/[\d.]+/g)||[]).slice(0,3).map(Number)}
    function luminance(rgb){let c=rgb.map(x=>x/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return c[0]*.2126+c[1]*.7152+c[2]*.0722}
    function contrast(a,b){let l1=luminance(color(a)),l2=luminance(color(b));return (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05)}
    for(const group of [['.step-card','.step-card h3'],['.step-card','.step-card p'],['.policy-box','.policy-box strong'],['.cta-block','.cta-block h3'],['.cta-block','.cta-block p']]){
     let bg=stats.colors[group[0]]?.bg,fg=stats.colors[group[1]]?.fg,ratio=bg&&fg?contrast(fg,bg):0;
     ok(ratio>=4.5,route+' '+width+' '+mode+' contrast '+group[1],String(Math.round(ratio*100)/100));
    }
    if(width===390){
     ok(stats.badge?.position==='relative'&&stats.badge?.top<600,route+' '+mode+' badge is inline near header',JSON.stringify(stats.badge));
     ok(!stats.bubble||stats.bubble?.display==='none',route+' '+mode+' floating bubble hidden',JSON.stringify(stats.bubble));
     ok(stats.strip,route+' '+mode+' AI and WA mobile strip exists');
     await pg.locator('.ftq-premium-mobile-actions .ftq-open-chat').click({force:true,timeout:1800});
     await pg.waitForTimeout(450);
     ok(await pg.locator('#ft-chat-widget.open').count()===1,route+' '+mode+' AI opens correctly');
     ok((await pg.locator('.ftq-premium-mobile-actions a[href*="wa.me/918381848389"]').count())===1,route+' '+mode+' WhatsApp link present');
    }
   }
   if(route==='/partners.html'&&width===390){ok(stats.badge?.position==='relative',route+' '+mode+' partner badge inline');}
  }
 }catch(e){ok(false,route+' '+width+' tests ran',e.message.slice(0,220))}
 finally{await pg.close()}
 }
}
await br.close();
console.log('FINAL',JSON.stringify({pass:checks.filter(c=>c.pass).length,fail:checks.filter(c=>!c.pass).length}));
if(checks.some(c=>!c.pass))process.exit(1);
})();
