# NOVA Studio V2 — Starter

A responsive Flask + JavaScript creative workspace foundation.

## Included
- Dark responsive AI creator workspace
- Text-to-video and text-to-image request flows using a configurable fal provider adapter
- Honest demo mode without API credentials
- Server-side API key handling
- Local video/image/audio import, clip selection, playback preview and basic timeline lanes
- Prompt improvement helper

## Not yet included
This is not yet a full CapCut/Adobe replacement. Frame-accurate multi-track rendering, real transition rendering/export, audio mixing, captions, keyframes, persistent cloud projects, login, payments, team sync and subscription enforcement are not implemented. The editor's export downloads the selected original source file only. 4K/120 FPS are selectable targets, not guaranteed output capabilities.

## Run on Windows
1. Install Python 3.11+ from https://www.python.org/downloads/ and enable Add Python to PATH.
2. Extract the ZIP and open a terminal in the `nova_studio_v2` folder.
3. Run:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env
py app.py
```
4. Visit http://127.0.0.1:5000

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Connect real AI
Create an account with an inference provider such as fal. Check its current model catalog, pricing and commercial terms. Copy `.env.example` to `.env`; set `FAL_KEY`, `FAL_VIDEO_MODEL`, and `FAL_IMAGE_MODEL` to the exact values shown by the provider. Different models have different input schemas: update the arguments in `app.py` to match the selected models' current API documentation. Restart the app. Provider usage can cost money; set spending limits where available. Never expose API keys in browser JavaScript or a public repository.

## Public launch checklist
This starter is for local testing. Before public production use, add authentication, CSRF protection, database-backed projects, per-user rate limits/quotas, a job queue, object storage with signed URLs, upload scanning, content moderation, verified payment webhooks, privacy/terms pages, HTTPS, secure headers, backups and monitoring. Deploy with a production WSGI server such as `gunicorn app:app`, not Flask's development server. Use your host's supported configuration and keep `.env` private.

A 4 GB RAM laptop can run the lightweight web interface, but local video rendering would be slow. AI inference runs on the connected provider's infrastructure.
