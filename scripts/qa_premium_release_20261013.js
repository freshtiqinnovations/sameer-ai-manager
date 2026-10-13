'use strict';
/* Layout and key-navigation QA. Public GET only; no submissions, no payments. */
const {chromium}=require('/node_modules/playwright');
const BASE=process.env.FTQ_AUDIT_BASE||'http://127.0.0.1:18791';
const PAGES=['/','/services.html','/pricing.html','/about.html','/contact.html','/earn-freshtiq.html','/partners.html','/reviews.html','/talent/'];
const WIDTHS=[360,390,768,1024,1280,1366,1600];
async function main(){
 const b=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[];
 try{
  for(const width of WIDTHS){
   for(const route of PAGES){
    const pg=await b.newPage({viewport:{width,height:850},deviceScaleFactor:1});
    const errors=[];pg.on('pageerror',e=>errors.push(e.message.slice(0,135)));
    await pg.route(/google-analytics\.com|googletagmanager\.com|doubleclick\.net/,r=>r.abort('blockedbyclient'));
    try {
      const response=await pg.goto(BASE+route,{waitUntil:'domcontentloaded',timeout:14000});
      await pg.waitForTimeout(110);
      const nav=pg.locator('#navbar .hamburger');
      const show=await nav.count()>0&&await nav.isVisible();
      if(show)await nav.click({timeout:3000});
      await pg.waitForTimeout(50);
      const x=await pg.evaluate(()=>{
        const nav=document.querySelector('#navbar .nav-links');
        const links=[...(nav?.querySelectorAll('a')||[])];
        const talent=links.find(a=>a.textContent.trim()==='Talent / Freelancer Login');
        const box=talent?.getBoundingClientRect();
        const first=links.find(a=>a.textContent.trim()==='Services');
        const style=first?getComputedStyle(first):null;
        const el=[...document.querySelectorAll('a,button,input,select,textarea')].filter(e=>{
          const r=e.getBoundingClientRect();const cs=getComputedStyle(e);
          return r.width>=10&&r.height>=10&&cs.visibility==='visible'&&cs.display!=='none';
        });
        return {overflowPx:document.documentElement.scrollWidth-innerWidth,
          h1:document.querySelectorAll('h1').length,
          navLinks:links.length,
          navOpen:nav?.classList.contains('open')||false,
          navFontPx:style?parseFloat(style.fontSize):null,
          talentVisible:!!talent &&box?.width>0 && box.left>=-2&&box.right<=innerWidth+2,
          firstMain:!!document.querySelector('main'),
          links:el.length,
          openLinks:links.filter(a=>a.textContent.trim().includes('Login')).length
        };
      });
      const errs=[];
      if(response.status()!==200)errs.push('HTTP_'+response.status());
      if(x.overflowPx>4)errs.push('HORIZONTAL_SCROLL_'+x.overflowPx);
      if(x.h1!==1)errs.push('H1_'+x.h1);
      if(errors.length)errs.push('JS_EXCEPTION_'+errors.length);
      if(route==='/'||route==='/reviews.html'){
        if(x.openLinks!==3)errs.push('LOGIN_ROLE_LINKS_NOT_3');
        if(!x.talentVisible)errs.push('TALENT_LINK_CLIPPED');
        if(width>=1200&&width<=1440&&(!show||!x.navOpen||x.navFontPx<13))errs.push('DESKTOP_DRAWER_CSS_COLLISION');
        if(width>1440&&x.navFontPx<12)errs.push('DESKTOP_FONT_TINY');
      }
      results.push({route,width,http:response.status(),menuToggleVisible:show,...x,errors:errs});
      if(errs.length)console.log('QA_FAIL',route,width,errs.join('|'));
    }catch(e){results.push({route,width,errors:['EXCEPTION_'+e.message.slice(0,180)]});console.log('QA_EXCEPTION',route,width,e.message.slice(0,180))}
    finally{await pg.close()}
   }
  }
 }finally{await b.close()}
 const bad=results.filter(r=>r.errors?.length);
 const summary={timestamp:new Date().toISOString(),site:BASE,tested:results.length,passed:results.length-bad.length,failed:bad.length,byWidth:WIDTHS,byPage:PAGES,failures:bad,results};
 const fs=require('fs');fs.mkdirSync('/tmp/freshtiq_premium_qa',{recursive:true});fs.writeFileSync('/tmp/freshtiq_premium_qa/layout_results.json',JSON.stringify(summary,null,2));
 console.log('PREMIUM_LAYOUT_QA',summary.passed+'/'+summary.tested,'failures',summary.failed,'report=/tmp/freshtiq_premium_qa/layout_results.json');
 if(bad.length)process.exitCode=1;
}
main().catch(e=>{console.error(e.stack);process.exit(1)});
