// Freshtiq AI Store — Product Data
const storeProducts = [
  // ─── Telegram Bots ───
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "Basic Support Bot",
    description: "24/7 auto-reply, FAQ response, ticket forwarding to your team. Perfect for customer support.",
    price: "₹8,000",
    monthly: "₹3,000/mo",
    delivery: "3 days",
    tags: ["bot", "popular"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "Sales Bot",
    description: "Automated sales assistant with product catalog, cart management, order tracking & payment links.",
    price: "₹15,000",
    monthly: "₹5,000/mo",
    delivery: "5 days",
    tags: ["bot", "popular"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "CRM Bot",
    description: "Full CRM in Telegram — manage leads, customers, invoices, support tickets & staff roles.",
    price: "₹25,000",
    monthly: "₹7,000/mo",
    delivery: "7 days",
    tags: ["bot"]
  },
  {
    category: "Telegram Bots",
    icon: "✈️",
    title: "ERP Bot",
    description: "Enterprise resource planning via Telegram — inventory, orders, HR, reports & analytics.",
    price: "₹35,000",
    monthly: "₹10,000/mo",
    delivery: "10 days",
    tags: ["bot", "premium"]
  },

  // ─── WhatsApp Bots ───
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "FAQ Bot",
    description: "Auto-reply to common questions, business hours, location sharing, catalog view on WhatsApp.",
    price: "₹15,000",
    monthly: "₹5,000/mo",
    delivery: "4 days",
    tags: ["bot", "popular"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "Sales Bot",
    description: "AI-powered WhatsApp sales assistant. Handle inquiries, send quotes, collect payments via link.",
    price: "₹25,000",
    monthly: "₹8,000/mo",
    delivery: "5 days",
    tags: ["bot", "popular"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "Lead Capture Bot",
    description: "Capture leads 24/7 from WhatsApp. Auto-qualify, tag, notify team & sync to CRM.",
    price: "₹30,000",
    monthly: "₹10,000/mo",
    delivery: "7 days",
    tags: ["bot"]
  },
  {
    category: "WhatsApp Bots",
    icon: "💬",
    title: "AI Assistant",
    description: "Full WhatsApp AI agent with DeepSeek/GPT, multi-language, memory, analytics & human handoff.",
    price: "₹45,000",
    monthly: "₹15,000/mo",
    delivery: "10 days",
    tags: ["bot", "premium"]
  },

  // ─── Websites ───
  {
    category: "Websites",
    icon: "🌐",
    title: "Business Website",
    description: "Professional 5-page website. Mobile responsive, SEO ready, contact form, WhatsApp integration.",
    price: "₹10,000+",
    monthly: "₹0",
    delivery: "3-5 days",
    tags: ["website", "popular"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "Premium Website",
    description: "Custom designed multi-page site. Animations, live chat, portfolio, blog, lead forms, analytics.",
    price: "₹25,000+",
    monthly: "₹0",
    delivery: "5-7 days",
    tags: ["website"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "Travel Website",
    description: "Booking engine, package listings, payment gateway, itinerary builder, customer portal.",
    price: "₹35,000+",
    monthly: "₹0",
    delivery: "7-10 days",
    tags: ["website"]
  },
  {
    category: "Websites",
    icon: "🌐",
    title: "E-commerce Website",
    description: "Full online store. Product catalog, cart, checkout, payments, order tracking, admin panel.",
    price: "₹60,000+",
    monthly: "₹0",
    delivery: "10-14 days",
    tags: ["website", "premium"]
  },

  // ─── ERP / CRM ───
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Sales CRM",
    description: "Track leads, manage contacts, pipeline view, email/SMS integration, team dashboards.",
    price: "₹25,000+",
    monthly: "₹0",
    delivery: "7 days",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Inventory ERP",
    description: "Stock management, purchase orders, supplier tracking, barcode scanning, low stock alerts.",
    price: "₹50,000+",
    monthly: "₹0",
    delivery: "10-14 days",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "HR System",
    description: "Employee management, attendance, leave tracking, payroll reports, document storage.",
    price: "₹60,000+",
    monthly: "₹0",
    delivery: "10-14 days",
    tags: ["erp"]
  },
  {
    category: "ERP / CRM",
    icon: "📊",
    title: "Factory ERP",
    description: "Complete factory management: production, inventory, orders, workforce, maintenance & reports.",
    price: "₹1,50,000+",
    monthly: "₹0",
    delivery: "21-30 days",
    tags: ["erp", "premium"]
  },

  // ─── SEO & Marketing ───
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "SEO Setup",
    description: "On-page SEO, meta optimization, keyword research, Google indexing, technical audit.",
    price: "₹5,000/mo",
    monthly: "",
    delivery: "1 week setup",
    tags: ["seo"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Google Business Profile",
    description: "GBP setup, verification, listing optimization, photo uploads, review management, posting.",
    price: "₹3,000",
    monthly: "₹2,000/mo",
    delivery: "5 days",
    tags: ["seo", "popular"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Content Marketing",
    description: "Blog writing, social media content, case studies, infographics, newsletter campaigns.",
    price: "₹10,000/mo",
    monthly: "",
    delivery: "Ongoing",
    tags: ["seo"]
  },
  {
    category: "SEO & Marketing",
    icon: "📈",
    title: "Lead Generation",
    description: "Targeted lead campaigns via Google Ads, Facebook, Instagram. Landing pages + tracking.",
    price: "₹15,000/mo",
    monthly: "",
    delivery: "Ongoing",
    tags: ["seo"]
  },

  // ─── AI Agents ───
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Customer Support AI",
    description: "AI agent trained on your business data. Answers 80%+ queries. Human handoff for complex issues.",
    price: "₹25,000+",
    monthly: "₹8,000/mo",
    delivery: "5-7 days",
    tags: ["ai", "popular"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Sales AI",
    description: "Proactive sales AI that qualifies leads, sends follow-ups, books meetings, tracks pipeline.",
    price: "₹35,000+",
    monthly: "₹12,000/mo",
    delivery: "7-10 days",
    tags: ["ai"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Operations AI",
    description: "Internal ops agent for task management, scheduling, reporting, document automation & reminders.",
    price: "₹45,000+",
    monthly: "₹0",
    delivery: "7-10 days",
    tags: ["ai"]
  },
  {
    category: "AI Agents",
    icon: "🧠",
    title: "Custom AI Agent",
    description: "Build bespoke AI agent for your unique business workflow. Any platform. Any integration.",
    price: "₹75,000+",
    monthly: "₹0",
    delivery: "10-14 days",
    tags: ["ai", "premium"]
  }
];
