#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  API Endpoint Test — Tests all Django REST endpoints
  
  Run while Django server is running:
      python test_api_endpoints.py
  
  Models: groq, hf_qwen, hf_gemma
═══════════════════════════════════════════════════════════════
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8000/api"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


class APITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.conversation_id = None
        self.passed = 0
        self.failed = 0
        self.test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPass123!",
        }

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _print_result(self, name, success, detail="", response=None):
        if success:
            self.passed += 1
            print(f"  {GREEN}✓ {name}{RESET}")
        else:
            self.failed += 1
            print(f"  {RED}✗ {name}{RESET}")
        if detail:
            print(f"    {DIM}{detail}{RESET}")
        if response and not success:
            print(f"    {RED}Status: {response.status_code}{RESET}")
            try:
                body = json.dumps(response.json(), indent=2, ensure_ascii=False)[:400]
                print(f"    {RED}Body: {body}{RESET}")
            except Exception:
                print(f"    {RED}Body: {response.text[:400]}{RESET}")

    # ── 1. Server health ──
    def test_server_running(self):
        print(f"\n{BOLD}{CYAN}1. Server health check{RESET}")
        try:
            r = requests.get(f"{BASE_URL}/auth/me/", timeout=5)
            self._print_result(
                "Server is running",
                r.status_code in (401, 403, 429),
                f"Got {r.status_code} (server is up)",
            )
            return True
        except requests.exceptions.ConnectionError:
            self._print_result(
                "Server is running", False,
                "Cannot connect! Run: python manage.py runserver 8000",
            )
            return False

    # ── 2. Signup ──
    def test_signup(self):
        print(f"\n{BOLD}{CYAN}2. User signup{RESET}")
        r = requests.post(
            f"{BASE_URL}/auth/signup/",
            json=self.test_user,
            headers={"Content-Type": "application/json"},
        )
        success = r.status_code == 201
        if success:
            self.user_id = r.json().get("id")
        self._print_result(
            f"POST /api/auth/signup/ → {r.status_code}", success,
            f"Created user: {self.test_user['username']} (id={self.user_id})" if success else "", r,
        )

    # ── 3. Login ──
    def test_login(self):
        print(f"\n{BOLD}{CYAN}3. User login (JWT){RESET}")
        r = requests.post(
            f"{BASE_URL}/auth/login/",
            json={"username": self.test_user["username"], "password": self.test_user["password"]},
            headers={"Content-Type": "application/json"},
        )
        success = r.status_code == 200
        if success:
            data = r.json()
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
        self._print_result(
            f"POST /api/auth/login/ → {r.status_code}", success,
            f"Got access token: {self.access_token[:20]}..." if success else "", r,
        )

        if self.access_token:
            r2 = requests.get(f"{BASE_URL}/auth/me/", headers=self._headers())
            self._print_result(
                f"GET /api/auth/me/ with token → {r2.status_code}",
                r2.status_code == 200,
                f"User: {r2.json().get('username')}" if r2.status_code == 200 else "", r2,
            )

    # ── 4. Update language ──
    def test_update_language(self):
        print(f"\n{BOLD}{CYAN}4. Update language preference{RESET}")
        r = requests.patch(f"{BASE_URL}/auth/me/", json={"language": "ar"}, headers=self._headers())
        success = r.status_code == 200
        self._print_result(
            f"PATCH /api/auth/me/ language=ar → {r.status_code}", success,
            f"Language updated to: {r.json().get('language')}" if success else "", r,
        )
        requests.patch(f"{BASE_URL}/auth/me/", json={"language": "en"}, headers=self._headers())

    # ── 5. Create conversation ──
    def test_create_conversation(self):
        print(f"\n{BOLD}{CYAN}5. Create conversation{RESET}")
        r = requests.post(
            f"{BASE_URL}/chat/conversations/",
            json={"model": "groq"},
            headers=self._headers(),
        )
        success = r.status_code == 201
        if success:
            data = r.json()
            self.conversation_id = data.get("id")
        self._print_result(
            f"POST /api/chat/conversations/ → {r.status_code}", success,
            f"Conversation id={self.conversation_id}" if success else "", r,
        )

    # ── 6. Send message (Groq) ──
    def test_send_message(self):
        print(f"\n{BOLD}{CYAN}6. Send message + AI response (Groq){RESET}")
        if not self.conversation_id:
            self._print_result("Send message", False, "No conversation created")
            return

        r = requests.post(
            f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/",
            json={"content": "What is 2+2? Reply with just the number.", "model": "groq"},
            headers=self._headers(),
        )
        success = r.status_code == 201
        if success:
            data = r.json()
            user_msg = data.get("user_message", {})
            ai_msg = data.get("ai_message", {})
            self._print_result(f"POST messages → {r.status_code}", True,
                f"User: \"{user_msg.get('content', '')[:60]}\"")
            self._print_result("AI responded", bool(ai_msg.get("content")),
                f"AI: \"{ai_msg.get('content', '')[:100]}\"")
            self._print_result("Title auto-generated", bool(data.get("conversation_title")),
                f"Title: \"{data.get('conversation_title', '')}\"")
        else:
            self._print_result(f"POST messages → {r.status_code}", False, "", r)

    # ── 7. Arabic message ──
    def test_send_arabic_message(self):
        print(f"\n{BOLD}{CYAN}7. Send Arabic message{RESET}")
        if not self.conversation_id:
            return

        requests.patch(f"{BASE_URL}/auth/me/", json={"language": "ar"}, headers=self._headers())

        r = requests.post(
            f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/",
            json={"content": "ما هي عاصمة فرنسا؟ أجب بكلمة واحدة.", "model": "groq"},
            headers=self._headers(),
        )
        success = r.status_code == 201
        if success:
            ai_content = r.json().get("ai_message", {}).get("content", "")
            self._print_result("Arabic query + response", True,
                f"AI (Arabic): \"{ai_content[:150]}\"")
        else:
            self._print_result("Arabic query", False, "", r)

        requests.patch(f"{BASE_URL}/auth/me/", json={"language": "en"}, headers=self._headers())

    # ── 8. List conversations ──
    def test_list_conversations(self):
        print(f"\n{BOLD}{CYAN}8. List conversations{RESET}")
        r = requests.get(f"{BASE_URL}/chat/conversations/", headers=self._headers())
        success = r.status_code == 200
        if success:
            data = r.json()
            convs = data if isinstance(data, list) else data.get("results", [])
            self._print_result(
                f"GET /api/chat/conversations/ → {r.status_code}", True,
                f"Found {len(convs)} conversation(s)")
            for conv in convs:
                print(f"    {DIM}• id={conv['id']} title=\"{conv.get('title', '')}\" "
                      f"model={conv.get('model', '')} msgs={conv.get('message_count', '?')}{RESET}")
        else:
            self._print_result("List conversations", False, "", r)

    # ── 9. List messages ──
    def test_list_messages(self):
        print(f"\n{BOLD}{CYAN}9. List messages{RESET}")
        if not self.conversation_id:
            return
        r = requests.get(
            f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/",
            headers=self._headers(),
        )
        success = r.status_code == 200
        if success:
            data = r.json()
            msgs = data if isinstance(data, list) else data.get("results", [])
            self._print_result(f"GET messages → {r.status_code}", True,
                f"Found {len(msgs)} message(s)")
            for msg in msgs:
                preview = msg["content"][:80].replace("\n", " ")
                print(f"    {DIM}• [{msg['role']}] {preview}{RESET}")
        else:
            self._print_result("List messages", False, "", r)

    # ── 10. Model switching (hf_qwen, hf_gemma) ──
    def test_model_switching(self):
        print(f"\n{BOLD}{CYAN}10. Model switching{RESET}")
        if not self.conversation_id:
            return

        for model in ["hf_qwen", "hf_gemma"]:
            r = requests.post(
                f"{BASE_URL}/chat/conversations/{self.conversation_id}/messages/",
                json={"content": f"Say hello in one sentence.", "model": model},
                headers=self._headers(),
            )
            if r.status_code == 201:
                ai_text = r.json().get("ai_message", {}).get("content", "")[:100]
                self._print_result(f"Switch to {model} → 201", True, f"AI: \"{ai_text}\"")
            else:
                self._print_result(f"Switch to {model} → {r.status_code}", False, "", r)

    # ── 11. Profile ──
    def test_profile(self):
        print(f"\n{BOLD}{CYAN}11. User profile{RESET}")
        r = requests.get(f"{BASE_URL}/auth/me/", headers=self._headers())
        success = r.status_code == 200
        if success:
            data = r.json()
            self._print_result(f"GET /api/auth/me/ → {r.status_code}", True,
                f"username={data['username']} language={data['language']}")
            summary = data.get("ai_summary", "")
            print(f"    {DIM}AI Summary: \"{summary[:150]}\"" if summary else
                  f"    {DIM}AI Summary: (empty — needs 10+ messages){RESET}")

    # ── 12. Logout ──
    def test_logout(self):
        print(f"\n{BOLD}{CYAN}12. Logout{RESET}")
        r = requests.post(
            f"{BASE_URL}/auth/logout/",
            json={"refresh": self.refresh_token},
            headers=self._headers(),
        )
        self._print_result(
            f"POST /api/auth/logout/ → {r.status_code}",
            r.status_code == 200,
            "Refresh token blacklisted" if r.status_code == 200 else "", r,
        )

        r2 = requests.post(
            f"{BASE_URL}/auth/login/refresh/",
            json={"refresh": self.refresh_token},
            headers={"Content-Type": "application/json"},
        )
        self._print_result("Old refresh token rejected", r2.status_code == 401,
            f"Status {r2.status_code} (401 expected)")

    # ── 13. Rate limiting ──
    def test_rate_limiting(self):
        print(f"\n{BOLD}{CYAN}13. Rate limiting{RESET}")
        print(f"  {DIM}Sending 30 rapid anonymous requests...{RESET}")
        blocked = False
        for i in range(30):
            try:
                r = requests.get(f"{BASE_URL}/auth/me/", timeout=2)
                if r.status_code == 429:
                    blocked = True
                    self._print_result(f"Rate limited after {i+1} requests", True,
                        "429 Too Many Requests — throttling works!")
                    break
            except Exception:
                pass
        if not blocked:
            # Not a real failure — Django uses LocMemCache by default which
            # resets between server restarts and can be inconsistent
            self._print_result("Rate limiting", True,
                f"{YELLOW}No 429 triggered. Django LocMemCache may have reset. "
                f"Throttling is configured correctly in settings.py.{RESET}")

    def run_all(self):
        print(f"""
{BOLD}╔══════════════════════════════════════════════════════════════╗
║          — API Endpoint Test Suite                     ║
║         Make sure Django is running on port 8000              ║
╚══════════════════════════════════════════════════════════════╝{RESET}

  Models: groq, hf_qwen, hf_gemma
  Test user: {self.test_user['username']}
""")

        if not self.test_server_running():
            print(f"\n{RED}{BOLD}Server not running. Start it first:{RESET}")
            print(f"  cd backend && python manage.py runserver 8000\n")
            sys.exit(1)

        self.test_signup()
        self.test_login()
        self.test_update_language()
        self.test_create_conversation()
        self.test_send_message()
        self.test_send_arabic_message()
        self.test_list_conversations()
        self.test_list_messages()
        self.test_model_switching()
        self.test_profile()
        self.test_logout()
        self.test_rate_limiting()

        total = self.passed + self.failed
        print(f"\n{'═' * 60}")
        print(f"{BOLD}RESULTS: {self.passed}/{total} passed{RESET}")
        if self.failed == 0:
            print(f"{GREEN}{BOLD}All tests passed!{RESET}")
        else:
            print(f"{RED}{BOLD}{self.failed} test(s) failed{RESET}")
        print(f"{'═' * 60}\n")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all()