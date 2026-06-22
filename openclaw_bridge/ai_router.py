"""
ai_router.py — Smart AI Router for OpenClaw
Auto-routes tasks to best available model:
- Simple → Ollama local (free)
- Complex → DeepSeek (sasta)
- Coding → Claude Code (CLI)
- Reasoning → DeepSeek Reasoner
"""

import subprocess
import json
import os
import time
import sys
from typing import Dict, Optional

# ─── CONFIG ───────────────────────────────────────────────────────────

CLASSIFY_PROMPT = """Analyze this task and classify it as one of: simple, coding, complex, reasoning.
Output ONLY one word.

Task: {task}
Classification:"""

# ─── ENGINE REGISTRY ─────────────────────────────────────────────────

class AIEngine:
    """Base class for AI engines."""
    
    def __init__(self, name: str, cost_per_m: float = 0, free: bool = True):
        self.name = name
        self.cost_per_m = cost_per_m  # Cost per million tokens
        self.free = free
        self.stats = {"calls": 0, "tokens": 0, "total_cost": 0}
    
    def can_handle(self, classification: str) -> bool:
        """Override in subclass."""
        return False
    
    def execute(self, prompt: str, max_tokens: int = 2000) -> Dict:
        """Execute with given prompt. Returns dict with success/response/error."""
        raise NotImplementedError


class OllamaEngine(AIEngine):
    """Local Ollama models — 100% free."""
    
    def __init__(self, model: str = "qwen2.5:3b"):
        super().__init__(f"Ollama/{model}", free=True)
        self.model = model
    
    def can_handle(self, classification: str) -> bool:
        return classification == "simple"
    
    def execute(self, prompt: str, max_tokens: int = 2000) -> Dict:
        start = time.time()
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode(),
                capture_output=True,
                timeout=120,
            )
            response = result.stdout.decode().strip()
            self.stats["calls"] += 1
            self.stats["tokens"] += len(response) // 4
            return {"success": True, "engine": self.name, "response": response, 
                    "time": round(time.time() - start, 2), "free": True}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout after 120s", "engine": self.name}
        except Exception as e:
            return {"success": False, "error": str(e)[:200], "engine": self.name}


class DeepSeekEngine(AIEngine):
    """DeepSeek API — low cost, high quality."""
    
    def __init__(self, model: str = "deepseek-chat", api_key: Optional[str] = None):
        cost = {"deepseek-chat": 0.28, "deepseek-v4-flash": 0.14, 
                "deepseek-reasoner": 0.28, "deepseek-v4-pro": 1.74}.get(model, 0.28)
        super().__init__(f"DeepSeek/{model}", cost_per_m=cost, free=False)
        self.model = model
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            for path in ["/root/.openclaw/.env", "/root/sameer_ai_manager/.env"]:
                if os.path.exists(path):
                    for line in open(path):
                        if line.startswith("DEEPSEEK_API_KEY="):
                            self.api_key = line.split("=", 1)[1].strip().strip("'\"")
                            break
                if self.api_key:
                    break
    
    def can_handle(self, classification: str) -> bool:
        return classification in ("complex", "reasoning")
    
    def execute(self, prompt: str, max_tokens: int = 4000) -> Dict:
        if not self.api_key:
            return {"success": False, "error": "No API key", "engine": self.name}
        
        start = time.time()
        try:
            import urllib.request
            data = json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            }).encode()
            
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            
            response = result["choices"][0]["message"]["content"].strip()
            usage = result.get("usage", {})
            tokens = usage.get("total_tokens", len(response) // 4)
            cost = (tokens / 1_000_000) * self.cost_per_m
            
            self.stats["calls"] += 1
            self.stats["tokens"] += tokens
            self.stats["total_cost"] += cost
            
            return {"success": True, "engine": self.name, "response": response,
                    "time": round(time.time() - start, 2), "tokens": tokens,
                    "cost": round(cost, 6), "free": False}
        
        except Exception as e:
            return {"success": False, "error": str(e)[:200], "engine": self.name}


class ClaudeCodeEngine(AIEngine):
    """Claude Code CLI — for complex coding tasks."""
    
    def __init__(self):
        super().__init__("Claude Code CLI", cost_per_m=0, free=True)  # Free if using CLI
        self._check_available()
    
    def _check_available(self):
        try:
            r = subprocess.run(["which", "claude"], capture_output=True, text=True)
            self.available = r.returncode == 0
        except:
            self.available = False
    
    def can_handle(self, classification: str) -> bool:
        return classification == "coding" and self.available
    
    def execute(self, prompt: str, max_tokens: int = 4000) -> Dict:
        if not self.available:
            return {"success": False, "error": "Claude CLI not available", "engine": self.name}
        
        start = time.time()
        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "CLAUDE_CODE_HEADLESS": "1"}
            )
            response = result.stdout.strip() or result.stderr.strip()
            self.stats["calls"] += 1
            return {"success": True, "engine": self.name, "response": response,
                    "time": round(time.time() - start, 2), "free": True}
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Claude timeout after 120s", "engine": self.name}
        except Exception as e:
            return {"success": False, "error": str(e)[:200], "engine": self.name}


# ─── AUTO ROUTER ────────────────────────────────────────────────────

class AutoRouter:
    """Intelligently routes tasks to best available engine."""
    
    def __init__(self):
        self.engines = [
            OllamaEngine("qwen2.5:3b"),
            OllamaEngine("llama3.2:1b"),
            DeepSeekEngine("deepseek-chat"),
            DeepSeekEngine("deepseek-reasoner"),
            DeepSeekEngine("deepseek-v4-flash"),
            ClaudeCodeEngine(),
        ]
        self.total_calls = 0
        self.total_cost = 0.0
    
    def classify(self, task: str) -> str:
        """Classify task complexity."""
        task_lower = task.lower()
        
        # Coding keywords
        coding_keywords = [
            "code", "function", "class", "api", "endpoint", "route",
            "script", "module", "refactor", "implement", "bug", "debug",
            "error", "fix", "syntax", "compile", "deploy", "npm", "pip",
            "javascript", "python", "typescript", "react", "node",
            "generate code", "write code", "create function",
        ]
        
        # Complex reasoning keywords
        complex_keywords = [
            "architecture", "design", "strategy", "analyze", "compare",
            "optimize", "security", "architecture decision",
            "trade-off", "scalability", "performance",
        ]
        
        # Python code check
        if any(kw in task_lower for kw in coding_keywords):
            return "coding"
        
        if any(kw in task_lower for kw in complex_keywords):
            return "complex"
        
        if len(task) > 500:
            return "complex"
        
        return "simple"
    
    def route(self, task: str, max_tokens: int = 2000) -> Dict:
        """Route task to best engine and execute."""
        classification = self.classify(task)
        self.total_calls += 1
        
        # Try engines in priority order for this classification
        for engine in self.engines:
            if engine.can_handle(classification):
                result = engine.execute(task, max_tokens)
                result["classification"] = classification
                if result.get("success"):
                    cost = result.get("cost", 0)
                    self.total_cost += cost
                    result["total_cost_sofar"] = round(self.total_cost, 6)
                    return result
        
        # Fallback: try any available engine
        for engine in self.engines:
            try:
                result = engine.execute(task, max_tokens)
                if result.get("success"):
                    result["classification"] = f"{classification}_fallback"
                    return result
            except:
                continue
        
        return {"success": False, "error": "No engine available", "classification": classification}
    
    def status(self) -> str:
        """Get status report."""
        parts = [f"🤖 *AI ROUTER STATUS*", "═" * 25]
        parts.append(f"Calls: {self.total_calls} | Total Cost: ₹{self.total_cost:.4f}")
        parts.append("")
        
        for engine in self.engines:
            status = "✅" if engine.stats["calls"] > 0 else "⏳"
            cost_info = f" (${engine.cost_per_m}/M)" if not engine.free else " (FREE)"
            parts.append(f"  {status} {engine.name}{cost_info}")
            if engine.stats["calls"] > 0:
                parts.append(f"     Calls: {engine.stats['calls']} | Tokens: {engine.stats['tokens']}")
        
        return "\n".join(parts)


# ─── GLOBAL INSTANCE ─────────────────────────────────────────────────

_router = None

def get_router() -> AutoRouter:
    global _router
    if _router is None:
        _router = AutoRouter()
    return _router

def ask(prompt: str, max_tokens: int = 2000) -> str:
    """Simple API: ask a question, get answer from best engine."""
    router = get_router()
    result = router.route(prompt, max_tokens)
    if result.get("success"):
        return f"[{result['engine']}] {result['response']}"
    return f"❌ {result.get('error', 'Unknown error')}"


# ─── CLI ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    router = get_router()
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = router.route(prompt)
        print(f"\n{'═'*50}")
        print(f"🎯 Classification: {result.get('classification', '?')}")
        print(f"🤖 Engine: {result.get('engine', '?')}")
        print(f"⏱ Time: {result.get('time', '?')}s")
        if result.get('cost'):
            print(f"💰 Cost: ${result['cost']}")
        print(f"{'═'*50}\n")
        print(result.get('response', result.get('error', '?')))
    else:
        print(router.status())
