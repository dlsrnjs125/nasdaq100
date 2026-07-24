from __future__ import annotations
"""
src/processing/eligibility.py
편입 / 편출 자격 판정 로직

편입 관찰 후보 조건:
  - Nasdaq 상장 기업
  - 현재 Nasdaq-100 비구성 종목
  - 금융업종이 아닌 기업 (is_financial != true, unknown 포함 제외)
  - market_cap이 존재
  - 거래 데이터가 존재 (last_price 또는 market_cap)

편출 관찰 후보 조건:
  - 현재 Nasdaq-100 구성 종목
  - market_cap이 존재
"""
from src.models import CandidateRecord


def assess_eligibility(records: list[CandidateRecord]) -> list[CandidateRecord]:
    """
    각 CandidateRecord의 eligibility_status와 exclusion_reason을 갱신한다.
    인플레이스 수정 후 반환한다.
    """
    for rec in records:
        reasons: list[str] = []

        # 시장 데이터 검사
        has_market_data = (rec.last_price is not None) or (rec.market_cap is not None)
        has_market_cap  = rec.market_cap is not None

        if not has_market_cap:
            reasons.append("market_cap_missing")

        if not has_market_data:
            reasons.append("market_data_missing")

        # 구성 종목 여부
        if rec.is_constituent:
            # 편출 후보: 구성 종목이면서 market_cap 있음
            if has_market_cap:
                rec.eligibility_status = "eligible"
                rec.exclusion_reason   = ""
            else:
                rec.eligibility_status = "unknown"
                rec.exclusion_reason   = "|".join(reasons)
            continue

        # 비구성 종목 편입 후보 판정
        if not has_market_cap or not has_market_data:
            rec.eligibility_status = "unknown"
            rec.exclusion_reason   = "|".join(reasons)
            continue

        if rec.is_financial == "true":
            rec.eligibility_status = "ineligible"
            rec.exclusion_reason   = "financial_sector"
            continue

        if rec.is_financial == "unknown":
            rec.eligibility_status = "unknown"
            rec.exclusion_reason   = "sector_unknown"
            continue

        # 모든 조건 충족
        rec.eligibility_status = "eligible"
        rec.exclusion_reason   = ""

    return records
