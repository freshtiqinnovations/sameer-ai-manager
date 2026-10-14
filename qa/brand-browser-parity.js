'use strict';
/* Browser brand contract: full public marketing page sweep, both breakpoints.
 * Run: node qa/brand-browser-parity.js [http://127.0.0.1:8197]
 * Requires Playwright/Chrome on test runner. No writes or live customer actions. */
const fs=require('fs'),path=require('path');
const {chromium}=require('/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const base=process.argv[2]||'http://127.0.0.1:8197';
const records=[];
function walk(dir){
 for(const item of fs.readdirSync(dir,{withFileTypes:true})){
  if(['.git','node_modules','backups','staging_pricing_20261013'].includes(item.name))continue;
  const p=path.join(dir,item.name);
  if(item.isDirectory())walk(p);
  else if(item.name.endsWith('.html')){
   const source=fs.readFileSync(p,'utf8');
   const isSecureRedirect=source.includes('http-equiv="refresh"')&&source.includes('portal.freshtiqautomation.com');
   if(source.includes('freshtiq-pricing-master-theme.css')&&!isSecureRedirect)
     records.push('/'+path.relative(root,p).replace(/\\/g,'/'));
  }
 }
}
walk(root);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage']});
 const start=Math.max(0,Number(process.argv[3]||0));
 const limit=Math.max(1,Number(process.argv[4]||records.length));
 let jobs=[];for(const pathname of records.slice(start,start+limit))for(const width of [390,1366])jobs.push({pathname,width});
 const failures=[];let passes=0,next=0;
 async function worker(){
  while(next<jobs.length){
   const job=jobs[next++];let page;
   try{
    page=await browser.newPage({viewport:{width:job.width,height:820}});
    const errs=[];page.on('pageerror',err=>errs.push(err.message));
    const resp=await page.goto(base+job.pathname,{waitUntil:'domcontentloaded',timeout:17000});
    await page.waitForFunction(()=>[...document.styleSheets].some(s=>s.href&&s.href.includes('freshtiq-pricing-master-theme.css')),undefined,{timeout:4500});
    await page.waitForTimeout(60);
    const detail=await page.evaluate(()=>{
     const root=getComputedStyle(document.body);
     const sheets=[...document.styleSheets].filter(s=>s.href&&s.href.includes('freshtiq-pricing-master-theme.css')).length;
     const sample=(sel)=>{const e=document.querySelector(sel);if(!e)return null;const x=getComputedStyle(e);return{x:x.backgroundColor,color:x.webkitTextFillColor||x.color}};
     return{background:root.backgroundColor,css:sheets,overflow:document.documentElement.scrollWidth-innerWidth,
      hero:sample('.fx-hero')||sample('.hero')||sample('.page-header'),card:sample('.fx-cap')||sample('.product')||sample('.insight-index-card')||sample('.card'),
      p:sample('.fx-cap p')||sample('.product p')||sample('.insight-index-card p')||sample('.card p')};
    });
    const good=resp.status()===200&&detail.css===1&&detail.background==='rgb(245, 249, 250)'&&detail.overflow<=10&&errs.length===0;
    if(good)passes++;
    else failures.push({path:job.pathname,width:job.width,status:resp.status(),detail,errors:errs.slice(0,2)});
   }catch(err){failures.push({path:job.pathname,width:job.width,error:err.message.slice(0,170)})}
   finally{if(page)await page.close();}
  }
 }
 await Promise.all(Array.from({length:5},worker));
 await browser.close();
 const report={pages:records.length,cases:jobs.length,passed:passes,failed:failures.length,failures:failures.slice(0,45)};
 console.log('FRESHTIQ_PUBLIC_BRAND_BROWSER_QA '+JSON.stringify(report));
 process.exit(failures.length?2:0);
})().catch(e=>{console.error(e.stack);process.exit(3)});
