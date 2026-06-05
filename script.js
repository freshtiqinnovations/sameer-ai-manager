/* ========================================
   FRESHTIQ AUTOMATION - JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {

  // ============= NAV SCROLL EFFECT =============
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

  // ============= HAMBURGER MENU =============
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
      });
    });
  }

  // ============= FADE-IN ON SCROLL =============
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

  // ============= TESTIMONIAL CAROUSEL =============
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

  // Auto-rotate carousel
  var autoRotate;
  if (track && track.children.length > 1) {
    autoRotate = setInterval(function() {
      currentIndex++;
      updateCarousel();
    }, 5000);

    // Pause on hover
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

  // Initialize
  updateCarousel();

  // ============= COPY BUTTONS =============
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
          // Fallback
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

// ============= PROJECT TRACKER =============
function trackProject() {
  const id = document.getElementById('projectId').value.trim();
  const steps = ['📥 Received','📋 Planning','🔧 Development','🧪 Testing','✅ Delivered'];
  const statusIndex = 2; // Development
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

// ============= AI QUOTE GENERATOR =============
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
      <a href="https://wa.me/918381848389?text=Hi!%20I%20need%20a%20${t}%20project.%20Budget%20${b}.%20Name:%20${name}" target="_blank" style="display:block;text-align:center;margin-top:14px;padding:12px;background:#25D366;color:white;border-radius:8px;text-decoration:none;font-weight:600;">💬 Send Quote on WhatsApp</a>
    </div>
  `;
}

// Auto-run project tracker on page load
document.addEventListener('DOMContentLoaded', function() {
  if(typeof trackProject === 'function') {
    try { trackProject(); } catch(e) { /* tracker may not exist on this page */ }
  }
});


/* ===== AI Sales Assistant ===== */
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

  // Package suggestions
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
        <a href="https://wa.me/918381848389?text=${msg}" target="_blank" style="flex:1;min-width:150px;padding:12px;background:#25D366;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">💬 Continue on WhatsApp</a>
        <a href="https://t.me/AutoPilotHubBot" target="_blank" style="flex:1;min-width:150px;padding:12px;background:#0088cc;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">📱 Start on Telegram</a>
        <a href="https://wa.me/918381848389?text=Hi%20Freshtiq!%20Please%20call%20me%20back.%20${name}%20${phone}" target="_blank" style="flex:1;min-width:150px;padding:12px;background:var(--gradient);color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">📞 Request Call Back</a>
      </div>
    </div>
  `;
}


/* ===== ROI Calculator ===== */
function calculateROI() {
  const hours = parseFloat(document.getElementById('roiHours').value) || 0;
  const staffCost = parseFloat(document.getElementById('roiStaffCost').value) || 0;
  const leads = parseFloat(document.getElementById('roiLeads').value) || 0;
  const revenue = parseFloat(document.getElementById('roiRevenue').value) || 0;

  if (hours < 1 || staffCost < 1) {
    document.getElementById('roiResult').innerHTML = '<div style="text-align:center;padding:20px;"><p style="color:#dc2626;">Please enter valid hours and staff cost.</p></div>';
    return;
  }

  // Calculations
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

  // Package recommendation
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
      <a href="https://wa.me/918381848389?text=${msg}" target="_blank" style="display:block;margin-top:14px;padding:12px;background:#25D366;color:white;border-radius:8px;text-align:center;text-decoration:none;font-weight:600;font-size:0.85rem;">💬 Get This Quote on WhatsApp</a>
    </div>
  `;
}
