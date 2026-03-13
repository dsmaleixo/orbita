"""Register (or update) Pluggy webhooks.

Usage:
    uv run python -m src.webhook.register --url https://<your-ngrok-id>.ngrok-free.app/webhook

This registers one webhook per required event type using the Pluggy SDK.
If a webhook for the same URL already exists it is skipped.
"""
from __future__ import annotations

import argparse
import sys

import httpx

from src.config import settings

EVENTS = [
    "item/created",
    "item/updated",
    "transactions/created",
    "transactions/updated",
    "transactions/deleted",
]

# Alternatively register a single "all" webhook instead of 5 individual ones.
# Set USE_ALL_EVENT=True to do that.
USE_ALL_EVENT = False


def _get_api_key() -> str:
    resp = httpx.post(
        f"{settings.PLUGGY_BASE_URL}/auth",
        json={"clientId": settings.PLUGGY_CLIENT_ID, "clientSecret": settings.PLUGGY_CLIENT_SECRET},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["apiKey"]


def _list_existing(headers: dict) -> list[dict]:
    resp = httpx.get(f"{settings.PLUGGY_BASE_URL}/webhooks", headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json().get("results", [])


def _create_webhook(url: str, event: str, headers: dict) -> dict:
    resp = httpx.post(
        f"{settings.PLUGGY_BASE_URL}/webhooks",
        json={"url": url, "event": event},
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _delete_webhook(webhook_id: str, headers: dict) -> None:
    resp = httpx.delete(
        f"{settings.PLUGGY_BASE_URL}/webhooks/{webhook_id}",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()


def register(url: str, replace: bool = False) -> None:
    print(f"Authenticating with Pluggy...")
    api_key = _get_api_key()
    headers = {"X-API-KEY": api_key}

    existing = _list_existing(headers)
    existing_by_event = {w["event"]: w for w in existing}

    events_to_register = ["all"] if USE_ALL_EVENT else EVENTS

    for event in events_to_register:
        if event in existing_by_event:
            existing_url = existing_by_event[event]["url"]
            if existing_url == url:
                print(f"  ✓ {event} — already registered at {url}")
                continue
            if replace:
                _delete_webhook(existing_by_event[event]["id"], headers)
                print(f"  ↺ {event} — replaced old URL ({existing_url})")
            else:
                print(f"  ⚠ {event} — already exists at different URL: {existing_url}")
                print(f"        Run with --replace to overwrite.")
                continue

        result = _create_webhook(url, event, headers)
        print(f"  ✅ {event} — registered (id={result['id']})")

    print("\nDone. Current webhooks:")
    for w in _list_existing(headers):
        print(f"  [{w['id']}] {w['event']} → {w['url']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Pluggy webhooks")
    parser.add_argument("--url", required=True, help="Public webhook URL, e.g. https://abc123.ngrok-free.app/webhook")
    parser.add_argument("--replace", action="store_true", help="Replace existing webhooks at different URLs")
    args = parser.parse_args()

    if "localhost" in args.url or "127.0.0.1" in args.url:
        print("❌ Error: Pluggy requires a publicly reachable URL, not localhost.")
        print("   Use ngrok: ngrok http 8000")
        sys.exit(1)

    register(args.url, replace=args.replace)


if __name__ == "__main__":
    main()
