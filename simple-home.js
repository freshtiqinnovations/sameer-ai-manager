"use strict";
(function(){
 const search=document.getElementById('serviceSearch');
 const popular=[...document.querySelectorAll('#serviceCards .card')];
 const extra=document.getElementById('serviceSearchMore'),none=document.getElementById('noResults');
 const services=[{"key": "website", "name": "Website / Store", "keywords": "website website Mobile-ready business site Lead/contact form"}, {"key": "basic_bot", "name": "Basic WhatsApp Bot", "keywords": "basic bot bot FAQ/auto replies Lead capture"}, {"key": "whatsapp_automation", "name": "WhatsApp Automation", "keywords": "whatsapp automation bot Core WhatsApp workflow Lead/order/booking capture"}, {"key": "whatsapp_ai_sales_bot", "name": "WhatsApp AI Sales Bot", "keywords": "whatsapp ai sales bot bot AI-assisted enquiries Lead capture"}, {"key": "restaurant_automation", "name": "Restaurant Automation", "keywords": "restaurant automation automation QR menu WhatsApp enquiry/order flow"}, {"key": "customer_support_ai", "name": "AI Customer Support Bot", "keywords": "customer support ai ai Knowledge-base answers Ticket/human handoff"}, {"key": "clinic_automation", "name": "Clinic Appointment Automation", "keywords": "clinic automation automation WhatsApp appointment booking Reminders"}, {"key": "travel_automation", "name": "Travel Automation Bot", "keywords": "travel automation automation Travel enquiry capture Package/fare workflow"}, {"key": "crm_erp", "name": "Custom CRM / ERP", "keywords": "crm erp crm Lead/customer records Pipeline/tasks"}, {"key": "field_sales_crm", "name": "Field Sales CRM", "keywords": "field sales crm crm Lead capture Visit logs"}, {"key": "factory_erp", "name": "Factory ERP System", "keywords": "factory erp crm Orders/production queue Inventory"}, {"key": "laundry_system", "name": "Laundry Management System", "keywords": "laundry system automation Order intake Pickup/delivery status"}, {"key": "dashboard_reporting", "name": "Business Dashboard & Reporting", "keywords": "dashboard reporting automation Core KPI dashboard Manual/CSV data sources"}, {"key": "ai_agent", "name": "Custom AI Agent", "keywords": "ai agent ai Business knowledge agent One primary channel"}, {"key": "mobile_app", "name": "Mobile App Development", "keywords": "mobile app app Core mobile workflow Authentication"}, {"key": "custom_integration", "name": "Custom Automation & Integration", "keywords": "custom integration automation One focused workflow Basic integration"}, {"key": "hotel_automation", "name": "Hotel / Hospitality Automation", "keywords": "hotel automation automation Room/package enquiry WhatsApp lead capture"}, {"key": "ecommerce_website", "name": "E-commerce Website / Store", "keywords": "ecommerce website website Product catalog Cart and checkout"}, {"key": "hr_system", "name": "HR & Employee Management System", "keywords": "hr system crm Employee records Attendance/leave workflow"}, {"key": "seo_service", "name": "SEO & Search Growth", "keywords": "seo service marketing Technical/on-page audit Core metadata fixes"}, {"key": "google_business_profile", "name": "Google Business Profile Setup & Growth", "keywords": "google business profile marketing Profile setup/cleanup Business details optimization"}, {"key": "content_marketing", "name": "Content Marketing", "keywords": "content marketing marketing Monthly content plan Core posts/articles"}, {"key": "lead_generation", "name": "Lead Generation Management", "keywords": "lead generation marketing Campaign setup/management Landing/lead tracking guidance"}, {"key": "cloud_hosting", "name": "Cloud Hosting & VPS Management", "keywords": "cloud hosting hosting Basic VPS/hosting management SSL/basic monitoring"}, {"key": "managed_support", "name": "Managed Support & Maintenance", "keywords": "managed support support Routine fixes Basic monitoring"}, {"key": "ai_voice_calling", "name": "AI Voice Calling & Receptionist", "keywords": "ai voice calling ai One approved inbound or opted-in outbound call workflow FAQ / booking / lead capture"}];
 const normalize=s=>String(s||'').toLowerCase().normalize('NFKD').replace(/[–—_\/]+/g,' ').replace(/[^\p{L}\p{N}\s]+/gu,' ').replace(/\s+/g,' ').trim();
 const shown=new Set(popular.map(el=>new URL(el.href,location.origin).searchParams.get('service')).filter(Boolean));
 function render(){
  if(!search)return;
  const q=normalize(search.value),terms=q.split(' ').filter(Boolean);
  if(!q){for(const card of popular)card.hidden=false;extra.replaceChildren();none.hidden=true;return;}
  let found=0;
  for(const card of popular){
   const hay=normalize(card.textContent+' '+(card.dataset.match||'')),ok=terms.every(t=>hay.includes(t));
   card.hidden=!ok;if(ok)found++;
  }
  extra.replaceChildren();
  for(const p of services){
   if(found>=18)break;
   if(shown.has(p.key))continue;
   const hay=normalize(p.name+' '+p.key+' '+p.keywords);
   if(!terms.every(t=>hay.includes(t)))continue;
   const a=document.createElement('a');a.className='card';
   a.href='https://portal.freshtiqautomation.com/store?service='+encodeURIComponent(p.key);
   const icon=document.createElement('span');icon.className='icon';icon.textContent='✦';
   const name=document.createElement('strong');name.textContent=p.name;
   const summary=document.createElement('p');summary.textContent='Compare local packages and request tracked service delivery.';
   a.append(icon,name,summary);extra.append(a);found++;
  }
  none.hidden=found!==0;
 }
 search?.addEventListener('input',render);
 render();
})();