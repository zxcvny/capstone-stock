from sqlalchemy import Column,Integer, String, Float, Date, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.database import Base
import datetime

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)

    name_en = Column(String, nullable=True)
    name_ko = Column(String, nullable=True)

    market_type = Column(String, default="overseas")
    api_source = Column(String, default="twelvedata")

    exchange = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    fifty_two_week_low = Column(Float, nullable=True)
    fifty_two_week_high = Column(Float, nullable=True)

    prices = relationship("StockPrice", back_populates="stock")

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    close_price = Column(Float, nullable=False)

    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)

    percent_change = Column(Float, nullable=False)

    stock = relationship("Stock", back_populates="prices")