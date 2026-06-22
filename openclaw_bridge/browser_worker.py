#!/usr/bin/env python3
"""
Browser Worker — Playwright-based website audit tool
Part of OpenClaw autonomous learning worker system

Provider: Ollama qwen2.5:3b (DeepSeek approval-only)
Per AI_PROVIDER_POLICY.md & AUTO_LEARNING_POLICY.md

Functions:
  website_audit(url)   → dict (load time, status, errors, resources)
  seo_audit(url)       → dict (meta, headers, schema, links, images)
  screenshot(url)      → str (path to saved PNG file)

Design doc: /root/.openclaw/workspace/memory_core/BROWSER_WORKER_ARCHITECTURE.md
"""

import json
import time
from datetime import datetime
from pathlib import Path

# ── Playwright ──────────────────────────────────────────────────
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

# ── HTML Parsing ────────────────────────────────────────────────
from bs4 import BeautifulSoup

# ── Paths ───────────────────────────────────────────────────────
REPORTS_DIR = Path("/root/.openclaw/workspace/reports/browser")
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
AUDITS_DIR = REPORTS_DIR / "audits"
SEO_DIR = REPORTS_DIR / "seo"

for d in [REPORTS_DIR, SCREENSHOTS_DIR, AUDITS_DIR, SEO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Helper ──────────────────────────────────────────────────────
def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def _domain(url: str) -> str:
    """Extract clean domain from URL."""
    url = url.strip().lower()
    if url.startswith("http://") or url.startswith("https://"):
        url = url.split("://")[1]
    return url.split("/")[0].split("?")[0].split("@")[-1].replace("www.", "")

# ══════════════════════════════════════════════════════════════════
# 1. website_audit(url) — Full website audit
# ══════════════════════════════════════════════════════════════════
def website_audit(url: str, timeout_ms: int = 30000) -> dict:
    """
    Full website audit using Playwright Chromium (headless).
    
    Returns:
        dict with keys: url, status, load_time_ms, title, 
                        console_errors, resources, page_size_kb,
                        broken_links, timestamp, screenshot_path
    """
    if not url.startswith("http"):
        url = "https://" + url

    result = {
        "url": url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": None,
        "load_time_ms": None,
        "title": None,
        "console_errors": [],
        "resources": {"css": 0, "js": 0, "images": 0},
        "page_size_kb": None,
        "broken_links": [],
        "screenshot_path": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        try:
            start = time.time()
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            load_time_ms = int((time.time() - start) * 1000)

            result["status"] = page.evaluate("document.readyState")
            result["load_time_ms"] = load_time_ms
            result["title"] = page.title()

            # Resources
            resources = page.evaluate("""() => {
                const r = {css: 0, js: 0, images: 0};
                document.querySelectorAll('link[rel=stylesheet]').forEach(() => r.css++);
                document.querySelectorAll('script[src]').forEach(() => r.js++);
                document.querySelectorAll('img').forEach(() => r.images++);
                return r;
            }""")
            result["resources"] = resources

            # Page size
            content = page.content()
            result["page_size_kb"] = round(len(content.encode("utf-8")) / 1024, 1)

            # Console errors (first 10)
            result["console_errors"] = console_errors[:10]

            # Screenshot
            domain = _domain(url)
            ts = _timestamp()
            ss_path = SCREENSHOTS_DIR / f"{domain}_{ts}.png"
            page.screenshot(path=str(ss_path), full_page=True)
            result["screenshot_path"] = str(ss_path)

        except PwTimeout:
            result["status"] = "timeout"
        except Exception as e:
            result["status"] = f"error: {str(e)[:200]}"
        finally:
            browser.close()

    # Save report
    domain = _domain(url)
    ts = _timestamp()
    report_path = AUDITS_DIR / f"{domain}_audit_{ts}.json"
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ══════════════════════════════════════════════════════════════════
# 2. seo_audit(url) — SEO analysis
# ══════════════════════════════════════════════════════════════════
def seo_audit(url: str, timeout_ms: int = 30000) -> dict:
    """
    SEO audit using Playwright + BeautifulSoup.
    
    Returns:
        dict with score (0-100), checks dict, warnings, critical issues
    """
    if not url.startswith("http"):
        url = "https://" + url

    result = {
        "url": url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "score": 0,
        "checks": {},
        "warnings": [],
        "critical": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            html = page.content()
        except PwTimeout:
            result["critical"].append("Page load timeout")
            browser.close()
            return result
        except Exception as e:
            result["critical"].append(f"Error: {str(e)[:200]}")
            browser.close()
            return result
        finally:
            browser.close()

    soup = BeautifulSoup(html, "html.parser")
    checks = {}

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None
    checks["title"] = {
        "pass": bool(title and 10 < len(title) < 70),
        "value": title or "MISSING",
        "detail": f"Length: {len(title) if title else 0} chars"
    }
    if not title:
        result["critical"].append("Missing <title> tag")
    elif len(title) > 70:
        result["warnings"].append(f"Title too long ({len(title)} chars)")

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_content = meta_desc.get("content", "").strip() if meta_desc else None
    checks["description"] = {
        "pass": bool(desc_content and 50 < len(desc_content) < 160),
        "value": desc_content[:120] if desc_content else "MISSING",
        "detail": f"Length: {len(desc_content) if desc_content else 0} chars"
    }
    if not desc_content:
        result["warnings"].append("Missing meta description")

    # Meta keywords
    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    checks["keywords"] = {
        "pass": bool(meta_kw and meta_kw.get("content", "").strip()),
        "value": meta_kw.get("content", "")[:100] if meta_kw else "MISSING",
    }

    # OG tags
    og_tags = soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")})
    checks["og_tags"] = {
        "pass": len(og_tags) >= 3,
        "value": [t.get("property") for t in og_tags],
    }
    if len(og_tags) < 3:
        result["warnings"].append(f"Only {len(og_tags)} Open Graph tags found (min 3 recommended)")

    # Twitter card
    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
    checks["twitter_card"] = {
        "pass": bool(twitter_card),
        "value": twitter_card.get("content", "") if twitter_card else "MISSING",
    }

    # Canonical
    canonical = soup.find("link", rel="canonical")
    checks["canonical"] = {
        "pass": bool(canonical and canonical.get("href")),
        "value": canonical.get("href", "") if canonical else "MISSING",
    }

    # H1
    h1_tags = soup.find_all("h1")
    checks["h1"] = {
        "pass": len(h1_tags) == 1,
        "value": [h.get_text(strip=True)[:50] for h in h1_tags],
        "detail": f"{len(h1_tags)} h1 tags found"
    }
    if len(h1_tags) == 0:
        result["critical"].append("Missing H1 tag")
    elif len(h1_tags) > 1:
        result["warnings"].append(f"Multiple H1 tags ({len(h1_tags)})")

    # Image alt attributes
    imgs = soup.find_all("img")
    missing_alt = [img.get("src", "")[:40] for img in imgs if not img.get("alt")]
    checks["image_alt"] = {
        "pass": len(missing_alt) < len(imgs) * 0.3,
        "value": f"{len(imgs) - len(missing_alt)}/{len(imgs)} have alt text",
        "missing": missing_alt[:10],
    }
    if len(missing_alt) > len(imgs) * 0.3:
        result["warnings"].append(f"{len(missing_alt)} images without alt text")

    # Schema.org / JSON-LD
    json_ld = soup.find("script", type="application/ld+json")
    checks["schema"] = {
        "pass": bool(json_ld),
        "value": "JSON-LD present" if json_ld else "MISSING",
    }
    if not json_ld:
        result["warnings"].append("No schema.org JSON-LD found")

    # Viewport meta
    viewport = soup.find("meta", attrs={"name": "viewport"})
    checks["viewport"] = {
        "pass": bool(viewport),
        "value": viewport.get("content", "") if viewport else "MISSING",
    }
    if not viewport:
        result["critical"].append("Missing viewport meta tag (mobile-unfriendly)")

    # Lang attribute
    html_tag = soup.find("html")
    checks["lang"] = {
        "pass": bool(html_tag and html_tag.get("lang")),
        "value": html_tag.get("lang", "") if html_tag else "MISSING",
    }

    # Favicon
    favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    checks["favicon"] = {
        "pass": bool(favicon),
        "value": favicon.get("href", "") if favicon else "MISSING",
    }

    # Score calculation (10 checks, 10 points each)
    score_checks = ["title", "description", "og_tags", "canonical", "h1",
                    "image_alt", "schema", "viewport", "lang", "favicon"]
    passed = sum(1 for c in score_checks if checks.get(c, {}).get("pass"))
    result["score"] = int((passed / len(score_checks)) * 100)
    result["checks"] = checks

    # Save report
    domain = _domain(url)
    ts = _timestamp()
    report_path = SEO_DIR / f"{domain}_seo_{ts}.json"
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ══════════════════════════════════════════════════════════════════
# 3. screenshot(url) — Full-page screenshot only
# ══════════════════════════════════════════════════════════════════
def screenshot(url: str, full_page: bool = True, timeout_ms: int = 30000) -> str:
    """
    Take a full-page screenshot using Playwright Chromium.
    
    Args:
        url: Target URL
        full_page: Capture entire scrollable page
    
    Returns:
        str: Absolute path to saved PNG file
    """
    if not url.startswith("http"):
        url = "https://" + url

    domain = _domain(url)
    ts = _timestamp()
    output_path = SCREENSHOTS_DIR / f"{domain}_{ts}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            page.screenshot(path=str(output_path), full_page=full_page)
        except PwTimeout:
            # Try with domcontentloaded fallback
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.screenshot(path=str(output_path), full_page=full_page)
        except Exception as e:
            browser.close()
            raise RuntimeError(f"Screenshot failed: {str(e)[:200]}")
        
        browser.close()

    return str(output_path)


# ══════════════════════════════════════════════════════════════════
# CLI entry (for testing)
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 browser_worker.py <audit|seo|screenshot> <url>")
        sys.exit(1)

    action = sys.argv[1]
    url = sys.argv[2]

    if action == "audit":
        result = website_audit(url)
        print(json.dumps(result, indent=2, default=str)[:2000])

    elif action == "seo":
        result = seo_audit(url)
        print(json.dumps(result, indent=2, default=str)[:2000])

    elif action == "screenshot":
        path = screenshot(url)
        print(f"✅ Screenshot saved to: {path}")

    else:
        print(f"Unknown action: {action}. Use: audit, seo, or screenshot")
        sys.exit(1)
