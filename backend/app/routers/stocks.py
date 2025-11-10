from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal
from ..db.database import get_db
from ..services import stock_service
from ..schemas import stock_schema

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=stock_schema.PaginatedStockResponse)
async def read_stocks(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 아이템 수"),
    market: Literal["all", "domestic", "overseas"] = Query("all", description="시장 구분"),
    db: AsyncSession = Depends(get_db)
):
    """
    주식 목록을 페이징하여 조회 (전체/국내/해외)
    """
    paginated_stocks = await stock_service.get_paginated_stock_list(
        db=db,
        page=page,
        size=size,
        market=market
    )
    return paginated_stocks