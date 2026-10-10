/* Unified Freshtiq marketing UI: fixed theme, mobile grids, in-app browser regression.
 * FTQ_BASE_URL=https://freshtiqautomation.com node qa/theme-contrast-regression.js
 * PASS does not cover external page interactions or every visual asset. */
const {chromium}=require('playwright');
const bUrl=process.env.FTQ_BASE_URL||'https://freshtiqautomation.com';
(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
let n=0,fail=0;
function check(ok,key,detail=''){(ok?n++:fail++);console.log(ok?'PASS':'FAIL',key,detail);}
let configs=[
 {id:'mobile390',viewport:{width:390,height:844},screen:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2.75},
 {id:'small320',viewport:{width:320,height:844},screen:{width:320,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:3},
 {id:'wide700',viewport:{width:700,height:844},screen:{width:700,height:844},isMobile:false,hasTouch:true,deviceScaleFactor:1},
 {id:'phoneDesktop980',viewport:{width:980,height:844},screen:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2.75},
 {id:'desktop980',viewport:{width:980,height:844},screen:{width:980,height:844},isMobile:false,hasTouch:false,deviceScaleFactor:1},
 {id:'desktop1366',viewport:{width:1366,height:900},screen:{width:1366,height:900},isMobile:false,hasTouch:false,deviceScaleFactor:1}
];
for(const cfg of configs){
 for(const path of ['/','/delivery.html','/services.html','/partners.html']){
 let pg=await b.newPage(cfg);let errors=[];
 pg.on('pageerror',err=>errors.push(err.message));
 try{
 await pg.goto(bUrl+path,{waitUntil:'domcontentloaded',timeout:18000});
 await pg.waitForTimeout(220);
 let v=await pg.evaluate(()=>{
 const el=s=>document.querySelector(s);
 const width=e=>e?.getBoundingClientRect().width;
 const grid=s=>{const e=el(s);return e?getComputedStyle(e).gridTemplateColumns.split(' ').length:0};
 return{theme:document.documentElement.dataset.ftqTheme,toggle:!!el('#ftq-theme-control'),compact:document.body.classList.contains('ftq-compact-device-view'),overflow:document.documentElement.scrollWidth-innerWidth,gridCap:grid('.fx-cap-grid'),gridSys:grid('.fx-system-grid'),gridProof:grid('.fx-proof-grid'),gridVal:grid('.fx-value-grid'),gridForm:grid('.hero-lead-form'),fontCard:el('.fx-cap p')?getComputedStyle(el('.fx-cap p')).fontSize:null,sticky:el('.sticky-mobile-cta')?getComputedStyle(el('.sticky-mobile-cta')).display:null,wa:!!el('.sticky-mobile-cta a[href*="wa.me/918381848389"]'),themeCss:document.querySelector('link[href*="freshtiq-unified-theme"]')?.href};
 });
 let pre=cfg.id+' '+path;
 check(v.theme==='light',pre+' fixed unified light',v.theme);
 check(!v.toggle,pre+' no theme button');
 check(v.overflow<=2,pre+' no horizontal overflow',v.overflow);
 check(errors.length===0,pre+' no JS error',errors.slice(0,3).join(';'));
 if(path==='/'){
  let expectedCompact=cfg.id==='phoneDesktop980';
  check(v.compact===expectedCompact,pre+' phone desktop mismatch detected',v.compact);
  if(['mobile390','small320','wide700','phoneDesktop980'].includes(cfg.id)){
   check(v.gridCap===1&&v.gridSys===1&&v.gridProof===1&&v.gridVal===1,pre+' readable single column',JSON.stringify([v.gridCap,v.gridSys,v.gridProof,v.gridVal]));
   check(v.gridForm===1,pre+' lead form single column',v.gridForm);
  }
  if(expectedCompact){
    check(parseFloat(v.fontCard)>25,pre+' phone-desktop fonts enlarged',v.fontCard);
    check(v.sticky!=='none',pre+' mobile sticky contact displayed',v.sticky);
    check(v.wa,pre+' correct WhatsApp link');
  }
  // Bot response and form elements should remain intact.
  check((await pg.locator('#heroLeadForm').count())===1,pre+' lead form intact');
  check((await pg.locator('.ftq-open-chat').count())>=1,pre+' AI contact hook intact');
 }
 await pg.evaluate(()=>localStorage.setItem('freshtiq_preferred_theme_v1','dark'));
 await pg.reload({waitUntil:'domcontentloaded',timeout:15000});
 check((await pg.evaluate(()=>document.documentElement.dataset.ftqTheme))==='light',pre+' old dark setting ignored');
 }catch(err){check(false,cfg.id+' '+path+' execution',String(err).slice(0,260));}
 finally{await pg.close()}
 }
}
await b.close();console.log('SUMMARY',JSON.stringify({passed:n,failed:fail}));if(fail)process.exitCode=2;
})()
