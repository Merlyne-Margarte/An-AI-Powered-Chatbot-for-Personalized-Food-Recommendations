from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Food(Base):
    __tablename__ = 'foods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    diet = Column(String, nullable=False)
    spice = Column(String, nullable=False)
    meal = Column(String, nullable=False)
    cuisine = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    allergens = Column(String, nullable=False)