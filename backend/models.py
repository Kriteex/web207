# backend/models.py
from sqlalchemy import Column, Integer, String, Float
from backend.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True)
    name = Column(String)
    objective = Column(String)
    spend = Column(Float)
    roas = Column(Float)