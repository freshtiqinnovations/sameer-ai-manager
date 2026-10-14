'use strict';
/* Pricing Page visual identity guard for public marketing pages */
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),pages=[];
const read=(r)=>fs.readFileSync(path.join(root,r),'utf8');
function walk(d){
 for(const a of fs.readdirSync(d,{withFileTypes:true})){
  if(['.git','backups','node_modules','staging_pricing_20261013'].includes(a.name))continue;
  const f=path.join(d,a.name);
  if(a.isDirectory())walk(f);
  else if(a.name.endsWith('.html')){
   const html=fs.readFileSync(f,'utf8');
   if(html.includes('freshtiq-pricing-master-theme.css'))pages.push({name:path.relative(root,f).replace(/\\/g,'/'),html});
  }
 }
}
walk(root);
const css=read('freshtiq-pricing-master-theme.css');
const js=read('freshtiq-premium-experience.js');
const link='/freshtiq-pricing-master-theme.css?v=20261014pricinglock1',fail=[];
function assert(ok,msg){if(!ok)fail.push(msg)}
assert(pages.length>=118,'Expected >=118 branded public pages, got '+pages.length);
assert(!pages.some(x=>x.html.includes('freshtiq-global-dark-20261014.css')),'Old global-dark CSS is still linked');
for(const p of pages){
 assert(p.html.split(link).length===2,'Missing/duplicate stylesheet: '+p.name);
 const idx=p.html.indexOf(link),head=p.html.toLowerCase().lastIndexOf('</head>');
 assert(idx>0&&idx<head,'Stylesheet outside head: '+p.name);
 const tail=p.html.slice(idx+link.length,head);
 assert(!/<link\b[^>]*(?:\.css|stylesheet)/i.test(tail),'Other stylesheet loads after master: '+p.name);
}
assert(js.includes("html.setAttribute('data-ftq-theme','light');"),'Light identity initializer missing');
assert(js.includes("html.style.colorScheme='light';"),'Light color scheme missing');
for(const [token,hex] of Object.entries({
 '--ftq-master-bg':'#F5F9FA',
 '--ftq-master-white':'#FFFFFF',
 '--ftq-master-navy':'#071D2B',
 '--ftq-master-ink':'#102E39',
 '--ftq-master-muted':'#415F68',
 '--ftq-master-teal':'#087A70',
 '--ftq-master-border':'#CCDEDF'
})){
 assert(css.includes(token+':'+hex+';'),'Pricing master palette changed: '+token);
}
assert(read('index.html').includes('document.documentElement.setAttribute("data-ftq-theme","light")'),'Home theme changed');
assert(read('pricing.html').includes('id="amount-website"'),'Price display missing');
assert(read('commercial-pricing.json').includes('"ai_voice_calling"'),'Catalog service missing');
console.log(JSON.stringify({guard:'FRESHTIQ_PRICING_MASTER',pass:fail.length===0,pages:pages.length,failures:fail},null,2));
if(fail.length)process.exit(1);