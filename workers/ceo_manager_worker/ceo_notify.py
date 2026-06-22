import os, requests
from dotenv import load_dotenv
load_dotenv("/root/sameer_ai_manager/.env")
TOKEN=os.getenv("TELEGRAM_TOKEN")
ADMIN_ID=os.getenv("ADMIN_ID")

def send_ceo(text):
    if not TOKEN or not ADMIN_ID:
        return {'ok':False,'error':'TOKEN_OR_ADMIN_ID_MISSING'}
    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r=requests.post(url,json={"chat_id":ADMIN_ID,"text":text[:3900]},timeout=15)
    return {'ok':r.ok,'status':r.status_code}

import sys
print(send_ceo(' '.join(sys.argv[1:]) or 'CEO notifier test'))
