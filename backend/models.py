# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True)
    name = Column(String)
    objective = Column(String)
    spend = Column(Float)
    roas = Column(Float)

    adsets = relationship("Adset", back_populates="campaign")

class Adset(Base):
    __tablename__ = "adsets"
    id = Column(String, primary_key=True)
    name = Column(String)
    campaign_id = Column(String, ForeignKey("campaigns.id"))

    campaign = relationship("Campaign", back_populates="adsets")
    ads = relationship("Ad", back_populates="adset")

class Ad(Base):
    __tablename__ = "ads"
    id = Column(String, primary_key=True)
    name = Column(String)
    adset_id = Column(String, ForeignKey("adsets.id"))

    adset = relationship("Adset", back_populates="ads")