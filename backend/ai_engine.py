# backend/ai_engine.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def recommend_action(campaign_data):
    prompt = f"""
    Zde jsou data kampaně:
    {campaign_data}

    Navrhni, zda škálovat, pauznout nebo nechat být. Vysvětli proč.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

