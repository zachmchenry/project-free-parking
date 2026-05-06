# Project Free Parking

Dockerized Flask web app for Project Free Parking stakeholder interview simulations. Trainees enter their name, choose one of five persona chatbots from a lobby, interview the stakeholder, then end the chat or log out to receive a short summary. Admins can configure the LLM provider and review per-user conversation logs.

## Features

- Name entry and persona lobby for Diane, Sarah, Marcus, Theo, and Mrs. Choi.
- Persona-specific chat sessions with off-topic detection and cut-off behavior.
- Persistent browser timer across lobby and chat pages.
- End-chat and logout flows with transcript-backed summaries.
- Admin-only provider/model configuration.
- Admin-only user log browser and transcript viewer.
- SQLite persistence for local and small-cohort deployments.
- Docker Compose setup with a persistent data volume.

## Quick Start

```bash
cp .env.example .env
# Edit .env with a real ADMIN_PASSWORD and provider API key.
export ADMIN_PASSWORD='choose-a-real-admin-password'
export LLM_PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

Open `http://127.0.0.1:5000`.

The admin page is at `http://127.0.0.1:5000/admin` and uses HTTP Basic Auth with `ADMIN_USERNAME` (default `admin`) and `ADMIN_PASSWORD`.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ADMIN_PASSWORD='dev-admin-password'
export LLM_PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-...
python app.py
```

For an offline integration check that does not call an LLM provider:

```bash
python tests/smoke_test_mock.py
```

For a real provider smoke test:

```bash
python tests/smoke_test.py
```

## Project Structure

```text
project-free-parking/
├── app.py                    Flask routes, session lifecycle, summaries, admin logs
├── config.py                 Runtime configuration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── docs/
│   └── personas/             Persona documentation and calibration notes
├── personas/                 Persona prompts and metadata
├── providers/                LLM provider abstraction and implementations
├── static/                   Browser JavaScript and CSS
├── templates/                Flask/Jinja pages
└── tests/                    Smoke tests
```

## Runtime Configuration

Provider selection is not exposed to trainees. Admins can change provider/model at `/admin`.

Supported provider values:

| Provider | `LLM_PROVIDER` | Required env vars |
| --- | --- | --- |
| Anthropic Claude | `claude` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai` | `OPENAI_API_KEY` |
| AWS Bedrock | `bedrock` | AWS credentials + `AWS_REGION` |
| Google Gemini | `gemini` | `GEMINI_API_KEY` |

Useful environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ADMIN_USERNAME` | `admin` | Basic Auth username for admin pages |
| `ADMIN_PASSWORD` | empty | Enables protected admin pages when set |
| `CHATBOT_DB` | `chatbot_sessions.db` | SQLite database path |
| `ADMIN_SETTINGS_PATH` | `admin_settings.json` | Persisted provider config path |
| `PORT` | `5000` | App port |

Docker Compose stores logs and admin settings in the `chatbot_data` volume.

## Admin Logs

Admins can review logs at:

- `/admin/logs` for user-grouped activity.
- `/admin/logs/user?name=<name>` for one trainee's sessions.
- `/admin/logs/session/<session_id>` for a transcript.

The JSON transcript endpoint is also admin-protected:

```text
GET /api/transcript?session_id=<hex_id>
```

## Adding Personas

1. Add a new module in `personas/`.
2. Export `SYSTEM_PROMPT`, `PERSONA_NAME`, `PERSONA_ROLE`, `PERSONA_AVATAR_INITIAL`, and `OPENING_MESSAGE`.
3. Register it in `personas/__init__.py` inside `ALL_PERSONAS`.
4. Add a card detail entry in `PERSONA_CARD_DETAILS` in `app.py`.

The shared prompt spine lives in `personas/_spine.py`.

## Production Notes

This app is suitable for local demos and small controlled deployments. Before broader production use, add trainee/cohort authentication, rate limiting, HTTPS, database backups/rotation, and a production database such as PostgreSQL.
