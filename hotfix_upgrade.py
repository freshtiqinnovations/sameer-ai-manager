from pathlib import Path

p = Path("bot.py")
text = p.read_text(encoding="utf-8")

old = 'response = ask_ai(user_text)'

new = '''
lower_text = user_text.lower()

if any(k in lower_text for k in [
    "upgrade",
    "feature add",
    "khud ko upgrade",
    "khud ko aur upgrade"
]):
    with open("/root/sameer_ai_manager/ai_patch_request.txt", "a", encoding="utf-8") as f:
        f.write(user_text + "\\n")

    await update.message.reply_text(
        "✅ Request save ho gayi.\\n\\n"
        "Safe AI patch ready karne ke liye /approve_patch bhejo."
    )
    return

response = ask_ai(user_text)
'''

if old not in text:
    print("TARGET NOT FOUND")
    raise SystemExit

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")

print("PATCH SUCCESS")
