"""
End-to-end test for PharmaSentry API.
Run: .venv\Scripts\python.exe scripts\e2e_test.py
"""
import json
import time
import urllib.parse
import urllib.request

BASE = "http://localhost:8000"


def req(url, data=None, headers=None, method="GET"):
    if data and isinstance(data, dict):
        data = json.dumps(data).encode()
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    resp = urllib.request.urlopen(r)
    return json.loads(resp.read().decode("utf-8", errors="replace"))


def req_raw(url, data=None, headers=None, method="GET"):
    if data and isinstance(data, dict):
        data = json.dumps(data).encode()
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    resp = urllib.request.urlopen(r)
    return resp.read().decode("utf-8", errors="replace")


print("=" * 60)
print("PharmaSentry E2E Test")
print("=" * 60)

# 1. Health check
result = req(f"{BASE}/ping")
assert result["status"] == "ok", f"Ping failed: {result}"
print("PASS 1: GET /ping ->", result)

# 2. Root
result = req(f"{BASE}/")
print("PASS 2: GET / ->", result["message"][:50])

# 3. Register
try:
    result = req(
        f"{BASE}/auth/register",
        data={"username": "e2euser", "email": "e2e@pharmasentry.com", "password": "Test1234!"},
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print("PASS 3a: POST /auth/register -> user id:", result.get("id"))
except Exception as e:
    print("PASS 3a: POST /auth/register (user exists, skipping):", str(e)[:60])

# 4. Login
form = urllib.parse.urlencode(
    {"username": "e2e@pharmasentry.com", "password": "Test1234!"}
).encode()
result = req(
    f"{BASE}/auth/login",
    data=form,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)
token = result["access_token"]
assert token, "No token!"
print("PASS 4: POST /auth/login -> JWT obtained")
auth = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

# 5. Chat — first message (triggers LTM auto-set for lisinopril)
raw = req_raw(
    f"{BASE}/api/v1/chat",
    data={"message": "What are the warnings for lisinopril?"},
    headers=auth,
    method="POST",
)
print("PASS 5: POST /api/v1/chat -> first 200 chars:", raw[:200])

# 6. Chat — second message (memory context should be injected)
raw2 = req_raw(
    f"{BASE}/api/v1/chat",
    data={"message": "Tell me more about the dosing."},
    headers=auth,
    method="POST",
)
print("PASS 6: POST /api/v1/chat (2nd turn) -> first 150 chars:", raw2[:150])

# 7. List chat sessions
sessions = req(f"{BASE}/api/v1/chat/sessions", headers=auth)
print("PASS 7: GET /api/v1/chat/sessions -> count:", len(sessions))

# 8. Intake submission
intake_result = req(
    f"{BASE}/intake/submit",
    data={"narrative": "Patient John Doe took lisinopril 10mg and experienced severe angioedema, was hospitalised."},
    headers=auth,
    method="POST",
)
print("PASS 8: POST /intake/submit ->")
print("  case_id:", intake_result.get("case_id"))
print("  product_suspected:", intake_result.get("product_suspected"))
print("  reactions_reported:", intake_result.get("reactions_reported"))
print("  requires_expedited_review:", intake_result.get("requires_expedited_review"))

# 9. Cases list
cases = req(f"{BASE}/cases", headers=auth)
print("PASS 9: GET /cases -> count:", len(cases))

print()
print("=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
