import json,sys,os,re
BOT_MAP={'autopilot_hub_bot':'/root/monster_bot/admin_panel.py','sameer_ai_manager':'/root/sameer_ai_manager/bot.py','freshtiq':'/root/workspaces/customers/freshtiq_ai_travel_pro/bot.py','salama':'/root/workspaces/customers/el_salama_radiator_factory/bot.py'}
REGISTRY_PATH='/root/sameer_ai_manager/factory_registry.json'


def _load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    try:
        return json.load(open(REGISTRY_PATH))
    except Exception:
        return {}


def duplicate_guard(bot, task, patch_path=None):
    reg=_load_registry()
    text=' '.join([str(bot or ''), str(task or ''), str(patch_path or '')]).lower()
    if patch_path and os.path.exists(patch_path):
        try:
            patch=json.load(open(patch_path))
            text+=' '+' '.join(str(patch.get(k,'')) for k in ['task','summary','search_text','replace_text','target_file']).lower()
        except Exception:
            pass
    features=reg.get('features',{}) if isinstance(reg, dict) else {}
    for _, items in features.items():
        for item in items or []:
            item_text=str(item).lower()
            if item_text and (item_text in text or text in item_text or item_text==text):
                return {'ok': False, 'reason': 'DUPLICATE_DETECTED'}
    for item in reg.get('milestones',[]) if isinstance(reg, dict) else []:
        item_text=str(item).lower()
        if item_text and (item_text in text or text in item_text or item_text==text):
            return {'ok': False, 'reason': 'DUPLICATE_DETECTED'}
    if re.search(r'/[a-zA-Z0-9_]{2,32}', text):
        cmd=re.search(r'/[a-zA-Z0-9_]{2,32}', text).group(0)
        for _, items in features.items():
            for item in items or []:
                if str(item).lower()==cmd:
                    return {'ok': False, 'reason': 'DUPLICATE_DETECTED'}
    return {'ok': True, 'reason': 'NO_DUPLICATE'}


def check_patch(patch_file):
    d=json.load(open(patch_file))
    bad=[]
    bot=d.get('bot','')
    target=d.get('target_file','')
    search=d.get('search_text','')
    replace=d.get('replace_text','')
    if bot not in BOT_MAP: bad.append('UNKNOWN_BOT')
    if bot in BOT_MAP and target and target!=BOT_MAP[bot]: bad.append('TARGET_FILE_MISMATCH')
    if search=='MANUAL_REQUIRED' or replace=='MANUAL_REQUIRED': bad.append('MANUAL_REQUIRED')
    if 'context.bot' in replace and 'context' not in replace.split('context.bot')[0]: bad.append('UNSAFE_CONTEXT_BOT')
    if '\\n' in replace: bad.append('LITERAL_BACKSLASH_N')
    if 'autopilot' in replace.lower() and bot!='autopilot_hub_bot': bad.append('HARD_CODED_AUTOPILOT_IN_PATCH')
    return {'ok':len(bad)==0,'issues':bad,'bot':bot,'target_file':target}

if len(sys.argv)>1:
    print(json.dumps(check_patch(sys.argv[1]),indent=2))
