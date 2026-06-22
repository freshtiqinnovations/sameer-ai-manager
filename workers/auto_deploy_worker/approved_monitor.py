
# --- SMART_CONVERSATION_FILTER START ---
def is_valid_terminal_command(text_input):
    clean_text = str(text_input).strip().lower()
    allowed = ['pwd', 'df', 'free', 'systemctl', 'ls', 'top', 'uptime', 'ifconfig']
    if not clean_text: return False
    first_word = clean_text.split()[0]
    if first_word in allowed and len(clean_text.split()) <= 4:
        return True
    return False
# --- SMART_CONVERSATION_FILTER END ---
import os,time,subprocess,json
APP='/root/sameer_ai_manager/approval_queue/approved'
PY='/root/sameer_ai_manager/venv/bin/python'
BR='/root/sameer_ai_manager/workers/auto_deploy_worker/approval_bridge.py'
DP='/root/sameer_ai_manager/workers/auto_deploy_worker/auto_deploy_worker.py'
TESTER='/root/sameer_ai_manager/workers/tester_worker/tester_worker.py'
GUARD='/root/sameer_ai_manager/workers/central_guard/guard.py'
NOTIFY='/root/sameer_ai_manager/workers/ceo_manager_worker/report_notify.py'
DONE='/root/sameer_ai_manager/approval_queue/deployed'
os.makedirs(DONE,exist_ok=True)

def save_notify_remove(src_file,data):
	out=os.path.join(DONE,os.path.basename(src_file))
	open(out,'w').write(json.dumps(data,indent=2))
	subprocess.getoutput(f'{PY} {NOTIFY} {out}')
	os.remove(src_file)

while True:
	for f in [x for x in os.listdir(APP) if x.endswith('.json')]:
		p=os.path.join(APP,f)
		patch=subprocess.getoutput(f'{PY} {BR} {p}').strip()
		if not patch or not os.path.exists(patch):
			continue
		d=json.load(open(p))
		dry=d.get('dry_run',{})
		main=dry.get('main','')
		service=dry.get('service','')
		tester=subprocess.getoutput(f'{PY} {TESTER} {main} {service}')
		d['tester_result']=tester
		if 'PASS' not in tester:
			d['final_status']='tester_failed_no_deploy'
			save_notify_remove(p,d)
			continue
		guard=subprocess.getoutput(f'{PY} {GUARD} {patch}')
		d['guard_result']=guard
		if '"ok": false' in guard:
			d['final_status']='blocked_by_guard'
			save_notify_remove(p,d)
			continue
		r=subprocess.getoutput(f'{PY} {DP} {patch}')
		d['patch_file']=patch
		d['deploy_time']=time.time()
		d['deploy_result']=r
		d['final_status']='deployed' if "'ok': True" in r or '"ok": true' in r else 'deploy_check_required'
		save_notify_remove(p,d)
	time.sleep(5)
