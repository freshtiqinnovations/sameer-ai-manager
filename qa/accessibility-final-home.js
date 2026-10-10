const{chromium}=require('playwright');
(async()=>{
const ax=await(await fetch('https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js')).text();
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const base=process.env.FTQ_BASE_URL||'http://127.0.0.1:8984';
let fail=0;
for(const [id,w,s]of [['mobile390',390,390],['inapp980',980,390],['laptop1366',1366,1366]]){
 let p=await b.newPage({viewport:{width:w,height:844},screen:{width:s,height:844},isMobile:s<700,hasTouch:s<700,deviceScaleFactor:s<700?2.75:1});
 await p.goto(base+'/',{waitUntil:'domcontentloaded'});await p.addScriptTag({content:ax});
 let a=await p.evaluate(async()=>axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
 let nodes=a.violations.flatMap(z=>z.nodes);fail+=nodes.length;
 console.log('AXE',id,nodes.length,a.incomplete.flatMap(z=>z.nodes).length);
 nodes.slice(0,9).forEach(z=>console.log('ISSUE',id,z.target.join(' '),z.failureSummary?.replace(/\n/g,' ').slice(0,140)));
 let options=await p.locator('#ftq-consent button').count();
 if(options){let before=await p.locator('#ftq-consent').count();await p.locator('#ftq-consent button[data-choice="denied"]').click();
  let after=await p.locator('#ftq-consent').count();console.log('PRIVACY',id,before,after);}
 await p.close();
}
await b.close();console.log('RESULT',fail);
if(fail)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2})
