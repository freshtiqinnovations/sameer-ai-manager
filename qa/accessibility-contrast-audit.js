/* Freshtiq color-contrast gate. Run on production or localhost:
     FTQ_BASE_URL=https://freshtiqautomation.com node qa/accessibility-contrast-audit.js
   Requires Node 18+, Playwright, Google Chrome. Reports definite axe-core
   contrast violations in both themes. Incomplete/gradient cases require
   visual review; a zero count is not a guarantee for every pixel. */
const { chromium } = require('playwright');
(async () => {
  const base=(process.env.FTQ_BASE_URL || 'https://freshtiqautomation.com').replace(/\/$/,'');
  const axeUrl='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js';
  const res=await fetch(axeUrl);
  if(!res.ok)throw Error('Unable to obtain axe-core: '+res.status);
  const axe=await res.text();
  const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
  const routes=['/','/delivery.html','/services.html','/partners.html'];
  let failures=0, incomplete=0;
  try{
    for(const route of routes)for(const mode of ['light','dark']){
      const page=await browser.newPage({viewport:{width:390,height:844}});
      try{
        await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:30000});
        await page.evaluate(value=>localStorage.setItem('freshtiq_preferred_theme_v1',value),mode);
        await page.reload({waitUntil:'domcontentloaded',timeout:30000});
        await page.addScriptTag({content:axe});
        const report=await page.evaluate(async()=>axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
        const nodes=report.violations.flatMap(v=>v.nodes);
        failures+=nodes.length;
        incomplete+=report.incomplete.reduce((n,r)=>n+r.nodes.length,0);
        console.log(route,mode,nodes.length+' contrast violations');
        for(const n of nodes)console.log('  '+n.target.join(' ')+' '+n.failureSummary?.slice(0,120));
      }finally{await page.close()}
    }
  }finally{await browser.close()}
  console.log('RESULT',{failures,incomplete});
  if(failures)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2});
