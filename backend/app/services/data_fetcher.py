# 외부 API 호출 및 데이터 저장 로직

import httpx
import asyncio
from datetime import date
from typing import Optional, Dict, Any

from ..db.database import AsyncSessionLocal
from ..core.config import settings, NASDAQ_100_SYMBOLS
from ..crud import crud_stock, crud_price
from ..schemas import stock_schema
from ..models import stock_model

import logging # 코드 실행 상태를 기록하기 위한 표준 모듈

logging.basicConfig(level=logging.INFO) # INFO 이상의 로그 출력
logger = logging.getLogger(__name__) # 현재 모듈 이름을 가진 로거 객체 생성

def _safe_float_cast(value: Optional[str]) -> Optional[float]:
    """문자열을 float로 변환"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

async def initialize_stock_list():
    """
    nasdaq100_symbols.txt → Stock 테이블에 초기화
    """
    logger.info(f"✅ {len(NASDAQ_100_SYMBOLS)}개 심볼의 주식 목록을 초기화합니다...")
    async with AsyncSessionLocal() as db:
        for symbol, name_ko in NASDAQ_100_SYMBOLS:
            db_stock = await crud_stock.get_stock_by_symbol(db, symbol)
            if not db_stock:
                stock_in = stock_schema.StockCreate(
                    symbol=symbol,
                    name_en=symbol,
                    name_ko=name_ko,
                    market_type="overseas",
                    api_source="twelvedata"
                )
                await crud_stock.create_stock(db, stock_in)

    logger.info("✅ NASDAQ100 목록 초기화가 완료되었습니다.")

async def fetch_twelvedata_quote_data(symbol: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Twelvedata API: 해외 주식 상세 정보(Quote) 가져오기"""
    url = f"{settings.TWELVEDATA_BASE_URL}/quote?symbol={symbol}&apikey={api_key}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            extracted_data = {
                "name_en": data.get("name"),
                "exchange": data.get("exchange"),
                "currency": data.get("currency"),
                "fifty_two_week_low": _safe_float_cast(data.get("fifty_two_week", {}).get("low")),
                "fifty_two_week_high": _safe_float_cast(data.get("fifty_two_week", {}).get("high")),

                "open_price": _safe_float_cast(data.get("open")),
                "high_price": _safe_float_cast(data.get("high")),
                "low_price": _safe_float_cast(data.get("low")),
                "volume": _safe_float_cast(data.get("volume")),
                "change": _safe_float_cast(data.get("change")),
                "percent_change": _safe_float_cast(data.get("percent_change")),
            }

            # 1. 종가 (close 또는 previous_close)
            if data.get("is_market_open") == True and data.get("close"):
                 extracted_data["close_price"] = _safe_float_cast(data.get("close"))
            elif data.get("previous_close"):
                extracted_data["close_price"] = _safe_float_cast(data.get("previous_close"))
            elif data.get("close"): # Fallback
                extracted_data["close_price"] = _safe_float_cast(data.get("close"))
            else:
                logger.warning(f"⚠️ API 응답에서 {symbol}에 대한 종가를 찾을 수 없습니다: {data}")
                return None
            
            return extracted_data

    except httpx.HTTPStatusError as e:
        logger.error(f"⛔ {symbol}을(를) 가져오는 중에 HTTP 오류가 발생했습니다: {e}")
    except Exception as e:
        logger.error(f"⛔ {symbol}을(를) 가져오는 중에 오류가 발생했습니다: {e}")
    return None

async def update_stock_prices_from_twelvedata():
    """
    twlevedata API 사용: 해외 주식 종가 업데이트
    """
    logger.info("✅ Twelvedata에서 종가 업데이트를 시작합니다...")
    api_key = settings.TWELVEDATA_API_KEY
    if not api_key:
        logger.error("⛔ Twlevedata API 키가 설정되지 않았습니다. 업데이트를 건너뜁니다.")
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
                logger.info(f"✅ {stock.symbol} 건너뛰기: 오늘의 종가가 이미 존재합니다.")

    # 세션이 닫힌 후, API 호출 작업 리스트 생성
    tasks = []
    for stock in stocks_to_fetch:
        # DB에서 가장 최근 날짜 확인
        tasks.append(fetch_and_save_price(stock.symbol, api_key, today))

    await asyncio.gather(*tasks)
    logger.info("✅ Twelvedata의 종가 업데이트가 완료되었습니다.")

async def fetch_and_save_price(symbol: str, api_key: str, fetch_date: date):
    """단일 종목 상세 정보를 비동기로 가져와 Stock은 업데이트, StockPrice는 생성"""

    # 1. API에서 상세 데이터 호출
    quote_data = await fetch_twelvedata_quote_data(symbol, api_key)

    if quote_data is None or quote_data.get("close_price") is None:
        logger.warning(f"⚠️ {symbol}의 가격 정보를 가져오지 못했습니다.")
        return

    # 2. DB 세션을 열고, Stock과 StockPrice 동시 처리
    async with AsyncSessionLocal() as db:
        try:
            # 2-1. Stock 모델 업데이트 (기본 정보)
            # 이 세션에서 stock 객체를 다시 가져와야 함 (Managed 상태)
            db_stock = await crud_stock.get_stock_by_symbol(db, symbol)
            if not db_stock:
                logger.error(f"⛔ {symbol}을(를) DB에서 찾을 수 없어 업데이트/저장에 실패했습니다.")
                return

            db_stock.name_en = quote_data.get("name_en")
            db_stock.exchange = quote_data.get("exchange")
            db_stock.currency = quote_data.get("currency")
            db_stock.fifty_two_week_low = quote_data.get("fifty_two_week_low")
            db_stock.fifty_two_week_high = quote_data.get("fifty_two_week_high")
            
            # 2-2. StockPrice 모델 생성 (일별 시세)
            price_in = stock_schema.StockPriceCreate(
                stock_id=db_stock.id,
                date=fetch_date,
                close_price=quote_data["close_price"],
                open_price=quote_data.get("open_price"),
                high_price=quote_data.get("high_price"),
                low_price=quote_data.get("low_price"),
                volume=quote_data.get("volume"),
                change=quote_data.get("change"),
                percent_change=quote_data.get("percent_change")
            )
            
            db.add(db_stock)
            await crud_price.create_stock_price(db, price_in)
            
            logger.info(f"✅ {symbol}의 정보 및 가격이 성공적으로 저장/업데이트되었습니다.")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"⛔ {symbol}의 정보를 저장하는 중 오류가 발생했습니다: {e}")

# 한투 API 추가 예정