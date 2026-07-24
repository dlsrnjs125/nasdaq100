from __future__ import annotations
"""
src/validation/reproducibility.py
스냅숏 해시 생성 및 재현성 검증

재현성 검증 방식:
- raw 파일 4개의 내용을 결합하여 SHA-256 해시 생성 (snapshot_hash)
- 동일 스냅숏으로 파이프라인을 두 번 실행하면 동일 결과가 생성되는지 확인
"""
import hashlib
import json
from pathlib import Path

from src.config import (
    RAW_CONSTITUENTS, RAW_UNIVERSE, RAW_MARKET_DATA, RAW_SEC_DATA,
)


def compute_snapshot_hash() -> str:
    """
    raw 스냅숏 4개 파일의 내용을 결합하여 SHA-256 해시를 반환한다.
    파일이 없으면 빈 바이트를 포함한다.
    """
    h = hashlib.sha256()
    for path in [RAW_CONSTITUENTS, RAW_UNIVERSE, RAW_MARKET_DATA, RAW_SEC_DATA]:
        if path.exists():
            h.update(path.read_bytes())
        else:
            h.update(b"")
    return h.hexdigest()


def verify_reproducibility(
    inclusion_rows_1: list[dict],
    inclusion_rows_2: list[dict],
    exclusion_rows_1: list[dict],
    exclusion_rows_2: list[dict],
) -> bool:
    """
    두 실행 결과의 ticker 순서가 동일한지 확인한다.
    """
    def extract_tickers(rows: list[dict]) -> list[str]:
        return [str(r.get("ticker", "")) for r in rows]

    inc_match = extract_tickers(inclusion_rows_1) == extract_tickers(inclusion_rows_2)
    exc_match = extract_tickers(exclusion_rows_1) == extract_tickers(exclusion_rows_2)
    return inc_match and exc_match
