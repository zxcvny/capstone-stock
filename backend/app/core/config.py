import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    TWELVEDATA_API_KEY: str = os.getenv("TWELVE_DATA_API_KEY")
    TWELVEDATA_BASE_URL: str = os.getenv("TWELVEDATA_BASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

def load_symbols_from_file(filepath: str = "nasdaq100_symbols.txt") -> list[str]:
    """
    파일에서 주식 심볼 리스트를 읽어옴.
    파일이 없으면 경고 후 빈 리스트 반환
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            symbols = [line.strip() for line in f if line.strip()]
            return symbols
    except FileNotFoundError:
        print(f"⚠️ 경고: {filepath} 파일을 찾지 못했습니다. 빈 리스트를 반환했습니다.")
        return []
    
NASDAQ_100_SYMBOLS = load_symbols_from_file()