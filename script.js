document.addEventListener('DOMContentLoaded', function() {
const nav = document.querySelector('nav');
if (nav) {
window.addEventListener('scroll', function() {
if (window.scrollY > 50) {
nav.classList.add('scrolled');
} else {
nav.classList.remove('scrolled');
}
});
}
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
if (hamburger && navLinks) {
hamburger.addEventListener('click', function() {
hamburger.classList.toggle('active');
navLinks.classList.toggle('open');
});
navLinks.querySelectorAll('a').forEach(function(link) {
link.addEventListener('click', function() {
hamburger.classList.remove('active');
navLinks.classList.remove('open');
});
});
}
const fadeElements = document.querySelectorAll('.fade-in');
if (fadeElements.length) {
const fadeObserver = new IntersectionObserver(function(entries) {
entries.forEach(function(entry) {
if (entry.isIntersecting) {
entry.target.classList.add('visible');
fadeObserver.unobserve(entry.target);
}
});
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
fadeElements.forEach(function(el) {
fadeObserver.observe(el);
});
}
const track = document.querySelector('.testimonials-track');
const dots = document.querySelectorAll('.dot');
const prevBtn = document.querySelector('.testimonial-arrow.prev');
const nextBtn = document.querySelector('.testimonial-arrow.next');
let currentIndex = 0;
function updateCarousel() {
if (!track) return;
var totalSlides = track.children.length;
if (totalSlides === 0) return;
if (currentIndex < 0) currentIndex = totalSlides - 1;
if (currentIndex >= totalSlides) currentIndex = 0;
track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
dots.forEach(function(d, i) {
d.classList.toggle('active', i === currentIndex);
});
}
if (prevBtn) {
prevBtn.addEventListener('click', function() {
currentIndex--;
updateCarousel();
});
}
if (nextBtn) {
nextBtn.addEventListener('click', function() {
currentIndex++;
updateCarousel();
});
}
dots.forEach(function(dot, i) {
dot.addEventListener('click', function() {
currentIndex = i;
updateCarousel();
});
});
var autoRotate;
if (track && track.children.length > 1) {
autoRotate = setInterval(function() {
currentIndex++;
updateCarousel();
}, 5000);
var slider = document.querySelector('.testimonials-slider');
if (slider) {
slider.addEventListener('mouseenter', function() {
clearInterval(autoRotate);
});
slider.addEventListener('mouseleave', function() {
autoRotate = setInterval(function() {
currentIndex++;
updateCarousel();
}, 5000);
});
}
}
updateCarousel();
document.querySelectorAll('.copy-btn').forEach(function(btn) {
btn.addEventListener('click', function() {
var target = this.getAttribute('data-copy');
if (target) {
if (navigator.clipboard && navigator.clipboard.writeText) {
navigator.clipboard.writeText(target).then(function() {
var original = btn.textContent;
btn.textContent = 'Copied!';
setTimeout(function() {
btn.textContent = original;
}, 2000);
});
} else {
var textarea = document.createElement('textarea');
textarea.value = target;
document.body.appendChild(textarea);
textarea.select();
document.execCommand('copy');
document.body.removeChild(textarea);
var original = btn.textContent;
btn.textContent = 'Copied!';
setTimeout(function() {
btn.textContent = original;
}, 2000);
}
}
});
});
});
function trackProject() {
const id = document.getElementById('projectId').value.trim();
const steps = ['📥 Received','📋 Planning','🔧 Development','🧪 Testing','✅ Delivered'];
const statusIndex = 2; 
let html = '<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">';
steps.forEach((s, i) => {
const isActive = i <= statusIndex;
const bg = isActive ? 'var(--gradient)' : '#e2e8f0';
const color = isActive ? 'white' : '#7a7a9a';
html += '<div style="flex:1;min-width:100px;padding:16px 12px;background:' + bg + ';color:' + color + ';border-radius:10px;text-align:center;font-weight:600;font-size:0.85rem;">' + s + '</div>';
});
html += '</div><p style="margin-top:16px;text-align:center;color:#4a4a6a;"><strong>' + id + '</strong> is currently in <strong>Development</strong> phase. Status updates every 24h.</p>';
document.getElementById('trackerResult').innerHTML = html;
}
function generateQuote() {
const name = document.getElementById('qName').value || 'Client';
const phone = document.getElementById('qPhone').value || '—';
const email = document.getElementById('qEmail').value || '—';  
const type = document.getElementById('qType').value;
const budget = document.getElementById('qBudget').value;
const types = {'website':'Website','app':'Mobile App','bot':'AI Chatbot','whatsapp':'WhatsApp Automation','erp':'ERP System','crm':'CRM System'};
const budgets = {'5k-10k':'₹5,000 – ₹10,000','10k-25k':'₹10,000 – ₹25,000','25k-50k':'₹25,000 – ₹50,000','50k+':'₹50,000+'};
if(!type || !budget) {
document.getElementById('quoteResult').innerHTML = '<p style="color:#dc2626;text-align:center;">Please select project type and budget.</p>';
return;
}
const t = types[type] || type;
const b = budgets[budget] || budget;
const estimate = budget === '5k-10k' ? '₹6,999' : budget === '10k-25k' ? '₹14,999' : budget === '25k-50k' ? '₹34,999' : '₹54,999+';
const delivery = type === 'bot' || type === 'whatsapp' ? '24–48 hours' : '3–10 days';
document.getElementById('quoteResult').innerHTML = `
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-top:10px;">
<h4 style="color:#1a1a2e;margin-bottom:12px;">📋 Quote Summary</h4>
<table style="width:100%;font-size:0.85rem;">
<tr><td style="padding:6px 0;color:#7a7a9a;">Client</td><td style="font-weight:600;">${name}</td></tr>
<tr><td style="padding:6px 0;color:#7a7a9a;">Project</td><td style="font-weight:600;">${t}</td></tr>
<tr><td style="padding:6px 0;color:#7a7a9a;">Estimate</td><td style="font-weight:600;color:#1a73e8;">${estimate}</td></tr>
<tr><td style="padding:6px 0;color:#7a7a9a;">Delivery</td><td style="font-weight:600;">${delivery}</td></tr>
</table>
<a href="https://wa.me/918381848389?text=Hi!%20I%20need%20a%20${t}%20project.%20Budget%20${b}.%20Name:%20${name}" target="_blank" rel="noopener" style="display:block;text-align:center;margin-top:14px;padding:12px;background:#25D366;color:white;border-radius:8px;text-decoration:none;font-weight:600;">💬 Send Quote on WhatsApp</a>
</div>
`;
}
document.addEventListener('DOMContentLoaded', function() {
if(typeof trackProject === 'function') {
try { trackProject(); } catch(e) {  }
}
});
function handleSalesConsult() {
const name = document.getElementById('salesName').value.trim();
const phone = document.getElementById('salesPhone').value.trim();
const project = document.getElementById('salesProject').value;
const budget = document.getElementById('salesBudget').value;
const timeline = document.getElementById('salesTimeline').value;
const idea = document.getElementById('salesIdea').value.trim();
if (!name || !phone || !project || !budget || !timeline) {
document.getElementById('salesResult').style.display = 'block';
document.getElementById('salesResult').innerHTML = '<p style="color:#dc2626;text-align:center;">Please fill all required fields (Name, WhatsApp, Project, Budget, Timeline).</p>';
return;
}
const packages = {
'website': { name: 'Starter Website Package', price: '₹4,999', desc: 'Professional responsive website with contact form, WhatsApp integration, and hosting.' },
'app': { name: 'Mobile App Package', price: '₹9,999', desc: 'Cross-platform mobile app with backend API, notifications, and dashboard.' },
'bot': { name: 'AI Bot Package', price: '₹1,999', desc: 'Custom Telegram/WhatsApp bot with AI responses, commands, and admin panel.' },
'erp': { name: 'Enterprise ERP Package', price: '₹19,999', desc: 'Full ERP system with inventory, sales, HR, accounting, and WhatsApp reports.' },
'crm': { name: 'Business CRM Package', price: '₹9,999', desc: 'CRM with lead tracking, sales pipeline, customer portal, and WhatsApp integration.' },
'travel': { name: 'Travel Portal Package', price: '₹14,999', desc: 'Travel booking portal with flights, hotels, visa info, and payment gateway.' },
'ai': { name: 'AI Automation Package', price: '₹3,999', desc: 'Custom AI automation workflow, data extraction, and decision engine.' },
'other': { name: 'Custom Solution Package', price: 'Contact Us', desc: 'Tell us more and we will build the perfect solution for your business.' }
};
const timelineTexts = {
'24h': '24 hours',
'3-7d': '3–7 days',
'7-15d': '7–15 days',
'15d+': '15+ days'
};
const pkg = packages[project] || packages['other'];
const estTime = timelineTexts[timeline] || '7–15 days';
const msg = encodeURIComponent(
`Hi Freshtiq Automation! I need a ${project}. Budget ${budget}. Timeline ${estTime}. Idea: ${idea || 'Tell me more'}. Name: ${name}`
);
document.getElementById('salesResult').style.display = 'block';
document.getElementById('salesResult').innerHTML = `
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
<span style="font-size:1.5rem;">🤖</span>
<div>
<h4 style="color:#1a1a2e;margin:0;font-size:1rem;">FRESHTIQ AI CONSULTANT</h4>
<p style="color:#7a7a9a;font-size:0.78rem;margin:2px 0 0;">FRESHTIQ INNOVATIONS (OPC) PRIVATE LIMITED</p>
</div>
</div>
<div style="background:linear-gradient(135deg,#f0f4ff,#f5f0ff);border-radius:10px;padding:16px;margin-bottom:14px;">
<p style="color:#1a1a2e;font-size:0.9rem;margin:0 0 8px;">📋 <strong>Recommendation:</strong></p>
<p style="color:#1a73e8;font-size:1.05rem;font-weight:700;margin:0 0 4px;">${pkg.name}</p>
<p style="color:#7c3aed;font-size:0.95rem;font-weight:600;margin:0 0 8px;">Estimated: ${pkg.price}</p>
<p style="color:#4a4a6a;font-size:0.82rem;margin:0;">${pkg.desc}</p>
<p style="color:#4a4a6a;font-size:0.82rem;margin:8px 0 0;">⏱️ Timeline: <strong>${estTime}</strong></p>
</div>
<p style="color:#6b7280;font-size:0.82rem;text-align:center;margin:0 0 14px;">Your request is ready. Click below to continue.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;">
<a href="https://wa.me/918381848389?text=${msg}" target="_blank" rel="noopener" style="flex:1;min-width:150px;padding:12px;background:#25D366;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">💬 Continue on WhatsApp</a>
<a href="https://t.me/AutoPilotHubBot" target="_blank" style="flex:1;min-width:150px;padding:12px;background:#0088cc;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">📱 Start on Telegram</a>
<a href="https://wa.me/918381848389?text=Hi%20Freshtiq!%20Please%20call%20me%20back.%20${name}%20${phone}" target="_blank" rel="noopener" style="flex:1;min-width:150px;padding:12px;background:var(--gradient);color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">📞 Request Call Back</a>
</div>
</div>
`;
}
function calculateROI() {
const hours = parseFloat(document.getElementById('roiHours').value) || 0;
const staffCost = parseFloat(document.getElementById('roiStaffCost').value) || 0;
const leads = parseFloat(document.getElementById('roiLeads').value) || 0;
const revenue = parseFloat(document.getElementById('roiRevenue').value) || 0;
if (hours < 1 || staffCost < 1) {
document.getElementById('roiResult').innerHTML = '<div style="text-align:center;padding:20px;"><p style="color:#dc2626;">Please enter valid hours and staff cost.</p></div>';
return;
}
const workingDays = 26;
const monthlyHours = hours * workingDays;
const automatedPct = hours <= 4 ? 80 : hours <= 8 ? 65 : 50;
const timeSaved = Math.round(monthlyHours * automatedPct / 100);
const costSaved = Math.round(staffCost * automatedPct / 100);
const leadConversionRate = 0.15;
const currentConversions = Math.round(leads * leadConversionRate);
const improvedConversions = Math.round(leads * leadConversionRate * 1.8);
const extraLeads = improvedConversions - currentConversions;
const avgOrderValue = leads > 0 ? Math.round(revenue / leads) : 500;
const revenueImprovement = extraLeads * avgOrderValue;
let pkgName, pkgPrice, pkgLink;
if (hours <= 4 && staffCost <= 10000) {
pkgName = 'AI Chatbot (₹1,999)';
pkgPrice = '₹1,999';
pkgLink = 'services.html';
} else if (hours <= 8 && staffCost <= 25000) {
pkgName = 'WhatsApp Automation (₹2,999)';
pkgPrice = '₹2,999';
pkgLink = 'services.html';
} else if (staffCost <= 50000) {
pkgName = 'Website + CRM (₹9,999+)';
pkgPrice = '₹9,999+';
pkgLink = 'services.html';
} else {
pkgName = 'Custom ERP/CRM (₹19,999+)';
pkgPrice = '₹19,999+';
pkgLink = 'services.html';
}
const msg = encodeURIComponent(
`Hi Freshtiq! I calculated my ROI: ${timeSaved}h/month time saved, ₹${costSaved.toLocaleString('en-IN')}/month cost saving, ₹${revenueImprovement.toLocaleString('en-IN')} potential revenue. Recommended: ${pkgName}. Please contact me.`
);
document.getElementById('roiResult').innerHTML = `
<div>
<h4 style="color:#1a1a2e;margin:0 0 14px;font-size:1rem;">📈 Your Estimated Savings</h4>
<div style="display:grid;gap:10px;">
<div style="background:#f0f4ff;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:0.82rem;color:#4a4a6a;">⏱️ Time Saved / Month</span>
<span style="font-weight:700;color:#1a73e8;">${timeSaved}h</span>
</div>
<div style="background:#f0f4ff;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:0.82rem;color:#4a4a6a;">💰 Cost Saving / Month</span>
<span style="font-weight:700;color:#1a73e8;">₹${costSaved.toLocaleString('en-IN')}</span>
</div>
<div style="background:#f5f0ff;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
<span style="font-size:0.82rem;color:#4a4a6a;">📊 Potential Revenue Improvement</span>
<span style="font-weight:700;color:#7c3aed;">₹${revenueImprovement.toLocaleString('en-IN')}/mo</span>
</div>
<div style="background:linear-gradient(135deg,#f0f4ff,#f5f0ff);border-radius:8px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
<span style="font-size:0.85rem;color:#1a1a2e;font-weight:600;">🎯 Recommended</span>
<span style="font-weight:700;color:#7c3aed;font-size:0.9rem;">${pkgName}</span>
</div>
</div>
<a href="https://wa.me/918381848389?text=${msg}" target="_blank" rel="noopener" style="display:block;margin-top:14px;padding:12px;background:#25D366;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">💬 Get This Quote on WhatsApp</a>
</div>
`;
}
function trackProjectDash() {
const id = document.getElementById('dashProjectId').value.trim();
if (!id) {
document.getElementById('dashResult').innerHTML = '<p style="color:#dc2626;text-align:center;">Please enter a Project ID.</p>';
return;
}
const steps = ['📥 Received', '📋 Planning', '🔧 Development', '🧪 Testing', '✅ Delivered'];
const statusIndex = 2; 
let html = '<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">';
steps.forEach((s, i) => {
const active = i <= statusIndex;
const bg = active ? 'var(--gradient)' : '#e2e8f0';
const color = active ? 'white' : '#7a7a9a';
html += '<div style="flex:1;min-width:80px;padding:14px 8px;background:' + bg + ';color:' + color + ';border-radius:8px;text-align:center;font-weight:600;font-size:0.78rem;">' + s + '</div>';
});
html += '</div>';
const phase = steps[statusIndex];
html += '<div style="margin-top:16px;padding:14px 18px;background:#f0f4ff;border-radius:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">';
html += '<div><p style="margin:0;font-size:0.82rem;color:#4a4a6a;"><strong style="color:#1a73e8;">' + id + '</strong> — Currently in <strong style="color:#7c3aed;">' + phase + '</strong> phase</p>';
html += '<p style="margin:4px 0 0;font-size:0.75rem;color:#7a7a9a;">Status updates every 24h &bull; Track on Telegram for live notifications.</p></div>';
html += '<span style="background:#1a73e8;color:white;padding:4px 12px;border-radius:20px;font-size:0.7rem;font-weight:600;">🔴 In Progress</span></div>';
document.getElementById('dashResult').innerHTML = html;
}
function openClawRecommend() {
const project = document.getElementById('salesProject').value;
const budget = document.getElementById('salesBudget').value;
const timeline = document.getElementById('salesTimeline').value;
const idea = document.getElementById('salesIdea').value.trim();
const recs = {
'website': {
'less10': { pkg: 'Starter Web Package', cost: '₹4,999 - ₹9,999', days: '3-5 Days', tech: 'HTML, CSS, JS, WhatsApp Integration, Hosting', team: '1 Developer + 1 Designer' },
'10to25': { pkg: 'Business Web Package', cost: '₹10,000 - ₹24,999', days: '5-7 Days', tech: 'HTML/CSS/JS, WhatsApp API, Telegram Bot, Admin Panel', team: '2 Developers + 1 Designer' },
'25to50': { pkg: 'Premium Web Package', cost: '₹25,000 - ₹49,999', days: '7-14 Days', tech: 'React/Angular, Python Backend, PostgreSQL, WhatsApp/Telegram, Dashboard', team: '2 Developers + 1 QA' },
'more50': { pkg: 'Enterprise Web Package', cost: '₹50,000+', days: '14-30 Days', tech: 'Full Stack, AI Integration, Multi-language, Real-time Dashboard', team: '3 Developers + 1 QA + 1 PM' }
},
'bot': {
'less10': { pkg: 'Basic Bot', cost: '₹1,999 - ₹4,999', days: '1-2 Days', tech: 'Python, Telegram API, Basic Commands', team: '1 Developer' },
'10to25': { pkg: 'AI Bot Package', cost: '₹5,000 - ₹14,999', days: '3-5 Days', tech: 'Python, OpenAI/GPT, Telegram/WhatsApp, Admin Panel', team: '1 Developer + 1 AI Engineer' },
'25to50': { pkg: 'Advanced Bot Suite', cost: '₹15,000 - ₹29,999', days: '5-10 Days', tech: 'Python, Multi-Platform, AI, Payment Integration, Analytics', team: '2 Developers + 1 AI Engineer' },
'more50': { pkg: 'Enterprise Bot Factory', cost: '₹30,000+', days: '10-20 Days', tech: 'Custom Protocol, Multi-bot Architecture, ML Pipeline', team: '2 Developers + 1 ML Engineer' }
},
'erp': {
'less10': { pkg: 'Mini ERP Lite', cost: '₹9,999 - ₹19,999', days: '7-14 Days', tech: 'Python, SQLite, Basic Dashboard', team: '1 Developer + 1 Data Analyst' },
'10to25': { pkg: 'Business ERP', cost: '₹20,000 - ₹49,999', days: '14-21 Days', tech: 'Python, PostgreSQL, Inventory, Sales, HR Modules', team: '2 Developers + 1 Tester' },
'25to50': { pkg: 'Premium ERP', cost: '₹50,000 - ₹99,999', days: '21-30 Days', tech: 'Python, PostgreSQL, Full Modules, WhatsApp Reports, API', team: '3 Developers + 1 QA + 1 BA' },
'more50': { pkg: 'Enterprise AI ERP PRO', cost: '₹1,00,000+', days: '30-60 Days', tech: 'Python, PostgreSQL, AI Predictions, Multi-Branch, Real-time', team: '4 Developers + 1 PM + 1 QA' }
},
'crm': {
'less10': { pkg: 'CRM Starter', cost: '₹4,999 - ₹9,999', days: '3-7 Days', tech: 'Python, SQLite, Lead Tracking, Telegram Alerts', team: '1 Developer' },
'10to25': { pkg: 'CRM Business', cost: '₹10,000 - ₹29,999', days: '7-14 Days', tech: 'Python, PostgreSQL, Pipeline, Analytics, WhatsApp', team: '2 Developers + 1 Tester' },
'25to50': { pkg: 'CRM Enterprise', cost: '₹30,000 - ₹59,999', days: '14-21 Days', tech: 'Python, PostgreSQL, Automation, Reports, Multi-user', team: '2 Developers + 1 QA' },
'more50': { pkg: 'CRM Suite PRO', cost: '₹60,000+', days: '21-45 Days', tech: 'Full Stack, AI Lead Scoring, Auto-campaigns, API', team: '3 Developers + 1 AI Engineer' }
},
'app': {
'less10': { pkg: 'Basic App', cost: '₹9,999 - ₹19,999', days: '7-14 Days', tech: 'React Native, Firebase, Basic UI', team: '1 Developer + 1 Designer' },
'10to25': { pkg: 'Business App', cost: '₹20,000 - ₹49,999', days: '14-21 Days', tech: 'React Native/Flutter, Python Backend, Notifications', team: '2 Developers + 1 Designer' },
'25to50': { pkg: 'Premium App Suite', cost: '₹50,000 - ₹99,999', days: '21-35 Days', tech: 'Flutter/React, PostgreSQL, NLP, Admin Panel', team: '2 Developers + 1 QA + 1 Designer' },
'more50': { pkg: 'Enterprise App PRO', cost: '₹1,00,000+', days: '30-60 Days', tech: 'Full Stack, AI, Multi-platform, Real-time Sync', team: '3 Developers + 1 QA + 1 PM' }
}
};
const budgetMap = { 'less10': 'less10', '10to25': '10to25', '25to50': '25to50', 'more50': 'more50' };
const b = budgetMap[budget] || 'less10';
const rec = recs[project] && recs[project][b] ? recs[project][b] : recs['website']['less10'];
const budgetScore = { 'less10': 30, '10to25': 50, '25to50': 75, 'more50': 100 };
const projectScore = idea.length > 20 ? 25 : 10;
const timelineScore = { '1week': 0, '2weeks': 5, '1month': 10, 'flexible': 20 };
const totalScore = (budgetScore[budget] || 30) + projectScore + (timelineScore[timeline] || 0);
const score = Math.min(100, totalScore);
let label, color;
if (score >= 80) { label = 'Hot Lead'; color = '#16a34a'; }
else if (score >= 50) { label = 'Warm Lead'; color = '#d97706'; }
else { label = 'Cold Lead'; color = '#dc2626'; }
const proposalText = `PROJECT: ${rec.pkg}\nDESCRIPTION: ${idea || project.toUpperCase()} Automation Solution\nDELIVERABLES: ${rec.tech}\nTIMELINE: ${rec.days}\nTEAM: ${rec.team}\nESTIMATED COST: ${rec.cost}\nLEAD SCORE: ${score}/100 - ${label}\n\nPowered by OpenClaw — Freshtiq Automation`;
const resultDiv = document.getElementById('salesResult');
resultDiv.style.display = 'block';
resultDiv.innerHTML = `
<div style="background:white;border-radius:12px;padding:20px;border:1px solid #e2e8f0;text-align:left;">
<div style="background:linear-gradient(135deg,#1a73e8,#7c3aed);margin:-20px -20px 16px;padding:14px 20px;border-radius:12px 12px 0 0;">
<span style="color:white;font-weight:700;font-size:0.9rem;">OPENCLAW AI CONSULTANT — RECOMMENDATION</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
<div style="background:#f0f4ff;padding:12px;border-radius:8px;"><span style="font-size:0.7rem;color:#7a7a9a;">RECOMMENDED PACKAGE</span><p style="margin:4px 0 0;font-weight:700;color:#1a1a2e;font-size:0.85rem;">${rec.pkg}</p></div>
<div style="background:#f5f0ff;padding:12px;border-radius:8px;"><span style="font-size:0.7rem;color:#7a7a9a;">ESTIMATED COST</span><p style="margin:4px 0 0;font-weight:700;color:#7c3aed;font-size:0.85rem;">${rec.cost}</p></div>
<div style="background:#f0f4ff;padding:12px;border-radius:8px;"><span style="font-size:0.7rem;color:#7a7a9a;">DELIVERY TIME</span><p style="margin:4px 0 0;font-weight:700;color:#1a1a2e;font-size:0.85rem;">${rec.days}</p></div>
<div style="background:#f5f0ff;padding:12px;border-radius:8px;"><span style="font-size:0.7rem;color:#7a7a9a;">LEAD SCORE</span><p style="margin:4px 0 0;font-weight:700;font-size:0.85rem;"><span style="color:${color};">${score}/100 — ${label}</span></p></div>
</div>
<div style="margin-bottom:12px;">
<p style="font-size:0.7rem;color:#7a7a9a;margin:0 0 4px;">PROJECT SUMMARY</p>
<div style="font-size:0.78rem;color:#4a4a6a;background:#f8f9fc;padding:12px;border-radius:8px;line-height:1.6;">
<strong>Package:</strong> ${rec.pkg}<br>
<strong>Cost:</strong> ${rec.cost}<br>
<strong>Delivery:</strong> ${rec.days}<br>
<strong>Tech Stack:</strong> ${rec.tech}<br>
<strong>Team:</strong> ${rec.team}
</div>
</div>
<div style="display:flex;gap:8px;flex-wrap:wrap;">
<a href="https://wa.me/918381848389?text=${encodeURIComponent(proposalText)}" target="_blank" rel="noopener" style="flex:1;min-width:120px;padding:10px;background:#25D366;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.78rem;">💬 Continue on WhatsApp</a>
<a href="https://t.me/AutoPilotHubBot" target="_blank" style="flex:1;min-width:120px;padding:10px;background:#0088cc;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.78rem;">📱 Continue on Telegram</a>
<a href="tel:+918381848389" style="flex:1;min-width:120px;padding:10px;background:var(--gradient);color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.78rem;">📞 Request Callback</a>
</div>
</div>
`;
}
async function submitLeadToAPI(project, budget, timeline, name, phone) {
if (!name || !phone) return null;
const id = 'APH' + new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0, 17) + '-' + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
const score = Math.min(100, (budget === 'more50' ? 100 : budget === '25to50' ? 75 : budget === '10to25' ? 50 : 30) + (name.length > 0 ? 20 : 0));
const label = score >= 80 ? 'Hot' : score >= 50 ? 'Warm' : 'Cold';
try {
const resp = await fetch('https://freshtiqautomation.in/api/lead', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({
lead_id: id,
source: 'OpenClaw Consultant',
name: name,
phone: phone,
project: project,
budget: budget,
timeline: timeline,
score: score,
label: label
})
});
return id;
} catch(e) {
console.log('Lead saved locally (API offline):', id);
return id;
}
}
function startPricingCarousel() {
const cards = document.querySelectorAll('.pricing-card');
const dots = document.querySelectorAll('#pricingDots .dot');
if (!cards.length) return;
let current = 0;
cards.forEach(c => c.classList.remove('active-highlight'));
cards[0]?.classList.add('active-highlight');
if (dots.length) {
dots.forEach((d,i) => d.style.background = i === 0 ? '#1a73e8' : '#d1d5db');
}
let interval = setInterval(() => {
cards.forEach(c => c.classList.remove('active-highlight'));
current = (current + 1) % cards.length;
cards[current].classList.add('active-highlight');
if (dots.length) {
dots.forEach((d,i) => d.style.background = i === current ? '#1a73e8' : '#d1d5db');
}
}, 2500);
cards.forEach(c => {
c.addEventListener('mouseenter', () => clearInterval(interval));
c.addEventListener('mouseleave', () => {
interval = setInterval(() => {
cards.forEach(c2 => c2.classList.remove('active-highlight'));
current = (current + 1) % cards.length;
cards[current].classList.add('active-highlight');
if (dots.length) {
dots.forEach((d,i) => d.style.background = i === current ? '#1a73e8' : '#d1d5db');
}
}, 2500);
});
});
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startPricingCarousel);
} else {
  startPricingCarousel();
}
function showToast(msg) {
var toast = document.createElement('div');
toast.textContent = msg;
toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1a1a2e;color:white;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999;box-shadow:0 4px 20px rgba(0,0,0,0.15);animation:fadeIn 0.3s;';
document.body.appendChild(toast);
setTimeout(function() {
toast.style.opacity = '0';
toast.style.transition = 'opacity 0.3s';
setTimeout(function() { toast.remove(); }, 300);
}, 2500);
}
var style = document.createElement('style');
style.textContent = '@keyframes fadeIn { from { opacity:0; transform:translateX(-50%) translateY(10px); } to { opacity:1; transform:translateX(-50%) translateY(0); } }';
document.head.appendChild(style);
