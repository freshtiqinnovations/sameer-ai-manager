
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
import os,json,time,subprocess,shlex
P='/root/sameer_ai_manager/approval_queue/pending'
A='/root/sameer_ai_manager/approval_queue/approved'
R='/root/sameer_ai_manager/approval_queue/rejected'
B='/root/sameer_ai_manager/approval_queue/blocked'
PY='/root/sameer_ai_manager/venv/bin/python'
DEC='/root/sameer_ai_manager/workers/auto_approval_worker/auto_approval_worker.py'
TEST='/root/sameer_ai_manager/workers/tester_worker/tester_worker.py'
QC='/root/sameer_ai_manager/workers/patch_generator/patch_quality_checker.py'
os.makedirs(A,exist_ok=True); os.makedirs(R,exist_ok=True); os.makedirs(B,exist_ok=True)

def _blocked_by_mode(d):
    mode=str(d.get('mode') or '').strip().upper()
    details=str(d.get('details') or d.get('task') or '').lower()
    if mode in ['REPORT_ONLY','PLAN_ONLY','QUEUE_ONLY']:
        return True, f'mode={mode}'
    if any(x in details for x in ['report only', 'no patch', 'plan only', 'do not patch', 'no restart']):
        return True, 'details_block'
    return False, ''

while True:
    for f in [x for x in os.listdir(P) if x.endswith('.json')]:
        p=os.path.join(P,f)
        d=json.load(open(p))
        blocked, reason = _blocked_by_mode(d)
        if blocked:
            d['status']='blocked_by_mode_gate'
            d['auto_approval_decision']='BLOCKED_BY_MODE_GATE'
            d['blocked_reason']=reason
            d['blocked_time']=time.time()
            out=os.path.join(B,f)
            open(out,'w').write(json.dumps(d,indent=2))
            os.remove(p)
            continue
        dry=d.get('dry_run',{})
        main=dry.get('main','')
        service=dry.get('service','')
        risk=d.get('risk') or 'low'
        patch=d.get('patch_file') or ''
        quality=subprocess.getoutput(f'{PY} {QC} {patch}') if patch else '{"ok": false, "issues":["NO_PATCH_FILE"]}'
        d['patch_quality_result']=quality
        if '"ok": false' in quality:
            d['status']='rejected_quality'
            d['auto_approval_decision']='REJECT_QUALITY'
            out=os.path.join(R,f)
            open(out,'w').write(json.dumps(d,indent=2))
            os.remove(p)
            continue
        test=subprocess.getoutput(f'{PY} {TEST} {main} {service}')
        test_status='PASS' if 'PASS' in test else 'FAIL'
        decision=subprocess.getoutput(f'{PY} {DEC} {shlex.quote(risk)} {shlex.quote(test_status)}').strip()
        d['auto_test_result']=test
        d['auto_approval_decision']=decision
        d['auto_approval_time']=time.time()
        if decision in ['AUTO_APPROVE','TESTER_APPROVED_AUTO_DEPLOY']:
            d['status']='approved_auto'
            out=os.path.join(A,f)
        elif decision=='REJECT':
            d['status']='rejected_auto'
            out=os.path.join(R,f)
        else:
            d['status']='pending_human_approval'
            open(p,'w').write(json.dumps(d,indent=2))
            continue
        open(out,'w').write(json.dumps(d,indent=2))
        os.remove(p)
    time.sleep(5)
