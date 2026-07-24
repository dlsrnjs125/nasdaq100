from __future__ import annotations
"""
src/processing/normalize.py
수집된 4개 데이터 소스를 통합하여 candidate_universe.csv를 생성한다.
"""
import csv
from datetime import datetime, timezone
from typing import Optional

from src.config import PROCESSED_UNIVERSE, FINANCIAL_SECTORS
from src.models import (
    Constituent, UniverseCompany, MarketData, SECRecord, CandidateRecord,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _determine_is_financial(sector: Optional[str]) -> str:
    if not sector:
        return "unknown"
    return "true" if sector.strip() in FINANCIAL_SECTORS else "false"


def build_candidate_universe(
    constituents: list[Constituent],
    universe: list[UniverseCompany],
    market_data: list[MarketData],
    sec_records: list[SECRecord],
) -> list[CandidateRecord]:
    """
    4개 데이터 소스를 병합하여 CandidateRecord 리스트를 생성하고
    PROCESSED_UNIVERSE (CSV)에 저장한다.
    """
    # 인덱스 구성
    constituent_tickers: set[str] = {c.ticker for c in constituents}
    market_map:  dict[str, MarketData] = {m.ticker: m for m in market_data}
    sec_map:     dict[str, SECRecord]  = {s.ticker: s for s in sec_records}
    universe_map: dict[str, UniverseCompany] = {u.ticker: u for u in universe}

    collected_at = _utcnow()
    records: list[CandidateRecord] = []

    # universe가 비어 있으면 구성 종목만이라도 처리
    all_tickers: set[str] = set(universe_map) | constituent_tickers

    for ticker in sorted(all_tickers):
        u  = universe_map.get(ticker)
        md = market_map.get(ticker)
        sr = sec_map.get(ticker)

        company_name = ""
        exchange     = "NASDAQ"
        sector: Optional[str] = None

        if u:
            company_name = u.company_name
            exchange     = u.exchange or "NASDAQ"
            sector       = u.sector
        elif ticker in constituent_tickers:
            c_match = next((c for c in constituents if c.ticker == ticker), None)
            if c_match:
                company_name = c_match.company_name
                sector       = c_match.sector

        # 시장 데이터
        market_cap:        Optional[float] = md.market_cap        if md else None
        last_price:        Optional[float] = md.last_price        if md else None
        shares_outstanding: Optional[float] = md.shares_outstanding if md else None
        market_cap_source: str              = md.market_cap_source if md else ""
        market_data_date:  str              = md.price_date        if md else ""

        # SEC 데이터 (SEC에 발행주식수가 있고 market_cap이 없으면 계산 시도)
        latest_sec_filing_type: Optional[str] = None
        latest_sec_filing_date: Optional[str] = None
        sec_data_date: str = ""
        if sr and sr.status == "ok":
            latest_sec_filing_type = sr.latest_filing_type
            latest_sec_filing_date = sr.latest_filing_date
            sec_data_date          = sr.sec_data_date
            if market_cap is None and last_price and sr.shares_outstanding:
                market_cap        = last_price * sr.shares_outstanding
                shares_outstanding = sr.shares_outstanding
                market_cap_source  = "calculated"

        is_financial = _determine_is_financial(sector)

        # 데이터 출처 기록
        sources = []
        if u:
            sources.append(u.source_type or "primary")
        if md:
            sources.append(md.source_type)
        if sr and sr.status == "ok":
            sources.append("sec_edgar")

        records.append(CandidateRecord(
            ticker=ticker,
            company_name=company_name,
            exchange=exchange,
            sector=sector,
            is_financial=is_financial,
            is_constituent=(ticker in constituent_tickers),
            market_cap=market_cap,
            market_cap_source=market_cap_source,
            last_price=last_price,
            shares_outstanding=shares_outstanding,
            latest_sec_filing_type=latest_sec_filing_type,
            latest_sec_filing_date=latest_sec_filing_date,
            market_data_date=market_data_date,
            sec_data_date=sec_data_date,
            eligibility_status="unknown",   # eligibility.py에서 갱신
            exclusion_reason="",
            data_source="|".join(sorted(set(sources))),
            collected_at=collected_at,
        ))

    # CSV 저장
    _save_csv(records)
    print(f"  [normalize] candidate_universe: {len(records)}개 기업 저장 완료")
    return records


_CSV_FIELDS = [
    "ticker", "company_name", "exchange", "sector",
    "is_financial", "is_constituent", "market_cap", "market_cap_source",
    "last_price", "shares_outstanding",
    "latest_sec_filing_type", "latest_sec_filing_date",
    "market_data_date", "sec_data_date",
    "eligibility_status", "exclusion_reason",
    "data_source", "collected_at",
]


def _save_csv(records: list[CandidateRecord]) -> None:
    PROCESSED_UNIVERSE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_UNIVERSE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for rec in records:
            writer.writerow({k: getattr(rec, k) for k in _CSV_FIELDS})


def load_candidate_universe() -> list[CandidateRecord]:
    """CSV에서 CandidateRecord를 로드한다."""
    if not PROCESSED_UNIVERSE.exists():
        return []
    records = []
    with open(PROCESSED_UNIVERSE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec = CandidateRecord(
                ticker=row["ticker"],
                company_name=row["company_name"],
                exchange=row["exchange"],
                sector=row["sector"] or None,
                is_financial=row["is_financial"],
                is_constituent=row["is_constituent"] == "True",
                market_cap=float(row["market_cap"]) if row["market_cap"] else None,
                market_cap_source=row["market_cap_source"],
                last_price=float(row["last_price"]) if row["last_price"] else None,
                shares_outstanding=float(row["shares_outstanding"]) if row["shares_outstanding"] else None,
                latest_sec_filing_type=row["latest_sec_filing_type"] or None,
                latest_sec_filing_date=row["latest_sec_filing_date"] or None,
                market_data_date=row["market_data_date"],
                sec_data_date=row["sec_data_date"],
                eligibility_status=row["eligibility_status"],
                exclusion_reason=row["exclusion_reason"],
                data_source=row["data_source"],
                collected_at=row["collected_at"],
            )
            records.append(rec)
    return records
