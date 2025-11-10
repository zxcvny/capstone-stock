from sqlalchemy import Column,Integer, String, Float, Date, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.database import Base
import datetime

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)

    market_type = Column(String, default="overseas")

    api_source = Column(String, default="twelvedata")

    prices = relationship("StockPrice", back_populates="stock")

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    close_price = Column(Float, nullable=False)

    stock = relationship("Stock", back_populates="prices")