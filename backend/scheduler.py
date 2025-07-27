# backend/scheduler.py
from __future__ import annotations

import asyncio
import time

import schedule

from backend.ads_api import fetch_campaigns


def _run_fetch_campaigns_sync() -> None:
    """
    The `schedule` library expects sync callables.
    Run the async function in a fresh event loop synchronously.
    """
    try:
        campaigns = asyncio.run(fetch_campaigns())
        print("Fetched campaigns:", campaigns)
    except Exception as exc:
        # Keep behavior visible but explicit
        print("Error fetching campaigns:", repr(exc))


# Every hour, as before
schedule.every(1).hours.do(_run_fetch_campaigns_sync)


def run_scheduler() -> None:
    """Blocking scheduler loop."""
    while True:
        schedule.run_pending()
        time.sleep(1)
