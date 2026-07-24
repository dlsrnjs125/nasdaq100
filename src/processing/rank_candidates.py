from __future__ import annotations
"""
src/processing/rank_candidates.py
편입 / 편출 관찰 후보 Top N을 산정하고 CSV로 저장한다.

편입 관찰 후보: eligible + 비구성 종목 → market_cap 내림차순
편출 관찰 후보: eligible + 구성 종목 → market_cap 오름차순
"""
import csv
from datetime import datetime, timezone
from typing import Optional

from src.config import TOP_N, OUT_INCLUSION, OUT_EXCLUSION
from src.models import CandidateRecord

_RATIONALE_INCLUSION = (
    "Nasdaq 상장 비금융 비구성 기업 중 공개 데이터 기준 시가총액 상위권"
)
_LIMITATION = "공식 Nasdaq 내부 순위 및 최종 재량은 반영되지 않음"

_RATIONALE_EXCLUSION = (
    "현재 구성 종목 중 공개 데이터 기준 시가총액 하위권"
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def rank_inclusion(records: list[CandidateRecord]) -> list[dict]:
    """
    편입 관찰 후보 Top N을 산정하고 OUT_INCLUSION에 저장한다.
    """
    candidates = [
        r for r in records
        if (not r.is_constituent)
        and r.eligibility_status == "eligible"
        and r.market_cap is not None
    ]
    # market_cap 내림차순 정렬 (안정 정렬 → ticker 보조 정렬)
    candidates.sort(key=lambda r: (-r.market_cap, r.ticker))

    top = candidates[:TOP_N]
    rows = []
    for i, rec in enumerate(top, 1):
        rows.append({
            "watch_rank":      i,
            "ticker":          rec.ticker,
            "company_name":    rec.company_name,
            "market_cap":      rec.market_cap,
            "market_cap_source": rec.market_cap_source,
            "sector":          rec.sector or "",
            "eligibility_status": rec.eligibility_status,
            "market_data_date": rec.market_data_date,
            "rationale":       _RATIONALE_INCLUSION,
            "limitation":      _LIMITATION,
        })

    _write_csv(rows, OUT_INCLUSION, list(rows[0].keys()) if rows else [])
    print(f"  [rank] 편입 관찰 후보 {len(rows)}개 저장 → {OUT_INCLUSION.name}")
    return rows


def rank_exclusion(records: list[CandidateRecord]) -> list[dict]:
    """
    편출 관찰 후보 Top N을 산정하고 OUT_EXCLUSION에 저장한다.
    """
    candidates = [
        r for r in records
        if r.is_constituent
        and r.market_cap is not None
    ]
    # market_cap 오름차순 정렬 (안정 정렬)
    candidates.sort(key=lambda r: (r.market_cap, r.ticker))

    top = candidates[:TOP_N]
    rows = []
    for i, rec in enumerate(top, 1):
        rows.append({
            "watch_rank":      i,
            "ticker":          rec.ticker,
            "company_name":    rec.company_name,
            "market_cap":      rec.market_cap,
            "sector":          rec.sector or "",
            "market_data_date": rec.market_data_date,
            "rationale":       _RATIONALE_EXCLUSION,
            "limitation":      _LIMITATION,
        })

    _write_csv(rows, OUT_EXCLUSION, list(rows[0].keys()) if rows else [])
    print(f"  [rank] 편출 관찰 후보 {len(rows)}개 저장 → {OUT_EXCLUSION.name}")
    return rows


def _write_csv(rows: list[dict], path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
