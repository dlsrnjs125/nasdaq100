from __future__ import annotations
"""
src/collectors/sec_collector.py
SEC EDGAR 공식 API를 통한 CIK 매핑 및 기업 데이터 수집

공식 API:
- https://www.sec.gov/files/company_tickers.json
- https://data.sec.gov/submissions/CIK{cik}.json
- https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json

SEC 정책:
- User-Agent 헤더 필수 (환경변수 SEC_USER_AGENT)
- 요청 간 최소 0.15초 이상 대기
- 재시도 최대 3회
"""
import json
import time
import requests
from datetime import datetime, timezone
from typing import Optional

from src.config import (
    SEC_COMPANY_TICKERS_URL, SEC_SUBMISSIONS_TPL, SEC_COMPANY_FACTS_TPL,
    SEC_USER_AGENT, SEC_REQUEST_DELAY, SEC_MAX_RETRIES,
    HTTP_TIMEOUT, RAW_SEC_DATA,
)
from src.models import SECRecord


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sec_get(url: str) -> dict:
    """SEC API GET 요청 (재시도 포함)."""
    headers = {
        "User-Agent": SEC_USER_AGENT,
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }
    last_exc: Exception = Exception("unknown")
    for attempt in range(1, SEC_MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            last_exc = exc
            if attempt < SEC_MAX_RETRIES:
                time.sleep(SEC_REQUEST_DELAY * (2 ** attempt))  # exponential backoff
    raise last_exc


# ──────────────────────────────────────────────────────────────────────────────
# CIK 매핑 테이블
# ──────────────────────────────────────────────────────────────────────────────

def fetch_cik_map() -> dict[str, str]:
    """
    SEC company_tickers.json을 로드하여 {ticker: cik} 매핑을 반환한다.
    CIK는 10자리 zero-padded 문자열로 반환한다.
    """
    print(f"  [sec] CIK 매핑 테이블 수집 중: {SEC_COMPANY_TICKERS_URL}")
    time.sleep(SEC_REQUEST_DELAY)
    data = _sec_get(SEC_COMPANY_TICKERS_URL)
    # 응답 구조: {"0": {"cik_str": 789019, "ticker": "MSFT", "title": "..."}, ...}
    mapping: dict[str, str] = {}
    for entry in data.values():
        ticker = str(entry.get("ticker", "")).strip().upper()
        cik    = str(entry.get("cik_str", "")).strip().zfill(10)
        if ticker and cik:
            mapping[ticker] = cik
    print(f"  [sec] CIK 매핑 {len(mapping)}개 로드 완료")
    return mapping


# ──────────────────────────────────────────────────────────────────────────────
# 개별 기업 SEC 데이터 수집
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_submissions(cik: str) -> dict:
    url = SEC_SUBMISSIONS_TPL.format(cik=cik)
    return _sec_get(url)


def _parse_latest_filing(sub: dict) -> tuple[Optional[str], Optional[str]]:
    """최근 10-K/10-Q 제출일을 반환한다."""
    filings = sub.get("filings", {}).get("recent", {})
    forms   = filings.get("form", [])
    dates   = filings.get("filingDate", [])
    for form, date in zip(forms, dates):
        if form in ("10-K", "10-Q"):
            return form, date
    return None, None


def _fetch_shares_outstanding(cik: str) -> Optional[float]:
    """companyfacts API에서 최근 발행주식수를 가져온다."""
    url = SEC_COMPANY_FACTS_TPL.format(cik=cik)
    try:
        time.sleep(SEC_REQUEST_DELAY)
        data = _sec_get(url)
        # dei > EntityCommonStockSharesOutstanding
        facts = (
            data.get("facts", {})
            .get("dei", {})
            .get("EntityCommonStockSharesOutstanding", {})
        )
        units = facts.get("units", {})
        shares_list = units.get("shares", [])
        if shares_list:
            # 날짜 기준 내림차순 정렬 후 최신 값 반환
            sorted_shares = sorted(shares_list, key=lambda x: x.get("end", ""), reverse=True)
            return float(sorted_shares[0].get("val", 0)) or None
    except Exception:
        pass
    return None


def collect_sec_data(
    tickers: list[str],
    cik_map: dict[str, str],
    warnings: list[str],
) -> list[SECRecord]:
    """
    tickers 목록에 대해 SEC 데이터를 수집하고 RAW_SEC_DATA에 저장한다.
    실패한 ticker는 status='failed'로 기록한다.
    """
    records: list[SECRecord] = []
    total = len(tickers)

    for idx, ticker in enumerate(tickers, 1):
        if idx % 50 == 0 or idx == total:
            print(f"  [sec] 진행 중: {idx}/{total}")

        cik = cik_map.get(ticker)
        if not cik:
            records.append(SECRecord(ticker=ticker, status="not_found"))
            time.sleep(SEC_REQUEST_DELAY)
            continue

        try:
            time.sleep(SEC_REQUEST_DELAY)
            sub = _fetch_submissions(cik)
            entity_name = sub.get("name", "")
            filing_type, filing_date = _parse_latest_filing(sub)

            shares = _fetch_shares_outstanding(cik)

            records.append(SECRecord(
                ticker=ticker,
                cik=cik,
                entity_name=entity_name,
                latest_filing_type=filing_type,
                latest_filing_date=filing_date,
                shares_outstanding=shares,
                sec_data_date=_utcnow()[:10],
                source_url=SEC_SUBMISSIONS_TPL.format(cik=cik),
                status="ok",
            ))

        except Exception as exc:
            msg = f"SEC 수집 실패 [{ticker} / CIK={cik}]: {exc}"
            warnings.append(msg)
            records.append(SECRecord(
                ticker=ticker,
                cik=cik,
                status="failed",
            ))
            time.sleep(SEC_REQUEST_DELAY)

    # 스냅숏 저장
    RAW_SEC_DATA.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "collected_at": _utcnow(),
        "source_urls": [
            SEC_COMPANY_TICKERS_URL,
            SEC_SUBMISSIONS_TPL,
            SEC_COMPANY_FACTS_TPL,
        ],
        "count": len(records),
        "data": [r.__dict__ for r in records],
    }
    RAW_SEC_DATA.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print(f"  [sec] SEC 데이터 수집 완료: {len(records)}개 처리")
    return records


def load_sec_data_from_raw() -> list[SECRecord]:
    """저장된 스냅숏에서 SEC 레코드를 로드한다."""
    if not RAW_SEC_DATA.exists():
        return []
    snap = json.loads(RAW_SEC_DATA.read_text())
    return [SECRecord(**row) for row in snap.get("data", [])]
