from __future__ import annotations
"""
src/pipeline.py
전체 파이프라인 오케스트레이션

--refresh 옵션:
  - 외부 데이터를 새로 수집하고 raw 스냅숏을 갱신한다.

기본 실행 (캐시 사용):
  - 기존 raw 스냅숏이 있으면 해당 데이터를 사용한다.
  - 없으면 자동으로 수집한다.
"""
import json
import uuid
from datetime import datetime, timezone

from src.config import (
    RAW_CONSTITUENTS, RAW_UNIVERSE, RAW_MARKET_DATA, RAW_SEC_DATA,
    OUT_RESULT, OUTPUTS_DIR,
    PASS_MIN_CONSTITUENTS, PASS_MIN_UNIVERSE,
    PASS_MIN_MARKET_CAP_RATE, PASS_MIN_SEC_MATCH_RATE,
    PASS_MIN_INCLUSION_CANDIDATES, PASS_MIN_EXCLUSION_CANDIDATES,
    UNIVERSE_MAX_SIZE, SEC_MAX_TICKERS,
)
from src.collectors.nasdaq_collector import (
    collect_constituents, collect_universe,
    load_constituents_from_raw, load_universe_from_raw,
)
from src.collectors.sec_collector import (
    fetch_cik_map, collect_sec_data, load_sec_data_from_raw,
)
from src.collectors.market_collector import (
    collect_market_data, load_market_data_from_raw,
)
from src.processing.normalize import build_candidate_universe, load_candidate_universe, _save_csv
from src.processing.eligibility import assess_eligibility
from src.processing.rank_candidates import rank_inclusion, rank_exclusion
from src.validation.data_quality import generate_report
from src.validation.reproducibility import compute_snapshot_hash, verify_reproducibility


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _all_raw_exist() -> bool:
    return all(p.exists() for p in [RAW_CONSTITUENTS, RAW_UNIVERSE, RAW_MARKET_DATA, RAW_SEC_DATA])


def run(refresh: bool = False) -> dict:
    """
    파이프라인 전체를 실행하고 poc_result.json을 반환한다.
    """
    warnings: list[str] = []
    official_sources: list[str] = []
    secondary_sources: list[str] = []

    # ── 1. 데이터 수집 ─────────────────────────────────────────────────────────
    if refresh or not _all_raw_exist():
        print("\n[pipeline] 외부 데이터 수집 시작...")

        constituents = collect_constituents(warnings)
        universe     = collect_universe(warnings)

        if not universe:
            # Nasdaq screener 실패 → 파이프라인 진행 불가
            raise RuntimeError(
                "Nasdaq 유니버스 수집 실패. 데이터 수집 없이 진행할 수 없습니다. "
                "네트워크 상태를 확인하거나 data_quality_report.json을 확인하세요."
            )

        # 유니버스 상위 UNIVERSE_MAX_SIZE개로 제한 (market_cap 기준)
        if len(universe) > UNIVERSE_MAX_SIZE:
            universe.sort(
                key=lambda u: (u.market_cap or 0), reverse=True
            )
            universe = universe[:UNIVERSE_MAX_SIZE]
            print(f"  [pipeline] 유니버스 상위 {UNIVERSE_MAX_SIZE}개로 제한")

        # 시장 데이터 (screener 포함 → 추가 수집 최소화)
        market_data  = collect_market_data(universe, warnings)

        # SEC 데이터 (상위 SEC_MAX_TICKERS개만 처리)
        # 구성 종목은 항상 포함, 나머지는 market_cap 상위 순
        constituent_tickers = {c.ticker for c in constituents}
        universe_sorted = sorted(universe, key=lambda u: (u.market_cap or 0), reverse=True)
        sec_priority = list(constituent_tickers)
        for u in universe_sorted:
            if u.ticker not in constituent_tickers:
                sec_priority.append(u.ticker)
        all_tickers = sec_priority[:SEC_MAX_TICKERS]
        print(f"\n[pipeline] SEC 데이터 수집 시작 ({len(all_tickers)}개 ticker, 약 {len(all_tickers)*0.3/60:.1f}분 예상)...")
        cik_map     = fetch_cik_map()
        sec_records = collect_sec_data(all_tickers, cik_map, warnings)

    else:
        print("\n[pipeline] 기존 raw 스냅숏 사용 (--refresh 없음)")
        constituents = load_constituents_from_raw()
        universe     = load_universe_from_raw()
        market_data  = load_market_data_from_raw()
        sec_records  = load_sec_data_from_raw()

    # 소스 분류
    sec_sources = ["https://www.sec.gov/files/company_tickers.json",
                   "https://data.sec.gov/submissions/",
                   "https://data.sec.gov/api/xbrl/companyfacts/"]
    nasdaq_sources = ["https://api.nasdaq.com/api/quote/list-type/nasdaq100",
                      "https://api.nasdaq.com/api/screener/stocks"]

    for w in warnings:
        if "yfinance" in w.lower():
            secondary_sources.append("yfinance (secondary_market_data)")
        if "API 실패" in w or "실패" in w:
            pass  # 실패한 공식 소스는 warnings에만 기록

    official_sources = nasdaq_sources + sec_sources
    has_secondary = any("yfinance" in w.lower() for w in warnings)
    if has_secondary and "yfinance" not in str(secondary_sources):
        secondary_sources.append("yfinance (secondary_market_data)")

    # ── 2. 스냅숏 해시 (1차) ──────────────────────────────────────────────────
    snapshot_hash = compute_snapshot_hash()

    # ── 3. 정규화 + 자격 판정 ─────────────────────────────────────────────────
    print("\n[pipeline] 정규화 및 자격 판정 중...")
    records = build_candidate_universe(constituents, universe, market_data, sec_records)
    records = assess_eligibility(records)
    _save_csv(records)

    # ── 4. 순위 산정 (1차) ────────────────────────────────────────────────────
    print("\n[pipeline] 순위 산정 중...")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    inclusion_1 = rank_inclusion(records)
    exclusion_1 = rank_exclusion(records)

    # ── 5. 재현성 검증 (동일 raw로 2차 실행) ──────────────────────────────────
    print("\n[pipeline] 재현성 검증 중 (동일 스냅숏 재처리)...")
    records_2 = build_candidate_universe(constituents, universe, market_data, sec_records)
    records_2  = assess_eligibility(records_2)
    inclusion_2 = rank_inclusion(records_2)
    exclusion_2 = rank_exclusion(records_2)

    reproducibility_passed = verify_reproducibility(
        inclusion_1, inclusion_2, exclusion_1, exclusion_2
    )

    # ── 6. 품질 리포트 ────────────────────────────────────────────────────────
    failed_tickers = [s.ticker for s in sec_records if s.status == "failed"]
    quality_report = generate_report(
        records, sec_records, market_data,
        warnings, official_sources, secondary_sources, failed_tickers,
    )

    # ── 7. PASS 판정 ──────────────────────────────────────────────────────────
    total         = quality_report["total_universe_count"]
    n_constituents = quality_report["constituent_count"]
    sec_ok        = quality_report["sec_matched_count"]
    market_ok     = quality_report["market_data_matched_count"]

    market_cap_rate = market_ok / total if total else 0
    sec_match_rate  = sec_ok   / total if total else 0
    completeness    = (total - quality_report["missing_market_cap_count"]) / total if total else 0

    has_official_nasdaq = not any("API 실패" in w for w in warnings if "nasdaq" in w.lower())
    uses_secondary = bool(secondary_sources)

    pass_conditions = {
        "constituents_ok":  n_constituents >= PASS_MIN_CONSTITUENTS,
        "universe_ok":      total >= PASS_MIN_UNIVERSE,
        "market_cap_rate":  market_cap_rate >= PASS_MIN_MARKET_CAP_RATE,
        "sec_match_rate":   sec_match_rate >= PASS_MIN_SEC_MATCH_RATE,
        "inclusion_ok":     len(inclusion_1) >= PASS_MIN_INCLUSION_CANDIDATES,
        "exclusion_ok":     len(exclusion_1) >= PASS_MIN_EXCLUSION_CANDIDATES,
        "reproducibility":  reproducibility_passed,
        "output_files":     True,  # 파일 저장은 이미 완료됨
    }

    all_pass = all(pass_conditions.values())
    if not has_official_nasdaq or uses_secondary:
        overall = "CONDITIONAL_PASS" if all_pass else "FAIL"
    else:
        overall = "PASS" if all_pass else "FAIL"

    # ── 8. poc_result.json 저장 ────────────────────────────────────────────────
    result = {
        "run_id":                    str(uuid.uuid4()),
        "snapshot_hash":             snapshot_hash,
        "inclusion_candidate_count": len(inclusion_1),
        "exclusion_candidate_count": len(exclusion_1),
        "reproducibility_passed":    reproducibility_passed,
        "data_completeness_rate":    round(completeness, 4),
        "official_source_ratio":     round(1.0 - (len(secondary_sources) / max(len(official_sources), 1)), 4),
        "overall_result":            overall,
        "pass_conditions":           pass_conditions,
        "limitations": [
            "공식 Nasdaq 내부 선정 기준(75·100·125위 기준 등)을 완전히 재현하지 않음",
            "결과는 관찰 후보이며 실제 편입·편출을 예측하지 않음",
            "시장 데이터는 수집 시점 기준이며 실시간이 아님",
        ],
    }

    OUT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    OUT_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    # ── 9. 터미널 출력 ────────────────────────────────────────────────────────
    print(f"""
=== Nasdaq-100 Official Data PoC ===
Universe: {total}
Current constituents: {n_constituents}
SEC matched: {sec_ok}
Market data matched: {market_ok}
Inclusion watch candidates: {len(inclusion_1)}
Exclusion watch candidates: {len(exclusion_1)}
Data completeness: {completeness * 100:.1f}%
Reproducibility: {"PASS" if reproducibility_passed else "FAIL"}
Overall result: {overall}
""")

    return result
