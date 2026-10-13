#!/usr/bin/env python3
"""Freshtiq SEO preflight. --apply refreshes honest Git-based sitemap lastmod."""
import argparse, datetime, re, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
SITE="https://freshtiqautomation.com"
XML=ROOT/"sitemap.xml"
NEW_PUBLIC_PAGES=("/earn-freshtiq.html",)

class Metadata(HTMLParser):
 def __init__(self):super().__init__();self.robots="";self.canon=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("name","").lower()=="robots":self.robots=a.get("content","").lower()
  if tag=="link" and "canonical" in a.get("rel","").lower():self.canon.append(a.get("href",""))

def verify(url):
 u=urlparse(url)
 if u.scheme!="https" or u.netloc!="freshtiqautomation.com":raise ValueError(f"Wrong property: {url}")
 relative=u.path.lstrip("/") or "index.html"
 if u.path.endswith("/") and u.path!="/":relative+="index.html"
 p=ROOT/relative
 if not p.is_file():raise ValueError(f"Missing page: {url}")
 m=Metadata();m.feed(p.read_text(encoding="utf-8",errors="replace"))
 if "noindex" in m.robots or url not in m.canon:raise ValueError(f"Nonindexable/noncanonical: {url}")
 day=subprocess.run(["git","log","-1","--format=%cs","--",relative],cwd=ROOT,capture_output=True,text=True).stdout.strip()
 if day and datetime.date.fromisoformat(day)>datetime.date.today():raise ValueError(f"Future commit: {url}")
 return day

def main(apply):
 raw=XML.read_text(encoding="utf-8")
 seen=set();corrected=0
 def fix(match):
  nonlocal corrected
  block=match.group(0);lm=re.search(r"<loc>(.*?)</loc>",block,re.S)
  if lm is None:raise ValueError("Missing loc")
  url=lm.group(1).strip()
  if url in seen:raise ValueError(f"Duplicate URL: {url}")
  seen.add(url);day=verify(url)
  old=re.search(r"<lastmod>(.*?)</lastmod>",block,re.S)
  if day and old and old.group(1).strip()<day:
   corrected+=1
   return block.replace(old.group(0),f"<lastmod>{day}</lastmod>",1)
  if day and not old:
   corrected+=1
   return block.replace(lm.group(0),lm.group(0)+f"<lastmod>{day}</lastmod>",1)
  return block
 out=re.sub(r"<url>(?:(?!</url>).)*</url>",fix,raw,flags=re.S)
 for path in NEW_PUBLIC_PAGES:
  url=SITE+path
  if url not in seen:
   day=verify(url)
   if not day:raise ValueError(f"Untracked page: {url}")
   out=out.replace("</urlset>",f"  <url><loc>{url}</loc><lastmod>{day}</lastmod></url>\n</urlset>")
   seen.add(url);corrected+=1
 ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
 elements=ET.fromstring(out).findall(f"{ns}url")
 if len(elements)!=len(seen):raise ValueError("XML URL count mismatch")
 if apply:XML.write_text(out,encoding="utf-8")
 print("SEO_SITEMAP_PREFLIGHT_PASS urls",len(elements),"corrected",corrected,"applied",apply)

if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--apply",action="store_true");main(a.parse_args().apply)
