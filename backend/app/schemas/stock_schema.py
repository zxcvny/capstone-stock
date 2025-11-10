from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class StockPriceBase(BaseModel):
    date: date
    close_price: float

    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[float] = None
    change: Optional[float] = None
    percent_change: Optional[float] = None

class StockPriceCreate(StockPriceBase):
    stock_id: int

class StockPriceResponse(StockPriceBase):
    id: int

    class Config:
        from_attributes = True

class StockBase(BaseModel):
    symbol: str

    name_en: Optional[str] = None
    name_ko: Optional[str] = None

    market_type: str
    api_source: str

    exchange: Optional[str] = None
    currency: Optional[str] = None
    fifty_two_week_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None

class StockCreate(StockBase):
    pass

class StockResponse(StockBase):
    id: int
    latest_price: Optional[StockPriceResponse] = None

    class Config:
        from_attributes = True

class PaginatedStockResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    size: int
    items: List[StockResponse]