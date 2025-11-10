# 외부 API 호출 및 데이터 저장 로직

import httpx
import asyncio
from datetime import date
from typing import Optional

from ..db.database import AsyncSessionLocal
from ..core.config import settings, NASDAQ_100_SYMBOLS
from ..crud import crud_stock, crud_price
from ..schemas import stock_schema
from ..models import stock_model

import logging # 코드 실행 상태를 기록하기 위한 표준 모듈

logging.basicConfig(level=logging.INFO) # INFO 이상의 로그 출력
logger = logging.getLogger(__name__) # 현재 모듈 이름을 가진 로거 객체 생성

async def initialize_stock_list():
    """
    nasdaq100_symbols.txt → Stock 테이블에 초기화
    """
    logger.info(f"Initializing stock list with {len(NASDAQ_100_SYMBOLS)} symbols...")
    async with AsyncSessionLocal() as db:
        for symbol in NASDAQ_100_SYMBOLS:
            db_stock = await crud_stock.get_stock_by_symbol(db, symbol)
            if not db_stock:
                stock_in = stock_schema.StockCreate(
                    symbol=symbol,
                    name=symbol, # 이름 수정 필요
                    market_type="overseas",
                    api_source="twelvedata"
                )
                await crud_stock.create_stock(db, stock_in)

    logger.info("Stock list initialization complete.")

async def fetch_twelvedata_closing_price(symbol: str, api_key: str) -> Optional[float]:
    """Twelvedata API: 해외 주식 종가 가져오기 (Quote)"""
    url = f"{settings.TWELVEDATA_BASE_URL}/quote?symbol={symbol}&apikey={api_key}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # 전일 종가 가져오기 (API 확인, 수정필요, 변화율 필요)
            if "close" in data:
                return float(data["close"])
            elif "previous_close" in data:
                # 당일 장이 마감 안됐으면 전일 종가 사용
                return float(data["previous_close"])
            else:
                logger.warning(f"No closing price found for {symbol} in API response: {data}")
                return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching {symbol}: {e}")
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
    return None

async def update_stock_prices_from_twelvedata():
    """
    twlevedata API 사용: 해외 주식 종가 업데이트
    """
    logger.info("Strating stock price update from Twelvedata...")
    api_key = settings.TWELVEDATA_API_KEY
    if not api_key:
        logger.error("Twlevedata API KEY is not set. Skipping update.")
        return
    
    today = date.today()
    stocks_to_fetch = []
    # 세션 잠깐 사용, 필요한 데이터만 가져옴
    async with AsyncSessionLocal() as db:
        all_stocks = await crud_stock.get_stocks_by_source(db, api_source="twelvedata")
        for stock in all_stocks:
            latest_data_in_db = await crud_price.get_latest_price_data(db, stock.id)
            if latest_data_in_db != today:
                stocks_to_fetch.append(stock)
            else:
                logger.info(f"Skipping {stock.symbol}: Today's price already exists.")

    # 세션이 닫힌 후, API 호출 작업 리스트 생성
    tasks = []
    for stock in stocks_to_fetch:
        # DB에서 가장 최근 날짜 확인
        tasks.append(fetch_and_save_price(stock, api_key, today))

    await asyncio.gather(*tasks)
    logger.info("Stock price update from Twelvedata complete.")

async def fetch_and_save_price(stock: stock_model.Stock, api_key: str, fetch_date: date):
    """단일 종목 가격을 비동기로 가져와 저장"""
    price = await fetch_twelvedata_closing_price(stock.symbol, api_key)

    if price is not None:
        async with AsyncSessionLocal() as db:
            try:
                price_in = stock_schema.StockPriceCreate(
                    stock_id=stock.id,
                    date=fetch_date,
                    close_price=price
                )
                await crud_price.create_stock_price(db, price_in)
                logger.info(f"Successfully saved price for {stock.symbol}: {price}")
            except Exception as e:
                logger.info(f"Error saving price for {stock.symbol}: {e}")
    else:
        logger.warning(f"Failed to fetch price for {stock.symbol}")

# 한투 API 추가 예정