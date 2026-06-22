"""
TRIO INTEGRATION — Sameer AI Bot ke liye plugin.
Isse Sameer AI bot import karega aur OpenClaw se baat karega.
"""
import json, os, sys
from pathlib import Path

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
TRIO_ENGINE = BRIDGE / "trio_engine.py"

# Add bridge to path
sys.path.insert(0, str(BRIDGE))

def process_user_message(text):
    """
    Sameer AI bot is function ko call karega jab user kuch bole.
    Returns human-readable response.
    """
    from trio_engine import understand_text, execute_task
    
    task = understand_text(text)
    result = execute_task(task)
    
    response_lines = result.get("response", [])
    response = "\n".join(response_lines)
    
    # Add type info
    task_type = task.get("type", "unknown")
    
    return {
        "response": response[:3500],
        "type": task_type,
        "task": task
    }

def is_system_command(text):
    """Check if this is a system command that needs OpenClaw, not AI."""
    from trio_engine import understand_text
    task = understand_text(text)
    task_type = task.get("type", "unknown")
    
    # These need OpenClaw, not AI
    if task_type in ["system", "discussion", "generate_bot", "generate_website", "generate_script", "generate_app"]:
        return True
    return False

def format_for_telegram(result):
    """Format response for Telegram."""
    response = result.get("response", "")
    task_type = result.get("type", "unknown")
    
    # Add prefix based on source
    if task_type == "system":
        return f"⚙️ **OpenClaw Report**\n\n{response}"
    elif task_type in ["generate_bot", "generate_website", "generate_script", "generate_app"]:
        return f"🔧 **Code Factory**\n\n{response}"
    elif task_type == "discussion":
        return f"💡 **Discussion**\n\n{response}"
    elif task_type == "ai_query":
        return f"🤖 **AI Analysis**\n\n{response}"
    elif task_type == "unknown":
        return response[:3500]  # Already has instructions
    
    return response[:3500]

if __name__ == "__main__":
    # Test
    test = "sab kaisa hai"
    result = process_user_message(test)
    print(format_for_telegram(result))
