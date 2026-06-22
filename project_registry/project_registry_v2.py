#!/usr/bin/env python3
import json, os, time
from pathlib import Path

BASE = Path("/root/sameer_ai_manager/project_registry")
REG = BASE / "PROJECT_REGISTRY_V2.json"
DETAILS = BASE / "details"
CUSTOMERS = Path("/root/workspaces/customers")
DETAILS.mkdir(parents=True, exist_ok=True)

START_ID = 200

KNOWN = {
 "sameer_ai_manager": {"id":200,"name":"Sameer AI Manager","service":"sameer_ai_manager.service","type":"core"},
 "freshtiq_whatsapp_sales_bot": {"id":201,"name":"Freshtiq WhatsApp Sales Bot","service":"freshtiq_sales_bot.service","type":"whatsapp_bot"},
 "flight_fare_ai": {"id":202,"name":"Flight Fare AI","service":"flight_fare_ai.service","type":"telegram_bot"},
 "sameer_speaking_english_commander_ai": {"id":203,"name":"Sameer English Commander","service":"sameer_english_commander.service","type":"education_bot"},
 "el_salama_radiator_factory": {"id":204,"name":"EL SALAMA AI ERP PRO","service":"salama_radiator_bot.service","type":"erp"},
 "hawala_token_system": {"id":205,"name":"USDT Deal Backend","service":"hawala_token_system.service","type":"flask_backend"},
 "usdt_deal_apk": {"id":206,"name":"USDT Deal Android App","service":"","type":"android_app"},
 "openclaw_whatsapp_bridge": {"id":207,"name":"OpenClaw WhatsApp Bridge","service":"openclaw-whatsapp.service","type":"operator"},
 "freshtiq_portal": {"id":208,"name":"Freshtiq Portal","service":"freshtiq_portal.service","type":"web_portal"},
 "binance_ai_trading_bot": {"id":209,"name":"Freshtiq Alpha Trader AI","service":"freshtiq_trader_bot.service","type":"trading_bot"}
}

def load():
    if REG.exists():
        return json.loads(REG.read_text())
    return {"next_id":210,"projects":{}}

def save(data):
    REG.write_text(json.dumps(data, indent=2))

def detail_file(pid, slug):
    return DETAILS / f"PROJECT_{pid}_{slug}.md"

def write_detail(p):
    f = detail_file(p["id"], p["slug"])
    if not f.exists():
        f.write_text(f"""# PROJECT {p['id']} — {p['name']}

Slug: {p['slug']}
Type: {p['type']}
Path: {p['path']}
Service: {p.get('service','')}
Status: active

## Rules
- Is project ka patch sirf is path me lage.
- Dusre project ka code touch nahi karna.
- Pehle scan, backup, patch, compile/build, restart, verify, report.
- Completed/pending kaam yahin update karna.

## Completed Work
- Registry created.

## Pending Work
- Update after next scan.

## Last Backup
-

## Known Issues
-

## Do Not Touch
- Other project paths.
""")

def detect():
    data = load()
    projects = data["projects"]

    for slug, meta in KNOWN.items():
        path = "/root/sameer_ai_manager" if slug=="sameer_ai_manager" else str(CUSTOMERS/slug)
        projects[slug] = {
            "id": meta["id"],
            "slug": slug,
            "name": meta["name"],
            "type": meta["type"],
            "path": path,
            "service": meta.get("service",""),
            "status": "active",
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    used_ids = {p["id"] for p in projects.values()}
    next_id = max(max(used_ids), data.get("next_id", START_ID)-1) + 1

    if CUSTOMERS.exists():
        for d in sorted(CUSTOMERS.iterdir()):
            if not d.is_dir(): continue
            slug = d.name
            if slug in projects: continue
            while next_id in used_ids:
                next_id += 1
            projects[slug] = {
                "id": next_id,
                "slug": slug,
                "name": slug.replace("_"," ").title(),
                "type": "unknown",
                "path": str(d),
                "service": "",
                "status": "detected",
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            used_ids.add(next_id)
            next_id += 1

    data["next_id"] = next_id
    save(data)

    for p in projects.values():
        write_detail(p)

    print("✅ PROJECT_REGISTRY_V2 UPDATED")
    print("Total projects:", len(projects))
    print("Next ID:", data["next_id"])
    for p in sorted(projects.values(), key=lambda x:x["id"])[:80]:
        print(f"Project {p['id']} — {p['name']}  |  Folder: {p['slug']}")

if __name__ == "__main__":
    detect()
