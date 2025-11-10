from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional

from ..models import stock_model
from ..schemas import stock_schema

async def get_latest_price_data(db: AsyncSession, stock_id: int) -> Optional[date]:
    """특정 주식의 가장 최근 종가 날짜 조회"""
    result = await db.execute(
        select(stock_model.StockPrice.date)
        .filter(stock_model.StockPrice.stock_id == stock_id)
        .order_by(stock_model.StockPrice.date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def create_stock_price(db: AsyncSession, price:stock_schema.StockPriceCreate) -> stock_model.StockPrice:
    """새로운 주식 가격 정보 생성"""
    db_price = stock_model.StockPrice(**price.model_dump())
    db.add(db_price)
    await db.commit()
    await db.refresh(db_price)
    return db_price

async def get_latest_price_for_stock(db: AsyncSession, stock_id: int) -> Optional[stock_model.StockPrice]:
    """특정 주식의 가장 최근 가격 정보 전체 조회"""
    result = await db.execute(
        select(stock_model.StockPrice)
        .filter(stock_model.StockPrice.stock_id == stock_id)
        .order_by(stock_model.StockPrice.date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()