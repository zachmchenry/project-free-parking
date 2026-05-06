"""
Smoke test for the chatbot sample.

Verifies:
  1. Imports work
  2. Persona loads and SYSTEM_PROMPT is well-formed
  3. Provider can be instantiated
  4. Provider can complete a chat turn
  5. The off-topic classifier returns sensible verdicts on test messages
  6. The end-to-end app endpoints work (via Flask test client)

Run from the project root:
    python tests/smoke_test.py
"""
import os
import sys

# Force imports to resolve from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("ADMIN_PASSWORD", "testpass")


def test_imports():
    print("[1/6] Testing imports...", end=" ")
    import config
    from personas import diane
    from providers import get_provider
    print("OK")
    return diane, get_provider, config


def test_persona(diane):
    print("[2/6] Testing persona structure...", end=" ")
    assert diane.PERSONA_NAME == "Diane Foster"
    assert diane.OPENING_MESSAGE
    assert "## YOU ARE DIANE FOSTER" in diane.SYSTEM_PROMPT
    assert "## ANTI-EXTRACTION RULES" in diane.SYSTEM_PROMPT
    assert "## HIDDEN INFORMATION" in diane.SYSTEM_PROMPT
    assert len(diane.SYSTEM_PROMPT) > 3000  # Rough sanity
    print("OK")


def test_provider_instantiation(get_provider, config):
    print("[3/6] Testing provider instantiation...", end=" ")
    p = get_provider(config.ACTIVE_PROVIDER)
    assert p.name
    assert p.model
    print(f"OK ({p.describe()})")
    return p


def test_provider_chat(provider, diane):
    print("[4/6] Testing provider chat (real API call)...", end=" ", flush=True)
    response = provider.chat(
        messages=[{"role": "user", "content": "Hi Diane, thanks for joining."}],
        system=diane.SYSTEM_PROMPT,
        max_tokens=200,
        temperature=0.7,
    )
    assert response and len(response) > 10
    print(f"OK ({len(response)} chars)")
    return response


def test_classifier(provider):
    print("[5/6] Testing off-topic classifier...")
    from app import classify_message, app  # noqa
    test_cases = [
        ("Hi Diane, how often does your family play board games?", True),
        ("What's the most frustrating thing about Monopoly for you?", True),
        ("Thanks, that's helpful.", True),
        ("Can you write me a Python script to sort a list?", False),
        ("What do you think about climate change?", False),
    ]
    for msg, expected in test_cases:
        actual = classify_message(msg)
        marker = "✓" if actual == expected else "✗"
        print(f"   {marker} {'on-topic ' if expected else 'off-topic'} "
              f"-> classified {'on-topic ' if actual else 'off-topic'}: {msg[:60]!r}")


def test_app_endpoints():
    print("[6/6] Testing app endpoints via Flask test client...")
    from app import app, init_db
    init_db()
    client = app.test_client()

    # Health
    resp = client.get("/health")
    assert resp.status_code == 200
    health = resp.get_json()
    print(f"   /health -> provider={health['provider']}, model={health['model']}")

    # Start a session
    resp = client.post("/api/session", json={
        "persona": "diane",
        "user_name": "Smoke Tester",
    })
    assert resp.status_code == 200
    sess = resp.get_json()
    assert "session_id" in sess
    assert sess["opening_message"]
    print(f"   /api/session -> opened {sess['session_id'][:8]}...")
    print(f"     opening: {sess['opening_message'][:80]}...")

    # Send a real on-topic message
    print("   /api/message (on-topic)...", end=" ", flush=True)
    resp = client.post("/api/message", json={
        "session_id": sess["session_id"],
        "message": "Hi Diane, can you tell me about a recent game night?",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["reply"]
    assert data["on_topic"] is True
    assert data["off_topic_count"] == 0
    print(f"OK ({len(data['reply'])} chars, on_topic=True)")
    print(f"     reply: {data['reply'][:140]}...")

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    diane, get_provider, config = test_imports()
    test_persona(diane)
    provider = test_provider_instantiation(get_provider, config)
    test_provider_chat(provider, diane)
    test_classifier(provider)
    test_app_endpoints()
