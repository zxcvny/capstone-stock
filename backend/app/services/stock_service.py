# 페이징, 필터링 등 비즈니스 로직

from sqlalchemy.ext.asyncio import AsyncSession
from ..crud import crud_stock, crud_price
from ..schemas import stock_schema
import math

async def get_paginated_stock_list(
    db: AsyncSession,
    page: int,
    size: int,
    market: str
) -> stock_schema.PaginatedStockResponse:
    """페이징 및 시장별 필터링 적용"""
    market_type = market if market != "all" else None

    # 총 아이템 개수 계산
    total_items = await crud_stock.count_stocks(db, market_type)
    total_pages = math.ceil(total_items / size)

    # 페이징 계산
    skip = (page - 1) * size

    # 페이징된 주식 목록
    db_stocks = await crud_stock.get_stocks_paginated(db, skip=skip, limit=size, market_type=market_type)

    # 각 주식의 최근 가격 정보 조합
    response_items = []
    for stock in db_stocks:
        latest_price_db = await crud_price.get_latest_price_for_stock(db, stock.id)

        stock_data = stock_schema.StockResponse.from_orm(stock)

        if latest_price_db:
            stock_data.latest_price = stock_schema.StockPriceResponse.from_orm(latest_price_db)

        response_items.append(stock_data)

    # 최종 페이징 응답 객체 반환
    return stock_schema.PaginatedStockResponse(
        total_items=total_items,
        total_pages=total_pages,
        page=page,
        size=size,
        items=response_items
    )