from __future__ import annotations
"""
src/models.py — 공통 데이터 모델
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Constituent:
    """Nasdaq-100 현재 구성 종목"""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    source_url: str = ""
    collected_at: str = ""


@dataclass
class UniverseCompany:
    """Nasdaq 상장 후보 기업 (구성 종목 포함)"""
    ticker: str
    company_name: str
    exchange: str = "NASDAQ"
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    last_price: Optional[float] = None
    source_url: str = ""
    as_of_date: str = ""
    source_type: str = "primary"            # primary | secondary_market_data


@dataclass
class MarketData:
    """시장 데이터 레코드"""
    ticker: str
    last_price: Optional[float] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    price_date: str = ""
    source_type: str = "primary"            # primary | secondary_market_data
    market_cap_source: str = "provided"     # provided | calculated


@dataclass
class SECRecord:
    """SEC EDGAR 수집 결과"""
    ticker: str
    cik: Optional[str] = None
    entity_name: Optional[str] = None
    latest_filing_type: Optional[str] = None
    latest_filing_date: Optional[str] = None
    shares_outstanding: Optional[float] = None
    sec_data_date: str = ""
    source_url: str = ""
    status: str = "ok"                      # ok | failed | not_found


@dataclass
class CandidateRecord:
    """정규화된 후보 기업 레코드"""
    ticker: str
    company_name: str
    exchange: str = "NASDAQ"
    sector: Optional[str] = None
    is_financial: str = "false"             # true | false | unknown
    is_constituent: bool = False
    market_cap: Optional[float] = None
    market_cap_source: str = ""             # provided | calculated | ""
    last_price: Optional[float] = None
    shares_outstanding: Optional[float] = None
    latest_sec_filing_type: Optional[str] = None
    latest_sec_filing_date: Optional[str] = None
    market_data_date: str = ""
    sec_data_date: str = ""
    eligibility_status: str = "unknown"    # eligible | ineligible | unknown
    exclusion_reason: str = ""
    data_source: str = ""
    collected_at: str = ""
