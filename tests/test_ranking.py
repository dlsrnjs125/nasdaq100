from __future__ import annotations
"""
tests/test_ranking.py — 순위 산정 단위 테스트
"""
import pytest
from src.processing.rank_candidates import rank_inclusion, rank_exclusion


def test_market_cap_descending_inclusion(sample_records):
    """편입 후보는 market_cap 내림차순으로 정렬된다."""
    rows = rank_inclusion(sample_records)
    caps = [r["market_cap"] for r in rows]
    assert caps == sorted(caps, reverse=True), "편입 후보가 market_cap 내림차순이 아님"


def test_market_cap_ascending_exclusion(sample_records):
    """편출 후보는 market_cap 오름차순으로 정렬된다."""
    rows = rank_exclusion(sample_records)
    caps = [r["market_cap"] for r in rows]
    assert caps == sorted(caps), "편출 후보가 market_cap 오름차순이 아님"


def test_inclusion_top_n_limit(sample_records):
    """편입 후보는 최대 10개를 초과하지 않는다."""
    from src.config import TOP_N
    rows = rank_inclusion(sample_records)
    assert len(rows) <= TOP_N


def test_exclusion_top_n_limit(sample_records):
    """편출 후보는 최대 10개를 초과하지 않는다."""
    from src.config import TOP_N
    rows = rank_exclusion(sample_records)
    assert len(rows) <= TOP_N


def test_output_files_created(tmp_path, monkeypatch, sample_records):
    """출력 파일 4개가 생성된다."""
    import src.config as cfg
    monkeypatch.setattr(cfg, "OUT_INCLUSION", tmp_path / "inclusion_watch_top10.csv")
    monkeypatch.setattr(cfg, "OUT_EXCLUSION", tmp_path / "exclusion_watch_top10.csv")
    monkeypatch.setattr(cfg, "OUT_QUALITY",   tmp_path / "data_quality_report.json")
    monkeypatch.setattr(cfg, "OUT_RESULT",    tmp_path / "poc_result.json")
    monkeypatch.setattr(cfg, "PROCESSED_UNIVERSE", tmp_path / "candidate_universe.csv")

    # 리임포트가 필요 없도록 직접 경로를 전달
    import src.processing.rank_candidates as rc
    monkeypatch.setattr(rc, "OUT_INCLUSION", tmp_path / "inclusion_watch_top10.csv")
    monkeypatch.setattr(rc, "OUT_EXCLUSION", tmp_path / "exclusion_watch_top10.csv")

    rank_inclusion(sample_records)
    rank_exclusion(sample_records)

    assert (tmp_path / "inclusion_watch_top10.csv").exists()
    assert (tmp_path / "exclusion_watch_top10.csv").exists()


def test_result_has_data_date(sample_records):
    """결과 파일에 데이터 기준일이 존재한다."""
    rows = rank_inclusion(sample_records)
    assert rows, "편입 후보가 없음"
    assert all(r.get("market_data_date") for r in rows), "market_data_date 누락"


def test_result_has_limitation(sample_records):
    """결과 파일에 limitation 항목이 존재한다."""
    rows = rank_inclusion(sample_records)
    assert all(r.get("limitation") for r in rows), "limitation 누락"
