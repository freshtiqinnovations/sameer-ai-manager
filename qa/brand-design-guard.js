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
// 2026-11-06: Twelve legacy branded detail pages were deliberately retired to\n// noindex redirects. All 106 retained branded pages must keep the master theme.\nassert(pages.length>=106,'Expected >=106 current branded public pages, got '+pages.length);
assert(!pages.some(x=>x.html.includes('freshtiq-global-dark-20261014.css')),'Old global-dark CSS is still linked');
for(const p of pages){
 assert(p.html.split(link).length===2,'Missing/duplicate stylesheet: '+p.name);
 const idx=p.html.indexOf(link),head=p.html.toLowerCase().lastIndexOf('</head>');
 assert(idx>0&&idx<head,'Stylesheet outside head: '+p.name);
 const tail=p.html.slice(idx+link.length,head);
 // The master theme remains required, with a strictly allowlisted final overlay cascade.
 // These are scoped page/locale refinements, not replacements for the master palette.
 const approvedPostMaster=new Set([
   '/freshtiq-brand-unified.css',
   '/freshtiq-page-parity.css',
   '/locale-premium-brand.css',
   '/locale-home-parity.css',
   '/special-premium-brand.css',
   '/seo-international.css'
 ]);
 const postLinks=Array.from(tail.matchAll(/<link\b[^>]*>/gi),m=>m[0])
  .filter(tag=>/rel=["']stylesheet["']/i.test(tag));
 const seen=new Set();
 for(const tag of postLinks){
  const match=tag.match(/href=["']([^"']+)["']/i);
  const href=match&&match[1];
  const pathname=href&&href.split('?')[0];
  assert(!!pathname&&approvedPostMaster.has(pathname),
    'Unapproved stylesheet after master: '+p.name+' -> '+(href||'[missing href]'));
  if(pathname){
   assert(!seen.has(pathname),'Duplicate post-master overlay: '+p.name+' -> '+pathname);
   assert(fs.existsSync(path.join(root,pathname.replace(/^\//,''))),
     'Missing approved overlay file: '+pathname);
   seen.add(pathname);
  }
 }

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
// The full canonical price matrix is retained for historical orders; only eight\n// services may be actively marketed through the public catalogue.\nconst active=['website','whatsapp_ai_sales_bot','customer_support_ai','ai_agent','dashboard_reporting','restaurant_automation','crm_erp','custom_integration'];\nfor(const key of active)assert(read('commercial-pricing.json').includes('"'+key+'"'),'Active service missing from historical pricing: '+key);\nassert((read('services.html').match(/<a class="svc-card"/g)||[]).length===8,'Public services page must show exactly eight services');\nassert((read('index.html').match(/<a class="card" data-match=/g)||[]).length===8,'Homepage must show exactly eight service cards');\nassert((read('pricing.html').match(/<article class="product" data-featured=/g)||[]).length===8,'Pricing page must show exactly eight active products');
console.log(JSON.stringify({guard:'FRESHTIQ_PRICING_MASTER',pass:fail.length===0,pages:pages.length,failures:fail},null,2));
if(fail.length)process.exit(1);