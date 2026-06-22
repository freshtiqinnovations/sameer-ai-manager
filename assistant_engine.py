import os
from openai import OpenAI

# OLLAMA - local, free, no API key needed
client = OpenAI(
    api_key="ollama",  # Ollama doesn't need a real key
    base_url="http://127.0.0.1:11434/v1",
)

DEFAULT_MODEL = "llama3.2:1b"

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to DeepSeek only if Ollama fails
        return _fallback_deepseek(prompt)

def chat(messages):
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return _fallback_deepseek_chat(messages)

def _fallback_deepseek(prompt):
    try:
        ds = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        response = ds.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ollama + DeepSeek both failed: {e}"

def _fallback_deepseek_chat(messages):
    try:
        ds = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        response = ds.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI error: {e}"
