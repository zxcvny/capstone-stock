from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class StockPriceBase(BaseModel):
    date: date
    close_price: float

class StockPriceCreate(StockPriceBase):
    stock_id: int

class StockPriceResponse(StockPriceBase):
    id: int

    class Config:
        from_attributes = True

class StockBase(BaseModel):
    symbol: str
    name: Optional[str] = None
    market_type: str
    api_source: str

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