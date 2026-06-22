#!/usr/bin/env python3
"""
DeepSeek API Wrapper — Sameer AI Manager ke liye.
DeepSeek ke paise waste nahi hote — sirf tab call hota hai jab zaroorat ho.
"""
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
LOG = BRIDGE / "deepseek.log"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def get_api_key():
    """Load DeepSeek API key."""
    env_file = Path("/root/sameer_ai_manager/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "DEEPSEEK_API_KEY" in line:
                key = line.split("=", 1)[1].strip()
                if key and "your" not in key and len(key) > 10:
                    return key
    return None

def is_configured():
    """Check if DeepSeek API is properly configured."""
    key = get_api_key()
    if key:
        return True
    return False

def call(prompt, system_prompt="You are a helpful AI assistant.", max_tokens=2048, temperature=0.7):
    """Call DeepSeek API and return response text."""
    key = get_api_key()
    if not key:
        log("⚠️ DeepSeek API key not configured")
        return None
    
    import urllib.request
    
    data = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }).encode()
    
    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            log(f"✅ DeepSeek OK — {tokens_used} tokens, {len(content)} chars")
            return content
    except Exception as e:
        log(f"❌ DeepSeek error: {e}")
        return None

def smart_call(prompt, system_prompt="You are a helpful AI assistant.", max_tokens=2048):
    """
    Smart call: DeepSeek agar configured hai to use karo, 
    nahi to template/text fallback do.
    """
    key = get_api_key()
    if key:
        result = call(prompt, system_prompt, max_tokens)
        if result:
            return result
    
    # Free fallback
    log("Using free fallback for query")
    return f"[Free Mode] DeepSeek not configured. Query: {prompt[:100]}...\nConfigure DeepSeek API in .env for AI-powered responses."

def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = smart_call(prompt)
        if result:
            print(result)
    else:
        if is_configured():
            print("✅ DeepSeek API configured and ready")
        else:
            print("⚠️ DeepSeek API not configured. Edit /root/sameer_ai_manager/.env")
            print("   Add: DEEPSEEK_API_KEY=sk-your-key-here")

if __name__ == "__main__":
    main()
