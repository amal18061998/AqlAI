#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  AI Provider Test — Tests Groq, HuggingFace directly
  
  Run: python test_ai_providers.py
  
  This script tests the AI service layer WITHOUT Django.
  It imports the provider classes directly and calls them.
  Use this FIRST to verify your API keys work.
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import time

# Add backend to path so we can import ai_services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env manually (without Django)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Mock Django settings since providers read from django.conf.settings
# We create a minimal mock that reads from environment
class MockSettings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    # DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Patch django.conf.settings before importing providers
import types
django_conf = types.ModuleType("django")
django_conf.conf = types.ModuleType("conf")
django_conf.conf.settings = MockSettings()
sys.modules["django"] = django_conf
sys.modules["django.conf"] = django_conf.conf

from llm_services.groq_provider import GroqProvider
from llm_services.huggingface_qwen_provider import HuggingFaceQwenProvider


# ── Colors for terminal output ──
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def test_provider(name, provider, api_key):
    """Test a single AI provider with English and Arabic prompts."""
    print(f"\n{'─' * 60}")
    print(f"{BOLD}{CYAN}Testing: {name}{RESET}")
    print(f"{'─' * 60}")

    if not api_key:
        print(f"  {YELLOW}⚠  SKIPPED — No API key set for {name}{RESET}")
        print(f"  Set {name.upper().replace(' ', '_').replace('(', '').replace(')', '')}_API_KEY in .env")
        return False

    print(f"  API key: {api_key[:8]}...{api_key[-4:]}")

    # Test 1: English response
    print(f"\n  {BOLD}Test 1: English query{RESET}")
    messages_en = [{"role": "user", "content": "What is Python? Answer in one sentence."}]
    try:
        start = time.time()
        response_en = provider.generate_response(messages_en, language="en")
        elapsed = time.time() - start
        print(f"  {GREEN}✓ Response ({elapsed:.1f}s):{RESET}")
        print(f"    {response_en[:200]}")
    except Exception as e:
        print(f"  {RED}✗ FAILED: {e}{RESET}")
        return False

    # Test 2: Arabic response
    print(f"\n  {BOLD}Test 2: Arabic query{RESET}")
    messages_ar = [{"role": "user", "content": "ما هو الذكاء الاصطناعي؟ أجب في جملة واحدة."}]
    try:
        start = time.time()
        response_ar = provider.generate_response(messages_ar, language="ar")
        elapsed = time.time() - start
        print(f"  {GREEN}✓ Response ({elapsed:.1f}s):{RESET}")
        print(f"    {response_ar[:200]}")
    except Exception as e:
        print(f"  {RED}✗ FAILED: {e}{RESET}")
        return False

    # Test 3: Multi-turn conversation
    print(f"\n  {BOLD}Test 3: Multi-turn conversation{RESET}")
    messages_multi = [
        {"role": "user", "content": "My name is Ahmed."},
        {"role": "assistant", "content": "Nice to meet you, Ahmed!"},
        {"role": "user", "content": "What is my name?"},
    ]
    try:
        start = time.time()
        response_multi = provider.generate_response(messages_multi, language="en")
        elapsed = time.time() - start
        has_name = "ahmed" in response_multi.lower()
        status = f"{GREEN}✓" if has_name else f"{YELLOW}⚠"
        print(f"  {status} Response ({elapsed:.1f}s) — remembers name: {has_name}{RESET}")
        print(f"    {response_multi[:200]}")
    except Exception as e:
        print(f"  {RED}✗ FAILED: {e}{RESET}")
        return False

    print(f"\n  {GREEN}{BOLD}✓ {name} — ALL TESTS PASSED{RESET}")
    return True


def main():
    print(f"""
{BOLD}╔══════════════════════════════════════════════════════════════╗
║            — AI Provider Test Suite                    ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    providers = [
        ("Groq (LLaMA)", GroqProvider(), MockSettings.GROQ_API_KEY),
        # ("DeepSeek", DeepSeekProvider(), MockSettings.DEEPSEEK_API_KEY),
        ("HuggingFace", HuggingFaceQwenProvider(), MockSettings.HUGGINGFACE_API_KEY),
    ]

    results = {}
    for name, provider, api_key in providers:
        results[name] = test_provider(name, provider, api_key)

    # Summary
    print(f"\n{'═' * 60}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'═' * 60}")
    for name, passed in results.items():
        if passed:
            print(f"  {GREEN}✓ {name} — PASSED{RESET}")
        elif passed is False and not locals():
            print(f"  {YELLOW}⚠ {name} — SKIPPED (no API key){RESET}")
        else:
            status = f"{GREEN}✓ PASSED" if passed else f"{RED}✗ FAILED"
            print(f"  {status} — {name}{RESET}")

    all_skipped = not any(results.values())
    if all_skipped:
        print(f"\n  {YELLOW}{BOLD}⚠  All providers skipped!{RESET}")
        print(f"  {YELLOW}  Edit .env and add at least one API key.{RESET}")
        print(f"  {YELLOW}  Groq is recommended (free, fast): https://console.groq.com{RESET}")


if __name__ == "__main__":
    main()
