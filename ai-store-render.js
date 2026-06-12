// Freshtiq AI Store — Render Engine
(function() {
  const grid = document.getElementById('storeGrid');
  const count = document.getElementById('storeCount');
  const empty = document.getElementById('storeEmpty');
  let currentFilter = 'all';

  function getWAUrl(product) {
    return 'https://wa.me/918381848389?text=I%20want%20' + encodeURIComponent(product.title) + '%2C%20please%20send%20details.';
  }

  function getQuoteWA(product) {
    return 'https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20want%20a%20quote%20for%20' + encodeURIComponent(product.title) + '.';
  }

  function renderProducts(products) {
    grid.innerHTML = '';

    if (products.length === 0) {
      empty.classList.add('visible');
      count.textContent = '0';
      return;
    }
    empty.classList.remove('visible');
    count.textContent = products.length;

    products.forEach(p => {
      const hasTag = p.tags && p.tags.length > 0;
      const popular = hasTag && p.tags.includes('popular');
      const premium = hasTag && p.tags.includes('premium');

      const card = document.createElement('div');
      card.className = 'store-card reveal';
      card.innerHTML = `
        ${popular ? '<span class="store-card-badge popular">⭐ Popular</span>' : ''}
        ${premium ? '<span class="store-card-badge premium">💎 Premium</span>' : ''}
        <div class="icon">${p.icon || '🛒'}</div>
        <h3>${p.title}</h3>
        <div class="desc">${p.description}</div>
        <div class="store-card-price">
          <div>
            <div class="main">${p.price}</div>
          </div>
          <div class="sub">
            ${p.monthly ? '<strong>Support:</strong> ' + p.monthly : ''}
            <div class="delivery"><strong>📅</strong> ${p.delivery}</div>
          </div>
        </div>
        <div class="store-card-actions" style="display:flex;flex-wrap:wrap;gap:6px;">
          <a href="${getWAUrl(p)}" target="_blank" class="store-wa-btn" style="background:#6C63FF;color:#fff;font-weight:900;opacity:1;border:none" onclick="gtag('event','whatsapp_click',{'product':'${p.title}','action':'inquiry'})">💬 WhatsApp</a>
          <a href="${getQuoteWA(p)}" target="_blank" class="store-quote-btn" style="background:#6C63FF;color:#fff;font-weight:900;opacity:1;border:none" onclick="gtag('event','lead_form_submit',{'product':'${p.title}','action':'quote'})">📄 Get Quote</a>
          <a href="https://wa.me/918381848389?text=Hi%20Freshtiq!%20I%20want%20a%20demo%20of%20${encodeURIComponent(p.title)}" target="_blank" rel="noopener" class="store-demo-btn" style="background:#6C63FF;color:#ffffff;font-weight:900;opacity:1;border:none" onclick="gtag('event','whatsapp_click',{'product':'${p.title}','action':'demo'})">📅 Book Demo</a>
        </div>
      `;
      grid.appendChild(card);
    });

    // Trigger reveal animations
    requestAnimationFrame(() => {
      document.querySelectorAll('.reveal').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight + 100) el.classList.add('visible');
      });
    });
  }

  function filterProducts(filter) {
    currentFilter = filter;
    document.querySelectorAll('.store-filter').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    let filtered;
    if (filter === 'all') {
      filtered = storeProducts;
    } else if (filter === 'popular') {
      filtered = storeProducts.filter(p => p.tags && p.tags.includes('popular'));
    } else if (filter === 'premium') {
      filtered = storeProducts.filter(p => p.tags && p.tags.includes('premium'));
    } else {
      filtered = storeProducts.filter(p => p.category === filter);
    }
    renderProducts(filtered);
  }

  // Setup filters
  document.querySelectorAll('.store-filter').forEach(btn => {
    btn.addEventListener('click', () => filterProducts(btn.dataset.filter));
  });

  // Initial render
  renderProducts(storeProducts);

  // Lazy reveal on scroll
  let revealTimer;
  window.addEventListener('scroll', () => {
    clearTimeout(revealTimer);
    revealTimer = setTimeout(() => {
      document.querySelectorAll('.reveal:not(.visible)').forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight + 50) el.classList.add('visible');
      });
    }, 100);
  }, { passive: true });

  console.log('[AI Store] Render engine loaded. ' + storeProducts.length + ' products.');
})();
