from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from typing import Optional

from ..models import stock_model
from ..schemas import stock_schema

async def get_stock_by_symbol(db: AsyncSession, symbol: str) -> Optional[stock_model.Stock]:
    """심볼로 주식 정보 조회"""
    result = await db.execute(
        select(stock_model.Stock).filter(stock_model.Stock.symbol == symbol)
    )
    return result.scalar_one_or_none()

async def create_stock(db: AsyncSession, stock: stock_schema.StockCreate) -> stock_model.Stock:
    """새로운 주식 정보 생성"""
    db_stock = stock_model.Stock(**stock.model_dump())
    db.add(db_stock)
    await db.commit()
    await db.refresh(db_stock)
    return db_stock

async def get_stocks_by_source(db: AsyncSession, api_source: str) -> list[stock_model.Stock]:
    """API 출처별 모든 주식 정보 조회"""
    result = await db.execute(
        select(stock_model.Stock).filter(stock_model.Stock.api_source == api_source)
    )
    return result.scalars().all()

async def get_stocks_paginated(db: AsyncSession, skip: int, limit: int, market_type: Optional[str] = None):
    """주식 목록 페이징 조회"""
    query = select(stock_model.Stock)
    if market_type:
        query = query.filter(stock_model.Stock.market_type == market_type)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def count_stocks(db: AsyncSession, market_type: Optional[str] = None) -> int:
    """주식 정보의 총 개수 조회"""
    query = select(func.count()).select_from(stock_model.Stock)
    if market_type:
        query = query.filter(stock_model.Stock.market_type == market_type)

    result = await db.execute(query)
    return result.scalar_one()