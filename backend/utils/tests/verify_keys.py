#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  API Key Verifier — Quick check if your keys actually work
  
  Run: python verify_keys.py
  
  No Django needed. Just reads .env and makes one test call
  per provider. Shows exact HTTP status + error message.
═══════════════════════════════════════════════════════════════
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

PAYLOAD = {
    "messages": [{"role": "user", "content": "Say hi"}],
    "max_tokens": 10,
    "temperature": 0.1,
}


def test_key(name, url, key, model, extra_headers=None):
    """Test a single API key with a minimal request."""
    print(f"\n{BOLD}{CYAN}── {name} ──{RESET}")

    if not key:
        print(f"  {YELLOW}⚠ NO KEY SET{RESET}")
        print(f"  Add it to your .env file")
        return False

    print(f"  Key: {key[:12]}...{key[-4:]}")
    print(f"  URL: {url}")
    print(f"  Model: {model}")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    body = {**PAYLOAD, "model": model}

    try:
        r = requests.post(url, headers=headers, json=body, timeout=30)
        print(f"  HTTP Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            print(f"  {GREEN}✓ KEY WORKS!{RESET}")
            print(f"  Response: \"{content.strip()[:80]}\"")
            return True
        else:
            print(f"  {RED}✗ FAILED{RESET}")
            try:
                err = r.json()
                print(f"  Error: {err}")
            except Exception:
                print(f"  Body: {r.text[:300]}")

            # Common fixes
            if r.status_code == 401:
                print(f"\n  {YELLOW}FIX: Your API key is invalid or expired.{RESET}")
                print(f"  {YELLOW}     Generate a NEW key from the provider's dashboard.{RESET}")
            elif r.status_code == 403:
                print(f"\n  {YELLOW}FIX: Key lacks permissions. Check token scopes.{RESET}")
            elif r.status_code == 404:
                print(f"\n  {YELLOW}FIX: Model not found. It may have been renamed.{RESET}")
            elif r.status_code == 429:
                print(f"\n  {YELLOW}FIX: Rate limited. Wait a minute and retry.{RESET}")
            return False

    except requests.exceptions.Timeout:
        print(f"  {RED}✗ TIMEOUT (30s){RESET}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  {RED}✗ CONNECTION ERROR: {e}{RESET}")
        return False


def main():
    print(f"""
{BOLD}╔══════════════════════════════════════════════════════════════╗
║                               ║
║         Tests each key with a single minimal request          ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    groq_key = os.getenv("GROQ_API_KEY", "")
    hf_key = os.getenv("HUGGINGFACE_API_KEY", "")

    results = {}

    # ── Groq ──
    results["Groq"] = test_key(
        name="Groq (LLaMA 3.3 70B)",
        url="https://api.groq.com/openai/v1/chat/completions",
        key=groq_key,
        model="llama-3.3-70b-versatile",
    )

    # ── HuggingFace Model 1: Qwen ──
    results["HuggingFace (Qwen)"] = test_key(
        name="Qwen/Qwen2.5-7B-Instruct",
        url="https://router.huggingface.co/v1/chat/completions",
        key=hf_key,
        model="Qwen/Qwen2.5-7B-Instruct",
    )

    results["HuggingFace (Gemma)"] = test_key(
    name="HuggingFace — Gemma 3-27b-it",
    url="https://router.huggingface.co/v1/chat/completions",
    key=hf_key,
    model="google/gemma-3-27b-it",
)
    # ── Summary ──
    print(f"\n{'═' * 60}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'═' * 60}")
    for name, ok in results.items():
        icon = f"{GREEN}✓" if ok else f"{RED}✗"
        print(f"  {icon} {name}{RESET}")

    print(f"\n{BOLD}How to get keys:{RESET}")
    print(f"  Groq:        https://console.groq.com/keys")
    print(f"               → Sign up → Create API Key → copy gsk_...")
    print(f"  HuggingFace: https://huggingface.co/settings/tokens")
    print(f"               → Create fine-grained token")
    print(f"               → Enable 'Make calls to Inference Providers'")
    print(f"               → copy hf_...")

    print(f"\n{BOLD}Your .env should look like:{RESET}")
    print(f"  GROQ_API_KEY=gsk_aBcDeFgH1234567890...")
    print(f"  HUGGINGFACE_API_KEY=hf_aBcDeFgH1234567890...")
    print()


if __name__ == "__main__":
    main()
