import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stocks
from .events.lifespan import lifespan
from .db.database import Base, engine

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # 교차-출처 요청을 보낼 수 있는 출처의 리스트
    allow_credentials=True, # 교차-출처 요청시 쿠키 지원 여부를 설정
    allow_methods=["*"], # 교차-출처 요청을 허용하는 HTTP 메소드의 리스트
    allow_headers=["*"], # 교차-출처를 지원하는 HTTP 요청 헤더의 리스트
)

app.include_router(stocks.router)

@app.get("/")
def read_root():
    return {"message": "Stock API"}