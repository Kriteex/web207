# tests/test_ai_engine.py
import pytest

from backend import ai_engine

def test_build_prompt_contains_data():
    p = ai_engine._build_prompt({"x": 1})
    assert "Zde jsou data kampaně" in p
    assert "x" in p


@pytest.mark.asyncio
async def test_recommend_action_mocks_openai(monkeypatch):
    class FakeResp:
        class Choice:
            def __init__(self):
                self.message = {"content": "PAUSE: důvod"}
        choices = [Choice()]
    class FakeOpenAI:
        class ChatCompletion:
            @staticmethod
            def create(model, messages):
                assert model == "gpt-4"
                assert "Zde jsou data kampaně" in messages[0]["content"]
                return FakeResp()

    monkeypatch.setattr(ai_engine, "openai", FakeOpenAI)
    out = await ai_engine.recommend_action({"spend": 10})
    assert "PAUSE" in out
