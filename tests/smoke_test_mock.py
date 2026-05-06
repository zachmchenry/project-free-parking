"""
Smoke test using a mock provider — validates the full app stack
without making real API calls.

This proves: imports work, persona is well-formed, the Flask app
correctly orchestrates the cut-off mechanism, and the database
captures conversations as expected.
"""
import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


# ---- Build a mock provider ----
class MockProvider:
    """Echoes a reasonable persona-ish reply, used for testing only."""
    name = "mock"
    model = "mock-1.0"

    def __init__(self):
        self.calls = []

    def chat(self, messages, system, max_tokens=1024, temperature=0.7):
        self.calls.append({"messages": messages, "system": system})
        # The classifier runs as a separate provider call with a special system prompt.
        # We detect that and return ON_TOPIC / OFF_TOPIC accordingly.
        if "ON_TOPIC" in system and "OFF_TOPIC" in system:
            # It's the classifier. Look at the user message and decide.
            user_msg = messages[-1]["content"].lower()
            offtopic_keywords = [
                "python", "code", "weather", "climate", "politics",
                "homework", "translate", "stock", "recipe",
            ]
            if any(k in user_msg for k in offtopic_keywords):
                return "OFF_TOPIC"
            return "ON_TOPIC"
        # Otherwise it's a persona reply. Return a fake Diane-ish answer.
        if "## SESSION CONTEXT" in system and "withdrawal" in system.lower():
            return ("I should run — good luck with the project. Feel free "
                    "to start fresh if something specific comes up.")
        if "## SESSION CONTEXT" in system:
            return ("Sorry — was there something specific about the "
                    "redesign you wanted to ask?")
        return ("[mock Diane reply] Yeah, last time we played it took "
                "ages and the kids lost interest about halfway through.")

    def describe(self):
        return f"{self.name} ({self.model})"


def main():
    # Patch the provider before importing app
    import providers as providers_pkg
    mock = MockProvider()
    providers_pkg.get_provider = lambda name: mock

    # Use a temp db so we don't pollute anything
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.environ["CHATBOT_DB"] = db_path
    os.environ["ADMIN_PASSWORD"] = "testpass"

    # Need to invalidate any cached imports of app.py
    for mod in list(sys.modules):
        if mod in ("app", "config"):
            del sys.modules[mod]

    print("[1/5] Importing app with mock provider...", end=" ", flush=True)
    import app as app_module
    app_module.provider = mock
    app_module.init_db()
    client = app_module.app.test_client()
    print("OK")

    print("[2/5] /health endpoint...", end=" ", flush=True)
    r = client.get("/health")
    assert r.status_code == 200, r.data
    h = r.get_json()
    assert h["provider"] == "mock"
    print(f"OK ({h['provider']}/{h['model']})")

    print("[3/5] /api/session...", end=" ", flush=True)
    r = client.post("/api/session", json={
        "persona": "diane",
        "user_name": "Test User",
    })
    assert r.status_code == 200
    sess = r.get_json()
    sid = sess["session_id"]
    assert sess["opening_message"]
    print(f"OK (session {sid[:8]})")

    print("[4/5] On-topic message flow...", end=" ", flush=True)
    r = client.post("/api/message", json={
        "session_id": sid,
        "message": "Hi Diane, can you tell me about how your family plays Monopoly?",
    })
    data = r.get_json()
    assert r.status_code == 200, data
    assert data["on_topic"] is True
    assert data["off_topic_count"] == 0
    assert data["cut_off"] is False
    assert data["reply"]
    print("OK (on_topic=True, count=0)")

    print("[5/5] Off-topic cut-off cascade...")
    # Send 4 off-topic messages and watch the counter escalate.
    for i in range(1, 5):
        r = client.post("/api/message", json={
            "session_id": sid,
            "message": f"Can you write me a python program to sort a list? attempt {i}",
        })
        data = r.get_json()
        print(f"   Off-topic msg {i}: count={data['off_topic_count']}, "
              f"cut_off={data['cut_off']}, state={data['state']}")
        if i < 4:
            assert data["cut_off"] is False
            assert data["off_topic_count"] == i
        else:
            assert data["cut_off"] is True
            assert data["state"] == "ended"

    print("\n[bonus] /api/transcript on the dead session...")
    r = client.get(
        f"/api/transcript?session_id={sid}",
        headers={"Authorization": "Basic YWRtaW46dGVzdHBhc3M="},
    )
    t = r.get_json()
    assert t["cut_off"] is True
    assert len(t["messages"]) >= 8
    print(f"   Transcript has {len(t['messages'])} messages, cut_off={t['cut_off']}")
    user_msgs = [m for m in t["messages"] if m["role"] == "user"]
    print(f"   User messages on/off-topic flags: "
          f"{[m['on_topic'] for m in user_msgs]}")

    print("\n[bonus] Sending one more message after cut-off...")
    r = client.post("/api/message", json={
        "session_id": sid,
        "message": "Are you still there?",
    })
    data = r.get_json()
    print(f"   Post-cutoff response cut_off={data['cut_off']}")
    assert data["cut_off"] is True

    print("\n[bonus] Ending user session...")
    r = client.post("/api/user/end", json={
        "user_name": "Test User",
        "session_ids": [sid],
        "total_elapsed_seconds": 180,
        "persona_durations": {"diane": 180},
    })
    data = r.get_json()
    assert r.status_code == 200, data
    assert data["summary"]
    assert data["session_count"] == 1
    print(f"   User summary: {data['summary'][:100]}...")

    print("\nAll integration tests passed.")
    print(f"Mock provider received {len(mock.calls)} total calls.")
    os.unlink(db_path)


if __name__ == "__main__":
    main()
