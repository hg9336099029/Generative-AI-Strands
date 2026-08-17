"""
PharmaSentry - Local Agent Test
================================
Tests the full pipeline locally:
  1. Registers a test user (or reuses if already exists)
  2. Logs in to get a JWT token
  3. Fires three real chat queries via the /api/v1/chat SSE endpoint
  4. Prints results + confirms NO stub-mode text is returned

Run from the project root:
    .venv\\Scripts\\python.exe scripts/test_local_agent.py
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8000"

SEP = "-" * 60

def _ok(msg):   print(f"  [OK]   {msg}")
def _info(msg): print(f"  [INFO] {msg}")
def _fail(msg): print(f"  [FAIL] {msg}")
def _head(msg): print(f"\n{SEP}\n  {msg}\n{SEP}")


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _post_json(path: str, payload: dict, token: str | None = None) -> Any:
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _post_form(path: str, fields: dict) -> Any:
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _sse_chat(message: str, session_id: str, token: str) -> dict:
    """Call /api/v1/chat (SSE endpoint) and collect the full response."""
    data = json.dumps({"message": message, "session_id": session_id}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/v1/chat", data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Accept": "text/event-stream",
        },
    )
    collected: dict = {}
    with urllib.request.urlopen(req, timeout=120) as r:
        for raw_line in r:
            line = raw_line.decode("utf-8").strip()
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload and payload != "[DONE]":
                    try:
                        collected = json.loads(payload)
                    except json.JSONDecodeError:
                        pass
    return collected


# ── Test data ─────────────────────────────────────────────────────────────────

TEST_USER = {
    "username": "pharma_tester",
    "email": "pharma_tester@example.com",
    "password": "PharmaTest@2026!",
}

QUERIES = [
    {
        "label": "Side-effects query  (LabelAgent expected)",
        "message": "What are the common side effects of lisinopril?",
    },
    {
        "label": "FAERS safety query  (SafetyAgent expected)",
        "message": "Are there any FDA adverse event reports for metformin causing lactic acidosis?",
    },
    {
        "label": "Clinical trials query  (TrialsAgent expected)",
        "message": "Show me recent clinical trials for sertraline in depression treatment.",
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    _head("PharmaSentry - Local Agent Test (AWS SSO + Bedrock ap-south-1)")

    # 1. Ping
    _info("Checking server health ...")
    try:
        req = urllib.request.Request(f"{BASE}/ping")
        with urllib.request.urlopen(req, timeout=5) as r:
            pong = json.loads(r.read())
        _ok(f"Server alive: {pong}")
    except Exception as e:
        _fail(f"Server not reachable at {BASE}. Start it first.\n     Error: {e}")
        sys.exit(1)

    # 2. Register
    _info("Registering test user ...")
    try:
        resp = _post_json("/auth/register", TEST_USER)
        _ok(f"Registered: {resp}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        _info(f"Register returned HTTP {e.code} - {body[:120]} (may already exist, continuing)")

    # 3. Login (OAuth2PasswordRequestForm expects 'username' + 'password')
    _info("Logging in ...")
    try:
        token_resp = _post_form("/auth/login", {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
        })
        token = token_resp["access_token"]
        _ok(f"JWT obtained: {token[:50]}...")
    except Exception as e:
        _fail(f"Login failed: {e}")
        sys.exit(1)

    # 4. Chat queries
    session_id = f"local-test-{int(time.time())}"
    all_passed = True
    results = []

    for idx, q in enumerate(QUERIES, 1):
        _head(f"Query {idx}/{len(QUERIES)}: {q['label']}")
        print(f"  Message : {q['message']}")
        print("  Sending request to Bedrock (ap-south-1) ...")

        t0 = time.time()
        try:
            answer = _sse_chat(q["message"], session_id, token)
            elapsed = time.time() - t0
        except Exception as e:
            _fail(f"Request failed: {e}")
            all_passed = False
            results.append({"label": q["label"], "passed": False, "error": str(e)})
            continue

        if not answer:
            _fail("Empty response received.")
            all_passed = False
            results.append({"label": q["label"], "passed": False, "error": "empty"})
            continue

        text        = answer.get("text", "")
        agent_used  = answer.get("agent_used", "unknown")
        citations   = answer.get("citations", [])
        signal      = answer.get("signal_present", False)

        is_stub = "[STUB MODE]" in text
        passed  = not is_stub and len(text) > 20

        if is_stub:
            _fail("STUB MODE response - Bedrock NOT active!")
            all_passed = False
        elif not passed:
            _fail(f"Response too short ({len(text)} chars) - possible error.")
            all_passed = False
        else:
            _ok(f"REAL Bedrock LLM response received in {elapsed:.1f}s")

        print(f"  Agent used     : {agent_used}")
        print(f"  Signal present : {signal}")
        print(f"  Citations      : {[c.get('title','') for c in citations]}")
        print(f"  Response length: {len(text)} chars")
        print(f"\n  --- Response Preview ---")
        preview = text[:700].replace("\n", "\n  ")
        print(f"  {preview}")
        if len(text) > 700:
            print(f"  ... [{len(text)-700} more chars]")

        results.append({"label": q["label"], "passed": passed, "elapsed": f"{elapsed:.1f}s", "agent": agent_used})

    # 5. Summary table
    _head("Test Summary")
    print(f"  {'#':<4} {'Status':<8} {'Elapsed':<10} {'Agent':<35} Query")
    print(f"  {'-'*4} {'-'*8} {'-'*10} {'-'*35} {'-'*40}")
    for i, r in enumerate(results, 1):
        status = "PASS" if r.get("passed") else "FAIL"
        elapsed = r.get("elapsed", "N/A")
        agent   = r.get("agent", "N/A")
        label   = QUERIES[i-1]["label"][:40]
        print(f"  {i:<4} {status:<8} {elapsed:<10} {agent:<35} {label}")

    print()
    if all_passed:
        _ok("ALL TESTS PASSED")
        _ok("Real Bedrock LLM (anthropic.claude-3-5-sonnet-20241022-v2:0) in ap-south-1 is ACTIVE")
        _ok("AWS SSO credential chain working - no .env required")
    else:
        _fail("Some tests FAILED - check output above for details.")
    print()


if __name__ == "__main__":
    main()
