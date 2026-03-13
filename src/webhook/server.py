"""Pluggy webhook receiver.

Listens for Pluggy events and writes them to a log file that the
Streamlit app can poll to invalidate its cache.

Run with:
    uv run uvicorn src.webhook.server:app --host 0.0.0.0 --port 8000 --reload

Then expose publicly with ngrok:
    ngrok http 8000
"""
from __future__ import annotations

import hashlib
import hmac as hmac_module
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("orbita.webhook")

# ── Config ─────────────────────────────────────────────────────────────────

# Optional: set PLUGGY_WEBHOOK_SECRET in .env to verify signatures
WEBHOOK_SECRET = os.getenv("PLUGGY_WEBHOOK_SECRET", "")

EVENTS_LOG = Path(__file__).parent.parent.parent / "logs" / "webhook_events.jsonl"
EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(title="Órbita Webhook Receiver", version="1.0.0")

SUPPORTED_EVENTS = {
    "item/created",
    "item/updated",
    "item/error",
    "transactions/created",
    "transactions/updated",
    "transactions/deleted",
    "all",
}


def _verify_signature(body: bytes, signature: str | None) -> bool:
    """Verify Pluggy HMAC-SHA256 signature if a secret is configured."""
    if not WEBHOOK_SECRET:
        return True  # No secret configured — skip verification
    if not signature:
        return False
    expected = hmac_module.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac_module.compare_digest(expected, signature.removeprefix("sha256="))


def _log_event(event: Dict[str, Any]) -> None:
    """Append event to JSONL log."""
    entry = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with EVENTS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info("Webhook event logged: %s (item=%s)", event.get("event"), event.get("itemId"))


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "orbita-webhook"}


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: Request,
    x_pluggy_signature: str | None = Header(default=None),
) -> JSONResponse:
    body = await request.body()

    if not _verify_signature(body, x_pluggy_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = payload.get("event", "unknown")
    if event_type not in SUPPORTED_EVENTS and event_type != "all":
        logger.warning("Received unknown event type: %s", event_type)

    _log_event(payload)

    # Write a "cache bust" marker so Streamlit knows to refresh
    bust_path = EVENTS_LOG.parent / "cache_bust.txt"
    bust_path.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")

    return JSONResponse({"received": True, "event": event_type})


@app.get("/events")
def list_events(limit: int = 20) -> Dict[str, Any]:
    """Return the last N webhook events (for debugging)."""
    if not EVENTS_LOG.exists():
        return {"events": [], "total": 0}
    lines = EVENTS_LOG.read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(l) for l in lines[-limit:]]
    return {"events": list(reversed(events)), "total": len(lines)}
