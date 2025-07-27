# backend/ai_engine.py
from __future__ import annotations

import os
from typing import Any, Dict

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# NOTE:
# - Keep the same OpenAI usage to avoid changing behavior.
# - The function remains async but executes the blocking call in a thread.


def _build_prompt(campaign_data: Any) -> str:
    """Create the Czech prompt while keeping the original phrasing."""
    return f"""
Zde jsou data kampaně:
{campaign_data}

Navrhni, zda škálovat, pauznout nebo nechat být. Vysvětli proč.
""".strip()


async def recommend_action(campaign_data: Any) -> str:
    """
    Ask GPT-4 for a recommendation. Preserves the original model+API,
    but runs the blocking call off the event loop to avoid starving it.
    """
    import asyncio

    prompt = _build_prompt(campaign_data)

    def _call_sync() -> str:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message["content"]  # type: ignore[index]

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _call_sync)
