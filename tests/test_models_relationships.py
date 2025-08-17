# tests/test_models_relationships.py
import importlib
import asyncio

from sqlalchemy import select

def test_models_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path/'m.db'}")

    from backend import database
    importlib.reload(database)
    from backend import models

    async def _run():
        await database.init_db()
        async with database.SessionLocal() as s:
            c = models.Campaign(id="c1", name="Camp", objective="OUTCOME_SALES", spend=10.0, roas=2.0)
            s.add(c)
            a = models.Adset(id="s1", name="Set", campaign=c)
            s.add(a)
            ad = models.Ad(id="ad1", name="Ad", adset=a)
            s.add(ad)
            await s.commit()

            q = await s.execute(select(models.Campaign).where(models.Campaign.id=="c1"))
            got = q.scalar_one()
            assert got.adsets[0].ads[0].id == "ad1"

    asyncio.run(_run())
