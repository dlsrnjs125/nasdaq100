from __future__ import annotations
"""
src/validation/data_quality.py
데이터 품질 리포트 생성
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import OUT_QUALITY
from src.models import CandidateRecord, SECRecord, MarketData


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_report(
    records: list[CandidateRecord],
    sec_records: list[SECRecord],
    market_records: list[MarketData],
    warnings: list[str],
    official_sources: list[str],
    secondary_sources: list[str],
    failed_tickers: list[str],
) -> dict:
    """
    data_quality_report.json을 생성하고 반환한다.
    """
    total = len(records)
    constituent_count = sum(1 for r in records if r.is_constituent)
    non_constituent_count = total - constituent_count

    sec_ok = sum(1 for s in sec_records if s.status == "ok")
    market_ok = sum(1 for m in market_records if m.market_cap is not None)

    missing_sector = sum(1 for r in records if not r.sector)
    missing_market_cap = sum(1 for r in records if r.market_cap is None)
    unknown_eligibility = sum(1 for r in records if r.eligibility_status == "unknown")

    report = {
        "collected_at": _utcnow(),
        "official_sources_used": official_sources,
        "secondary_sources_used": secondary_sources,
        "total_universe_count": total,
        "constituent_count": constituent_count,
        "non_constituent_count": non_constituent_count,
        "sec_matched_count": sec_ok,
        "market_data_matched_count": market_ok,
        "missing_sector_count": missing_sector,
        "missing_market_cap_count": missing_market_cap,
        "unknown_eligibility_count": unknown_eligibility,
        "failed_tickers": failed_tickers,
        "source_warnings": warnings,
    }

    OUT_QUALITY.parent.mkdir(parents=True, exist_ok=True)
    OUT_QUALITY.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report
