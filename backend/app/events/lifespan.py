# 앱 시작/종료 이벤트 (데이터 적재)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import Base, engine, AsyncSessionLocal
from ..services import data_fetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """DB 테이블 생성"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"⛔데이터베이스 테이블을 생성하는 중에 오류가 발생했습니다: {e}")

async def run_startup_tasks():
    """앱 시작 시 실행될 비동기 작업들"""
    logger.info("✅시작 작업 실행...")

    try:
        # 1. DB에 NASDAQ100 리스트 초기화
        await data_fetcher.initialize_stock_list()

        # 2. Twlevedata API에서 종가 업데이트
        await data_fetcher.update_stock_prices_from_twelvedata()

        # 3. 한투 API 데이터 로더 추가 예정

    except Exception as e:
        logger.error(f"⛔시작 작업 중 오류 발생: {e}")
    
    logger.info("✅시작 작업이 완료되었습니다.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅애플리케이션 시작...")

    await init_db()
    
    # asyncio.create_task: 앱 시작 속도 개선
    await run_startup_tasks()

    yield

    logger.info("✅애플리케이션 종료...")
