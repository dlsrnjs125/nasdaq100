from __future__ import annotations
"""
src/config.py — 경로·엔드포인트·상수 설정
"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# ── 디렉터리 경로 ────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent.parent
DATA_RAW        = BASE_DIR / "data" / "raw"
DATA_PROCESSED  = BASE_DIR / "data" / "processed"
OUTPUTS_DIR     = BASE_DIR / "outputs"

# raw 스냅숏 파일 경로
RAW_CONSTITUENTS    = DATA_RAW / "nasdaq100_constituents.json"
RAW_UNIVERSE        = DATA_RAW / "nasdaq_universe.json"
RAW_MARKET_DATA     = DATA_RAW / "market_data.json"
RAW_SEC_DATA        = DATA_RAW / "sec_company_data.json"

# processed / outputs
PROCESSED_UNIVERSE  = DATA_PROCESSED / "candidate_universe.csv"
OUT_INCLUSION       = OUTPUTS_DIR / "inclusion_watch_top10.csv"
OUT_EXCLUSION       = OUTPUTS_DIR / "exclusion_watch_top10.csv"
OUT_QUALITY         = OUTPUTS_DIR / "data_quality_report.json"
OUT_RESULT          = OUTPUTS_DIR / "poc_result.json"

# ── Nasdaq API 엔드포인트 ─────────────────────────────────────────────────────
NASDAQ100_LIST_URL  = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
NASDAQ_SCREENER_URL = (
    "https://api.nasdaq.com/api/screener/stocks"
    "?limit=5000&exchange=nasdaq&download=true"
)

# Nasdaq API 공통 헤더
NASDAQ_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/",
    "Origin": "https://www.nasdaq.com",
}

# ── SEC EDGAR 엔드포인트 ──────────────────────────────────────────────────────
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_TPL     = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_COMPANY_FACTS_TPL   = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

SEC_USER_AGENT: str = os.getenv(
    "SEC_USER_AGENT", "Nasdaq100PoC example@example.com"
)

# ── HTTP / Rate-limiting ──────────────────────────────────────────────────────
HTTP_TIMEOUT        = 300         # seconds (Nasdaq API can be slow)
SEC_REQUEST_DELAY   = 0.15        # seconds between SEC calls
SEC_MAX_RETRIES     = 3
SEC_MAX_TICKERS     = 500         # SEC 수집 대상 최대 ticker 수 (상위 N개)

# ── 후보 산정 파라미터 ────────────────────────────────────────────────────────
TOP_N               = 10
UNIVERSE_MAX_SIZE   = 500         # screener 결과 상위 N개만 처리 (market_cap 기준)
MIN_UNIVERSE_SIZE   = 150

# 금융업 섹터 (편입 후보 제외)
FINANCIAL_SECTORS: frozenset[str] = frozenset({
    "Financials",
    "Financial Services",
    "Finance",
    "Banking",
    "Insurance",
})

# PoC PASS 기준
PASS_MIN_CONSTITUENTS           = 90
PASS_MIN_UNIVERSE               = 150
PASS_MIN_MARKET_CAP_RATE        = 0.90
PASS_MIN_SEC_MATCH_RATE         = 0.90
PASS_MIN_INCLUSION_CANDIDATES   = 5
PASS_MIN_EXCLUSION_CANDIDATES   = 5
