#!/usr/bin/env python3
import json, os, time
from pathlib import Path

BASE=Path("/root/sameer_ai_manager/project_registry")
REG=BASE/"PROJECT_REGISTRY_V2.json"
DETAILS=BASE/"details"
DETAILS.mkdir(parents=True,exist_ok=True)

data=json.load(open(REG))["projects"]

MAIN_IDS=range(200,210)

for p in sorted(data.values(), key=lambda x:x["id"]):
    if p["id"] not in MAIN_IDS:
        continue
    f=DETAILS/f"PROJECT_{p['id']}_{p['slug']}.md"
    if not f.exists():
        f.write_text("")
    old=f.read_text()
    header=f"""# Project {p['id']} — {p['name']}

## Identity
Project ID: {p['id']}
Folder: {p['slug']}
Type: {p.get('type','')}
Path: {p['path']}
Service: {p.get('service','')}
Status: {p.get('status','active')}
Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Hard Rules
- Patch sirf isi project path me lage.
- Dusre project ka code touch nahi karna.
- Pehle scan → backup → patch → compile/build → restart → verify → report.
- Agar path/service mismatch ho to STOP.
- Fake PASS report nahi.
- Same mistake repeat nahi.

## Completed Work
"""

    if "## Completed Work" in old:
        rest=old.split("## Completed Work",1)[1]
        body="## Completed Work"+rest
        f.write_text(header+body.replace("## Completed Work","",1))
    else:
        f.write_text(header+"- Registry detail file created.\n\n## Pending Work\n- Scan required.\n\n## Last Patch\n-\n\n## Last Backup\n-\n\n## Known Issues\n-\n\n## Do Not Touch\n- Other project folders.\n")

print("MAIN_PROJECT_DETAILS_READY")
for pid in MAIN_IDS:
    matches=[x for x in data.values() if x["id"]==pid]
    if matches:
        p=matches[0]
        print(f"Project {pid} detail: {DETAILS/f'PROJECT_{pid}_{p['slug']}.md'}")
