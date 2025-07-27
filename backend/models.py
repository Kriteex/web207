# backend/models.py
from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    objective = Column(String, nullable=True)
    spend = Column(Float, nullable=True)
    roas = Column(Float, nullable=True)

    adsets = relationship("Adset", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Campaign id={self.id!r} name={self.name!r} objective={self.objective!r}>"


class Adset(Base):
    __tablename__ = "adsets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)

    campaign = relationship("Campaign", back_populates="adsets")
    ads = relationship("Ad", back_populates="adset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Adset id={self.id!r} name={self.name!r} campaign_id={self.campaign_id!r}>"


class Ad(Base):
    __tablename__ = "ads"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    adset_id = Column(String, ForeignKey("adsets.id"), nullable=False)

    adset = relationship("Adset", back_populates="ads")

    def __repr__(self) -> str:
        return f"<Ad id={self.id!r} name={self.name!r} adset_id={self.adset_id!r}>"
