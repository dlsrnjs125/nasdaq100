

"""
tests/test_reproducibility.py — 재현성 단위 테스트
"""
import pytest
from src.validation.reproducibility import verify_reproducibility
from src.processing.eligibility import assess_eligibility
from src.processing.rank_candidates import rank_inclusion, rank_exclusion


def test_same_snapshot_produces_same_results(sample_records):
    """동일 스냅숏을 두 번 처리하면 동일 결과가 생성된다."""
    # 두 번째 평가 (같은 데이터로 처음부터 다시)
    records_2 = assess_eligibility(
        [r.__class__(**{k: getattr(r, k) for k in r.__dataclass_fields__}) for r in sample_records]
    )

    inc_1 = rank_inclusion(sample_records)
    exc_1 = rank_exclusion(sample_records)
    inc_2 = rank_inclusion(records_2)
    exc_2 = rank_exclusion(records_2)

    assert verify_reproducibility(inc_1, inc_2, exc_1, exc_2), \
        "동일 스냅숏 재처리 결과가 다름 — 재현성 실패"


def test_verify_reproducibility_detects_mismatch():
    """verify_reproducibility가 불일치를 올바르게 감지한다."""
    inc1 = [{"ticker": "AAPL"}, {"ticker": "MSFT"}]
    inc2 = [{"ticker": "MSFT"}, {"ticker": "AAPL"}]  # 순서 다름
    exc  = [{"ticker": "SMLL"}]

    assert not verify_reproducibility(inc1, inc2, exc, exc), \
        "순서가 다른 경우 False를 반환해야 함"


def test_verify_reproducibility_passes_identical():
    """동일한 결과는 True를 반환한다."""
    inc = [{"ticker": "AAPL"}, {"ticker": "MSFT"}]
    exc = [{"ticker": "SMLL1"}, {"ticker": "SMLL2"}]
    assert verify_reproducibility(inc, inc, exc, exc)
