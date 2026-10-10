const{chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const base=process.env.FTQ_BASE_URL||'http://127.0.0.1:8984';
 const profiles=[
  ['phone320',320,320,true],['phone390',390,390,true],['phone430',430,430,true],
  ['inapp980',980,390,true],['tablet768',768,768,true],
  ['laptop1366',1366,1366,false],['desktop1920',1920,1920,false]
 ];
 let pass=0,fail=0;
 const chk=(ok,label,d='')=>{if(ok)pass++;else{fail++;console.log('FAIL',label,JSON.stringify(d).slice(0,260));}};
 for(const [id,width,physical,touch]of profiles){
  const page=await b.newPage({viewport:{width,height:844},screen:{width:physical,height:844},
   isMobile:touch,hasTouch:touch,deviceScaleFactor:touch?2.75:1});
  const errs=[];page.on('pageerror',e=>errs.push(e.message));
  await page.goto(base+'/?verify=polish3',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForTimeout(350);
  const d=await page.evaluate(()=>{
   const el=s=>document.querySelector(s);
   const styles=s=>{let e=el(s);if(!e)return{};const c=getComputedStyle(e),r=e.getBoundingClientRect();return {width:Math.round(r.width),height:Math.round(r.height),font:parseFloat(c.fontSize),display:c.display,grid:c.gridTemplateColumns.split(' ').length,color:c.color,bg:c.backgroundColor}};
   return{width:innerWidth,screen:screen.width,scroll:document.documentElement.scrollWidth,
    theme:document.documentElement.dataset.ftqTheme,compact:document.body.classList.contains('ftq-compact-device-view'),
    nav:styles('#navbar'),navinner:styles('#navbar .nav-inner'),
    logo:styles('#navbar .logo'),burger:styles('#navbar .hamburger'),
    locale:styles('#navbar .ftq-nav-locale'),menulocale:!!el('#navbar .nav-links .ftq-nav-locale'),
    ribbon:styles('.ftq-ad-discovery'),workspace:styles('.ftq-workspace-entry'),
    workspaceCard:styles('.ftq-workspace-entry>a'),mobileLabel:styles('.ftq-workspace-entry>a .ftq-mobile-label'),
    hero:styles('.fx-hero-shell'),h1:styles('.fx-hero-copy h1'),
    cap:styles('.fx-cap-grid'),system:styles('.fx-system-grid'),form:styles('.hero-lead-form'),
    sticky:styles('.sticky-mobile-cta'),ai:styles('#ft-chat-toggle'),
    audit:!!el('#heroLeadForm'),wa:!!el('.sticky-mobile-cta a[href*="wa.me/918381848389"]'),
    lang:!!el('#navbar .ftq-lang-switch'),headline:el('.fx-hero-copy h1')?.innerText.slice(0,70)
   }
  });
  console.log('CASE',id,JSON.stringify(d));
  chk(d.theme==='light',id+' fixed theme');
  chk(d.scroll<=d.width+2,id+' no horizontal overflow',{scroll:d.scroll,width:d.width});
  chk(d.audit&&d.wa&&d.lang,id+' form/whatsapp/language');
  chk(errs.length===0,id+' no JS exception',errs);
  if(physical<=430){
   chk(d.menulocale,id+' language inside menu');
   chk(d.cap.grid===1&&d.system.grid===1&&d.form.grid===1,id+' single column cards/form',d);
   chk(d.workspace.grid===3&&d.mobileLabel.display!=='none',id+' compact workspace',d);
   chk(d.sticky.display!=='none',id+' sticky contacts',d.sticky);
   chk(d.burger.width<=120&&d.nav.height<=140,id+' modest header',d.nav);
   chk(d.h1.font>=29,id+' readable hero',d.h1);
  }
  if(!touch&&width>=1366){
   chk(d.cap.grid>=2&&d.system.grid>=3,id+' laptop grids preserved',d);
   chk(d.nav.height<=95,id+' laptop standard nav',d.nav);
  }
  if(physical<=430){
   try{
    await page.locator('#navbar .hamburger').click({timeout:4000});
    await page.waitForTimeout(130);
    let menu=await page.evaluate(()=>{
     let e=document.querySelector('#navbar .nav-links');const x=e.getBoundingClientRect();
     return{class:e.className,display:getComputedStyle(e).display,box:x.width,aria:document.querySelector('#navbar .hamburger').getAttribute('aria-expanded'),locale:e.querySelector('.ftq-nav-locale')!==null}
    });
    console.log('MENU',id,JSON.stringify(menu));
    chk(menu.box>(id==='inapp980'?850:200)&&menu.locale,id+' nav opens with languages',menu);
    await page.locator('#navbar .hamburger').click({timeout:4000});
   }catch(e){chk(false,id+' hamburger click',e.message)}
  }
  if(['phone390','inapp980','laptop1366'].includes(id)){
   await page.screenshot({path:'/root/workspaces/candidates/freshtiq-ui-polish-20261010/qa/'+id+'-first.png',fullPage:false,timeout:15000});
  }
  await page.close();
 }
 await b.close();
 console.log('TOTAL',{pass,fail});if(fail)process.exitCode=2;
})().catch(e=>{console.error(e);process.exitCode=2})
