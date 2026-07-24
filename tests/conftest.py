from __future__ import annotations
"""
tests/conftest.py — 단위 테스트용 공통 fixture
외부 네트워크 호출 없이 저장된 raw fixture를 사용한다.
"""
import json
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _make_candidate(
    ticker: str,
    is_constituent: bool,
    market_cap: float | None,
    sector: str | None,
    is_financial: str = "false",
    eligibility_status: str = "unknown",
):
    from src.models import CandidateRecord
    return CandidateRecord(
        ticker=ticker,
        company_name=f"Company {ticker}",
        exchange="NASDAQ",
        sector=sector,
        is_financial=is_financial,
        is_constituent=is_constituent,
        market_cap=market_cap,
        market_cap_source="provided" if market_cap else "",
        last_price=market_cap / 1e9 if market_cap else None,
        shares_outstanding=None,
        latest_sec_filing_type="10-K",
        latest_sec_filing_date="2024-01-01",
        market_data_date="2024-01-01",
        sec_data_date="2024-01-01",
        eligibility_status=eligibility_status,
        exclusion_reason="",
        data_source="primary",
        collected_at="2024-01-01T00:00:00Z",
    )


@pytest.fixture
def sample_records():
    """편입/편출 테스트에 사용되는 샘플 레코드"""
    from src.processing.eligibility import assess_eligibility

    records = [
        # 구성 종목 (편출 후보)
        _make_candidate("AAPL",  is_constituent=True,  market_cap=2_800_000_000_000, sector="Technology"),
        _make_candidate("MSFT",  is_constituent=True,  market_cap=2_500_000_000_000, sector="Technology"),
        _make_candidate("NVDA",  is_constituent=True,  market_cap=2_000_000_000_000, sector="Technology"),
        _make_candidate("GOOG",  is_constituent=True,  market_cap=1_900_000_000_000, sector="Communication Services"),
        _make_candidate("AMZN",  is_constituent=True,  market_cap=1_800_000_000_000, sector="Consumer Discretionary"),
        _make_candidate("META",  is_constituent=True,  market_cap=1_200_000_000_000, sector="Communication Services"),
        _make_candidate("TSLA",  is_constituent=True,  market_cap=800_000_000_000,   sector="Consumer Discretionary"),
        _make_candidate("AVGO",  is_constituent=True,  market_cap=750_000_000_000,   sector="Technology"),
        _make_candidate("COST",  is_constituent=True,  market_cap=400_000_000_000,   sector="Consumer Staples"),
        _make_candidate("NFLX",  is_constituent=True,  market_cap=280_000_000_000,   sector="Communication Services"),
        # 하위 구성 종목 (편출 후보 Top)
        _make_candidate("SMLL1", is_constituent=True,  market_cap=10_000_000_000,    sector="Technology"),
        _make_candidate("SMLL2", is_constituent=True,  market_cap=8_000_000_000,     sector="Technology"),

        # 비구성 종목 (편입 후보)
        _make_candidate("NEWCO1", is_constituent=False, market_cap=500_000_000_000,  sector="Technology"),
        _make_candidate("NEWCO2", is_constituent=False, market_cap=400_000_000_000,  sector="Healthcare"),
        _make_candidate("NEWCO3", is_constituent=False, market_cap=300_000_000_000,  sector="Industrials"),

        # 금융기업 (편입 제외)
        _make_candidate("FINCO",  is_constituent=False, market_cap=600_000_000_000,  sector="Financials",   is_financial="true"),

        # market_cap 없음 (unknown)
        _make_candidate("NODATA", is_constituent=False, market_cap=None,             sector="Technology"),

        # sector 없음 (unknown → 편입 제외)
        _make_candidate("NOSEC",  is_constituent=False, market_cap=200_000_000_000,  sector=None,           is_financial="unknown"),
    ]
    return assess_eligibility(records)
