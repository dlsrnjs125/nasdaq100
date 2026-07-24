"""
tests/test_streamlit_data_loader.py
ui/data_loader.py 단위 테스트 — 네트워크 호출 없음
"""
from __future__ import annotations

import csv
import json
import pytest
from pathlib import Path


# ── fixture: 임시 outputs 디렉터리 ────────────────────────────────────────────

@pytest.fixture
def mock_outputs(tmp_path, monkeypatch):
    """실제 CSV/JSON과 동일한 구조의 임시 파일을 생성한다."""
    import ui.data_loader as dl
    monkeypatch.setattr(dl, "OUTPUTS_DIR",   tmp_path)
    monkeypatch.setattr(dl, "INCLUSION_CSV", tmp_path / "inclusion_watch_top10.csv")
    monkeypatch.setattr(dl, "EXCLUSION_CSV", tmp_path / "exclusion_watch_top10.csv")
    monkeypatch.setattr(dl, "QUALITY_JSON",  tmp_path / "data_quality_report.json")
    monkeypatch.setattr(dl, "RESULT_JSON",   tmp_path / "poc_result.json")

    # inclusion CSV
    inc = tmp_path / "inclusion_watch_top10.csv"
    with open(inc, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "watch_rank", "ticker", "company_name", "market_cap",
            "market_cap_source", "sector", "eligibility_status",
            "market_data_date", "rationale", "limitation",
        ])
        w.writeheader()
        w.writerow({
            "watch_rank": 1, "ticker": "TESTCO", "company_name": "Test Co.",
            "market_cap": 500_000_000_000, "market_cap_source": "provided",
            "sector": "Technology", "eligibility_status": "eligible",
            "market_data_date": "2024-01-01", "rationale": "test rationale",
            "limitation": "test limitation",
        })

    # exclusion CSV
    exc = tmp_path / "exclusion_watch_top10.csv"
    with open(exc, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "watch_rank", "ticker", "company_name", "market_cap",
            "sector", "market_data_date", "rationale", "limitation",
        ])
        w.writeheader()
        w.writerow({
            "watch_rank": 1, "ticker": "SMLLCO", "company_name": "Small Co.",
            "market_cap": 10_000_000_000, "sector": "",
            "market_data_date": "2024-01-01", "rationale": "test",
            "limitation": "test limitation",
        })

    # quality json
    q = tmp_path / "data_quality_report.json"
    q.write_text(json.dumps({
        "collected_at": "2024-01-01T00:00:00Z",
        "total_universe_count": 200,
        "constituent_count": 100,
        "sec_matched_count": 195,
        "market_data_matched_count": 198,
        "missing_sector_count": 50,
        "unknown_eligibility_count": 50,
        "source_warnings": [],
    }), encoding="utf-8")

    # result json
    r = tmp_path / "poc_result.json"
    r.write_text(json.dumps({
        "overall_result": "CONDITIONAL_PASS",
        "reproducibility_passed": True,
        "data_completeness_rate": 0.95,
        "official_source_ratio": 0.85,
        "inclusion_candidate_count": 1,
        "exclusion_candidate_count": 1,
        "limitations": ["테스트 제한 사항"],
    }), encoding="utf-8")

    return tmp_path


# ── 테스트 ─────────────────────────────────────────────────────────────────────

def test_load_inclusion_candidates(mock_outputs):
    """inclusion 후보 CSV를 정상적으로 읽는다."""
    import ui.data_loader as dl
    dl.load_inclusion_candidates.clear()
    df, warn = dl.load_inclusion_candidates()
    assert warn == "", f"예상치 못한 경고: {warn}"
    assert not df.empty
    assert "ticker" in df.columns
    assert df.iloc[0]["ticker"] == "TESTCO"


def test_load_exclusion_candidates(mock_outputs):
    """exclusion 후보 CSV를 정상적으로 읽는다."""
    import ui.data_loader as dl
    dl.load_exclusion_candidates.clear()
    df, warn = dl.load_exclusion_candidates()
    assert warn == "", f"예상치 못한 경고: {warn}"
    assert not df.empty
    assert df.iloc[0]["ticker"] == "SMLLCO"


def test_load_poc_result(mock_outputs):
    """poc_result.json을 정상적으로 읽는다."""
    import ui.data_loader as dl
    dl.load_poc_result.clear()
    data, warn = dl.load_poc_result()
    assert warn == ""
    assert data["overall_result"] == "CONDITIONAL_PASS"
    assert data["reproducibility_passed"] is True


def test_no_data_generated_when_file_missing(tmp_path, monkeypatch):
    """파일이 없을 때 임의 데이터를 생성하지 않는다."""
    import ui.data_loader as dl
    monkeypatch.setattr(dl, "INCLUSION_CSV", tmp_path / "nonexistent.csv")
    monkeypatch.setattr(dl, "EXCLUSION_CSV", tmp_path / "nonexistent2.csv")
    monkeypatch.setattr(dl, "QUALITY_JSON",  tmp_path / "nonexistent3.json")
    monkeypatch.setattr(dl, "RESULT_JSON",   tmp_path / "nonexistent4.json")

    dl.load_inclusion_candidates.clear()
    dl.load_exclusion_candidates.clear()
    dl.load_data_quality_report.clear()
    dl.load_poc_result.clear()

    inc_df, inc_warn = dl.load_inclusion_candidates()
    exc_df, exc_warn = dl.load_exclusion_candidates()
    q_data, q_warn   = dl.load_data_quality_report()
    r_data, r_warn   = dl.load_poc_result()

    assert inc_df.empty,  "파일 없을 때 빈 DataFrame이어야 함"
    assert exc_df.empty,  "파일 없을 때 빈 DataFrame이어야 함"
    assert q_data == {},  "파일 없을 때 빈 dict이어야 함"
    assert r_data == {},  "파일 없을 때 빈 dict이어야 함"
    assert inc_warn != "" and exc_warn != "" and q_warn != "" and r_warn != ""


def test_numeric_column_conversion_does_not_crash(mock_outputs):
    """숫자형 컬럼 변환에서 앱이 중단되지 않는다."""
    import ui.data_loader as dl
    dl.load_inclusion_candidates.clear()
    df, _ = dl.load_inclusion_candidates()
    # market_cap_fmt가 문자열로 존재해야 함
    assert "market_cap_fmt" in df.columns
    assert isinstance(df.iloc[0]["market_cap_fmt"], str)
    # 포맷 확인 ($T 단위)
    assert "$" in df.iloc[0]["market_cap_fmt"]


def test_fmt_market_cap():
    """시가총액 포매터가 올바르게 동작한다."""
    from ui.data_loader import fmt_market_cap
    assert fmt_market_cap(1_500_000_000_000) == "$1.50T"
    assert fmt_market_cap(125_400_000_000)   == "$125.4B"
    assert fmt_market_cap(850_000_000)       == "$850.0M"
    assert fmt_market_cap(None)              == "N/A"
    assert fmt_market_cap("invalid")         == "N/A"
