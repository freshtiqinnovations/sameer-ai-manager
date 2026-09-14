// Freshtiq AI Store — Product Data
const storeProducts = [
  // ─── Telegram Bots ───
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "Basic Support Bot",
    description: "24/7 auto-reply, FAQ response, ticket forwarding to your team. Perfect for customer support.",
    price: "From ₹8,000",
    tiers: { standard: "₹8,000", professional: "₹15,000", premium: "₹25,000" },
    monthly: "",
    delivery: "3–7 days",
    tags: ["bot", "popular"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "Sales Bot",
    description: "Automated sales assistant with product catalog, cart management, order tracking & payment links.",
    price: "From ₹15,000",
    tiers: { standard: "₹15,000", professional: "₹30,000", premium: "₹50,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["bot", "popular"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "CRM Bot",
    description: "Full CRM in Telegram — manage leads, customers, invoices, support tickets & staff roles.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹75,000" },
    monthly: "",
    delivery: "1–4 weeks",
    tags: ["bot"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "ERP Bot",
    description: "Enterprise resource planning via Telegram — inventory, orders, HR, reports & analytics.",
    price: "From ₹35,000",
    tiers: { standard: "₹35,000", professional: "₹75,000", premium: "₹1,50,000" },
    monthly: "",
    delivery: "2–6 weeks",
    tags: ["bot", "premium"]
  },

  // ─── WhatsApp Bots ───
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "FAQ Bot",
    description: "Auto-reply to common questions, business hours, location sharing, catalog view on WhatsApp.",
    price: "From ₹8,000",
    tiers: { standard: "₹8,000", professional: "₹15,000", premium: "₹25,000" },
    monthly: "",
    delivery: "3–7 days",
    tags: ["bot", "popular"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "Sales Bot",
    description: "AI-powered WhatsApp sales assistant. Handle inquiries, send quotes, collect payments via link.",
    price: "From ₹15,000",
    tiers: { standard: "₹15,000", professional: "₹30,000", premium: "₹50,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["bot", "popular"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "Lead Capture Bot",
    description: "Capture leads 24/7 from WhatsApp. Auto-qualify, tag, notify team & sync to CRM.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹75,000" },
    monthly: "",
    delivery: "1–4 weeks",
    tags: ["bot"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "AI Assistant",
    description: "Full WhatsApp AI agent with DeepSeek/GPT, multi-language, memory, analytics & human handoff.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹85,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["bot", "premium"]
  },

  // ─── Websites ───
  {
    category: "Websites",
    icon: "🌐",
    title: "Business Website",
    description: "Professional 5-page website. Mobile responsive, SEO ready, contact form, WhatsApp integration.",
    price: "From ₹4,999",
    tiers: { standard: "₹4,999", professional: "₹12,000", premium: "₹25,000" },
    monthly: "",
    delivery: "3–7 days",
    tags: ["website", "popular"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "Premium Website",
    description: "Custom designed multi-page site. Animations, live chat, portfolio, blog, lead forms, analytics.",
    price: "From ₹4,999",
    tiers: { standard: "₹4,999", professional: "₹12,000", premium: "₹25,000" },
    monthly: "",
    delivery: "3–7 days",
    tags: ["website"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "Travel Website",
    description: "Booking engine, package listings, payment gateway, itinerary builder, customer portal.",
    price: "From ₹15,000",
    tiers: { standard: "₹15,000", professional: "₹30,000", premium: "₹50,000" },
    monthly: "",
    delivery: "7–21 days",
    tags: ["website"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "E-commerce Website",
    description: "Full online store. Product catalog, cart, checkout, payments, order tracking, admin panel.",
    price: "From ₹15,000",
    tiers: { standard: "₹15,000", professional: "₹30,000", premium: "₹60,000" },
    monthly: "",
    delivery: "7–21 days",
    tags: ["website", "premium"]
  },

  // ─── ERP / CRM ───
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Sales CRM",
    description: "Track leads, manage contacts, pipeline view, email/SMS integration, team dashboards.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹75,000" },
    monthly: "",
    delivery: "1–4 weeks",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Inventory ERP",
    description: "Stock management, purchase orders, supplier tracking, barcode scanning, low stock alerts.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹50,000", premium: "₹90,000" },
    monthly: "",
    delivery: "1–4 weeks",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "HR System",
    description: "Employee management, attendance, leave tracking, payroll reports, document storage.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹75,000" },
    monthly: "",
    delivery: "1–4 weeks",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Factory ERP",
    description: "Complete factory management: production, inventory, orders, workforce, maintenance & reports.",
    price: "From ₹35,000",
    tiers: { standard: "₹35,000", professional: "₹75,000", premium: "₹1,50,000" },
    monthly: "",
    delivery: "2–6 weeks",
    tags: ["erp", "premium"]
  },

  // ─── SEO & Marketing ───
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "SEO Setup",
    description: "On-page SEO, meta optimization, keyword research, Google indexing, technical audit.",
    price: "From ₹5,000/month",
    tiers: { standard: "₹5,000/month", professional: "₹10,000/month", premium: "₹18,000/month" },
    monthly: "",
    delivery: "Monthly service",
    tags: ["seo"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Google Business Profile",
    description: "GBP setup, verification, listing optimization, photo uploads, review management, posting.",
    price: "From ₹3,000",
    tiers: { standard: "₹3,000", professional: "₹6,000", premium: "₹10,000" },
    monthly: "",
    delivery: "3–10 days",
    tags: ["seo", "popular"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Content Marketing",
    description: "Blog writing, social media content, case studies, infographics, newsletter campaigns.",
    price: "From ₹10,000/month",
    tiers: { standard: "₹10,000/month", professional: "₹20,000/month", premium: "₹35,000/month" },
    monthly: "",
    delivery: "Monthly service",
    tags: ["seo"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Lead Generation",
    description: "Targeted lead campaigns via Google Ads, Facebook, Instagram. Landing pages + tracking.",
    price: "From ₹15,000/month",
    tiers: { standard: "₹15,000/month", professional: "₹30,000/month", premium: "₹50,000/month" },
    monthly: "",
    delivery: "Monthly service",
    tags: ["seo"]
  },

  // ─── AI Agents ───
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Customer Support AI",
    description: "AI agent trained on your business data. Answers routine business/support enquiries with human handoff for complex cases.",
    price: "From ₹12,000",
    tiers: { standard: "₹12,000", professional: "₹25,000", premium: "₹40,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["ai", "popular"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Sales AI",
    description: "Proactive sales AI that qualifies leads, sends follow-ups, books meetings, tracks pipeline.",
    price: "From ₹15,000",
    tiers: { standard: "₹15,000", professional: "₹30,000", premium: "₹50,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["ai"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Operations AI",
    description: "Internal ops agent for task management, scheduling, reporting, document automation & reminders.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹85,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["ai"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Custom AI Agent",
    description: "Build bespoke AI agent for your unique business workflow. Platform and integrations are confirmed by scope.",
    price: "From ₹25,000",
    tiers: { standard: "₹25,000", professional: "₹45,000", premium: "₹85,000" },
    monthly: "",
    delivery: "5–14 days",
    tags: ["ai", "premium"]
  }
];
