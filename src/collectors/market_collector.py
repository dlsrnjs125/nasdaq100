from __future__ import annotations
"""
src/collectors/market_collector.py
시장 데이터 수집

우선순위:
1. Nasdaq screener에서 이미 수집한 market_cap / last_price 활용 (primary)
2. 데이터 없는 ticker에 대해 yfinance로 보완 (secondary_market_data)
"""
import json
import time
import warnings as _warnings
from datetime import datetime, timezone
from typing import Optional

from src.config import RAW_MARKET_DATA, HTTP_TIMEOUT
from src.models import MarketData, UniverseCompany


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_yfinance_batch(tickers: list[str]) -> dict[str, MarketData]:
    """yfinance를 사용해 시장 데이터를 일괄 수집한다."""
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        return {}

    result: dict[str, MarketData] = {}
    # yfinance batch download
    if not tickers:
        return result

    batch_size = 50
    today = _utcnow()[:10]
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i : i + batch_size]
        try:
            # suppress yfinance noise
            import logging
            logging.getLogger("yfinance").setLevel(logging.ERROR)

            info_map = {}
            for t in batch:
                try:
                    tk = yf.Ticker(t)
                    info = tk.fast_info
                    market_cap: Optional[float] = getattr(info, "market_cap", None)
                    price: Optional[float] = getattr(info, "last_price", None) or getattr(info, "previous_close", None)
                    shares: Optional[float] = getattr(info, "shares", None)

                    if market_cap or price:
                        mc_source = "provided" if market_cap else "calculated"
                        if not market_cap and price and shares:
                            market_cap = price * shares
                        result[t] = MarketData(
                            ticker=t,
                            last_price=price,
                            market_cap=market_cap,
                            shares_outstanding=shares,
                            price_date=today,
                            source_type="secondary_market_data",
                            market_cap_source=mc_source,
                        )
                except Exception:
                    pass
            time.sleep(0.5)
        except Exception:
            pass

    return result


def collect_market_data(
    universe: list[UniverseCompany],
    warnings: list[str],
) -> list[MarketData]:
    """
    1. Nasdaq screener 데이터에서 market_cap / last_price 추출 (primary)
    2. 누락 ticker는 yfinance로 보완 (secondary_market_data)
    """
    result: dict[str, MarketData] = {}
    today = _utcnow()[:10]

    # Step 1: Nasdaq screener에서 직접 추출
    for company in universe:
        mc = company.market_cap
        price = company.last_price
        if mc is not None or price is not None:
            result[company.ticker] = MarketData(
                ticker=company.ticker,
                last_price=price,
                market_cap=mc,
                shares_outstanding=None,
                price_date=company.as_of_date or today,
                source_type=company.source_type,
                market_cap_source="provided",
            )

    # Step 2: 누락 ticker를 yfinance로 보완
    missing = [c.ticker for c in universe if c.ticker not in result]
    if missing:
        print(f"  [market] yfinance로 누락 {len(missing)}개 보완 중...")
        warnings.append(
            f"{len(missing)}개 ticker의 시장 데이터를 yfinance(secondary)로 수집함"
        )
        secondary = _fetch_yfinance_batch(missing)
        result.update(secondary)
        print(f"  [market] yfinance 보완: {len(secondary)}개 성공")

    records = list(result.values())

    # 스냅숏 저장
    RAW_MARKET_DATA.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "collected_at": _utcnow(),
        "count": len(records),
        "data": [r.__dict__ for r in records],
    }
    RAW_MARKET_DATA.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print(f"  [market] 시장 데이터 수집 완료: {len(records)}개")
    return records


def load_market_data_from_raw() -> list[MarketData]:
    """저장된 스냅숏에서 시장 데이터를 로드한다."""
    if not RAW_MARKET_DATA.exists():
        return []
    snap = json.loads(RAW_MARKET_DATA.read_text())
    return [MarketData(**row) for row in snap.get("data", [])]
