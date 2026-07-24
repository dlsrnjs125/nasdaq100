from __future__ import annotations
"""
src/collectors/nasdaq_collector.py
Nasdaq-100 구성 종목 및 Nasdaq 상장 기업 유니버스 수집

우선순위:
1. Nasdaq 공식 API (api.nasdaq.com)
2. 실패 시 → data_quality_report에 기록, CONDITIONAL_PASS 표시
"""
import json
import time
import requests
from datetime import datetime, timezone
from typing import Optional

from src.config import (
    NASDAQ100_LIST_URL, NASDAQ_SCREENER_URL, NASDAQ_HEADERS,
    RAW_CONSTITUENTS, RAW_UNIVERSE, HTTP_TIMEOUT,
)
from src.models import Constituent, UniverseCompany


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get(url: str, params: Optional[dict] = None) -> dict:
    """공통 GET 요청. 실패 시 예외 발생."""
    resp = requests.get(
        url, headers=NASDAQ_HEADERS, params=params, timeout=HTTP_TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────────────────────────────────────────
# Nasdaq-100 구성 종목
# ──────────────────────────────────────────────────────────────────────────────

def _parse_constituents_from_list_api(data: dict) -> list[Constituent]:
    """api.nasdaq.com/api/quote/list-type/nasdaq100 응답 파싱"""
    rows = (
        data.get("data", {}).get("data", {}).get("rows")
        or data.get("data", {}).get("rows")
        or []
    )
    collected_at = _utcnow()
    result = []
    for row in rows:
        ticker = (row.get("symbol") or row.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        result.append(Constituent(
            ticker=ticker,
            company_name=(row.get("companyName") or row.get("companyname") or "").strip(),
            sector=row.get("sector") or None,
            source_url=NASDAQ100_LIST_URL,
            collected_at=collected_at,
        ))
    return result


def collect_constituents(warnings: list[str]) -> list[Constituent]:
    """
    Nasdaq-100 구성 종목을 수집하고 RAW_CONSTITUENTS에 저장한다.
    실패 시 빈 리스트를 반환하고 warnings에 이유를 기록한다.
    """
    constituents: list[Constituent] = []
    source_url = NASDAQ100_LIST_URL

    try:
        print(f"  [nasdaq] Nasdaq-100 구성 종목 수집 중: {source_url}")
        data = _get(source_url)
        constituents = _parse_constituents_from_list_api(data)
        if not constituents:
            raise ValueError("응답에서 구성 종목을 파싱할 수 없음")
        print(f"  [nasdaq] 구성 종목 {len(constituents)}개 수집 완료")

    except Exception as e:
        msg = f"Nasdaq-100 공식 API 실패 ({source_url}): {e}"
        warnings.append(msg)
        print(f"  [nasdaq] WARNING: {msg}")
        # 대체 소스 없이 빈 리스트 반환 (가짜 데이터 생성 금지)
        constituents = []

    # 스냅숏 저장
    RAW_CONSTITUENTS.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "collected_at": _utcnow(),
        "source_url": source_url,
        "count": len(constituents),
        "data": [c.__dict__ for c in constituents],
    }
    RAW_CONSTITUENTS.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return constituents


def load_constituents_from_raw() -> list[Constituent]:
    """저장된 스냅숏에서 구성 종목을 로드한다."""
    if not RAW_CONSTITUENTS.exists():
        return []
    snap = json.loads(RAW_CONSTITUENTS.read_text())
    return [Constituent(**row) for row in snap.get("data", [])]


# ──────────────────────────────────────────────────────────────────────────────
# Nasdaq 상장 기업 유니버스
# ──────────────────────────────────────────────────────────────────────────────

def _parse_market_cap(raw: str | None) -> Optional[float]:
    """'1234567890' 또는 '1.23B' 등을 float로 변환"""
    if not raw:
        return None
    raw = str(raw).strip().replace(",", "")
    if not raw or raw in ("", "N/A", "nan", "None"):
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_price(raw: str | None) -> Optional[float]:
    """'$189.30' → 189.30"""
    if not raw:
        return None
    cleaned = str(raw).replace("$", "").replace(",", "").strip()
    if not cleaned or cleaned in ("N/A",):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_screener_rows(rows: list[dict], as_of_date: str) -> list[UniverseCompany]:
    collected_at = _utcnow()
    result = []
    for row in rows:
        ticker = (row.get("symbol") or "").strip().upper()
        if not ticker:
            continue
        result.append(UniverseCompany(
            ticker=ticker,
            company_name=(row.get("name") or "").strip(),
            exchange=(row.get("exchange") or "NASDAQ").strip().upper(),
            sector=row.get("sector") or None,
            industry=row.get("industry") or None,
            market_cap=_parse_market_cap(row.get("marketCap")),
            last_price=_parse_price(row.get("lastsale")),
            source_url=NASDAQ_SCREENER_URL,
            as_of_date=as_of_date,
            source_type="primary",
        ))
    return result


def collect_universe(warnings: list[str]) -> list[UniverseCompany]:
    """
    Nasdaq 전체 상장 기업 유니버스를 수집하고 RAW_UNIVERSE에 저장한다.
    """
    universe: list[UniverseCompany] = []

    try:
        print(f"  [nasdaq] 유니버스 수집 중: {NASDAQ_SCREENER_URL}")
        data = _get(NASDAQ_SCREENER_URL)

        # 응답 구조: data.table.rows 또는 data.rows
        table = data.get("data", {}).get("table") or data.get("data", {})
        rows = table.get("rows") or []
        as_of_date = table.get("asOf") or _utcnow()[:10]

        universe = _parse_screener_rows(rows, as_of_date)
        if not universe:
            raise ValueError("스크리너 응답에서 기업 목록 파싱 실패")
        print(f"  [nasdaq] 유니버스 {len(universe)}개 수집 완료")

    except Exception as e:
        msg = f"Nasdaq screener API 실패 ({NASDAQ_SCREENER_URL}): {e}"
        warnings.append(msg)
        print(f"  [nasdaq] WARNING: {msg}")

    # 스냅숏 저장
    RAW_UNIVERSE.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "collected_at": _utcnow(),
        "source_url": NASDAQ_SCREENER_URL,
        "count": len(universe),
        "data": [u.__dict__ for u in universe],
    }
    RAW_UNIVERSE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return universe


def load_universe_from_raw() -> list[UniverseCompany]:
    """저장된 스냅숏에서 유니버스를 로드한다."""
    if not RAW_UNIVERSE.exists():
        return []
    snap = json.loads(RAW_UNIVERSE.read_text())
    result = []
    for row in snap.get("data", []):
        result.append(UniverseCompany(**row))
    return result
