from __future__ import annotations
"""
tests/test_eligibility.py — 자격 판정 단위 테스트
"""
import pytest
from src.processing.eligibility import assess_eligibility


def test_inclusion_excludes_constituents(sample_records):
    """편입 후보에 현재 구성 종목이 포함되지 않는다."""
    inclusion = [
        r for r in sample_records
        if not r.is_constituent and r.eligibility_status == "eligible"
    ]
    assert all(not r.is_constituent for r in inclusion)


def test_inclusion_excludes_financial(sample_records):
    """편입 후보에 명확한 금융기업이 포함되지 않는다."""
    inclusion = [
        r for r in sample_records
        if not r.is_constituent and r.eligibility_status == "eligible"
    ]
    assert all(r.is_financial != "true" for r in inclusion)


def test_unknown_eligibility_excluded_from_inclusion(sample_records):
    """eligibility_status가 unknown인 기업은 편입 후보에 포함되지 않는다."""
    inclusion = [
        r for r in sample_records
        if not r.is_constituent and r.eligibility_status == "eligible"
    ]
    tickers = {r.ticker for r in inclusion}
    # NODATA와 NOSEC은 unknown → 포함되면 안 됨
    assert "NODATA" not in tickers
    assert "NOSEC" not in tickers


def test_exclusion_only_constituents(sample_records):
    """편출 후보는 현재 구성 종목으로만 구성된다."""
    exclusion_candidates = [r for r in sample_records if r.is_constituent and r.market_cap is not None]
    assert all(r.is_constituent for r in exclusion_candidates)


def test_no_market_cap_excluded_from_ranking(sample_records):
    """market_cap이 없는 기업은 순위 계산에서 제외된다."""
    from src.processing.rank_candidates import rank_inclusion, rank_exclusion
    inc = rank_inclusion(sample_records)
    exc = rank_exclusion(sample_records)
    inc_tickers = {r["ticker"] for r in inc}
    exc_tickers = {r["ticker"] for r in exc}
    assert "NODATA" not in inc_tickers
    assert "NODATA" not in exc_tickers
