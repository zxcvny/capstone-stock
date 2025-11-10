import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List, Tuple
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

def load_symbols_from_file(filepath: str = "nasdaq100_symbols.txt") -> List[Tuple[str, str]]:
    """
    파일에서 주식 심볼 리스트를 읽어옴.
    파일이 없으면 경고 후 빈 리스트 반환
    """
    symbols: List[Tuple[str, str]] = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    symbol, korean_name = line.split(",", 1)
                    symbols.append((symbol.strip(), korean_name.strip()))
                except ValueError:
                    print(f"⚠️ 형식 오류: '{line}' (콤마로 구분되지 않음)")
        return symbols
    except FileNotFoundError:
        print(f"⚠️ 경고: {filepath} 파일을 찾지 못했습니다. 빈 리스트를 반환했습니다.")
        return []
    
NASDAQ_100_SYMBOLS = load_symbols_from_file()