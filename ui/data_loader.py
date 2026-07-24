"""
ui/data_loader.py
기존 outputs/ 파일을 읽어 Streamlit에서 사용할 수 있는 형태로 반환한다.

원칙:
- 파일이 없으면 임의 데이터를 생성하지 않는다.
- 친절한 안내 메시지와 함께 None 또는 빈 DataFrame을 반환한다.
- 숫자 변환 실패 시 앱을 중단하지 않는다.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# ── 경로 상수 ──────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR   = _PROJECT_ROOT / "outputs"

INCLUSION_CSV  = OUTPUTS_DIR / "inclusion_watch_top10.csv"
EXCLUSION_CSV  = OUTPUTS_DIR / "exclusion_watch_top10.csv"
QUALITY_JSON   = OUTPUTS_DIR / "data_quality_report.json"
RESULT_JSON    = OUTPUTS_DIR / "poc_result.json"


# ── 시가총액 포매터 ────────────────────────────────────────────────────────────

def fmt_market_cap(val) -> str:
    """숫자를 $1.23T / $125.4B / $850.0M 형태로 반환한다."""
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if v >= 1e12:
        return f"${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"${v / 1e6:.1f}M"
    return f"${v:,.0f}"


def _safe_float(val) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ── 로더 함수 ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_inclusion_candidates() -> tuple[pd.DataFrame, str]:
    """
    inclusion_watch_top10.csv 로드.
    Returns (DataFrame, warning_message).
    파일이 없거나 비어 있으면 빈 DataFrame + 안내 메시지를 반환한다.
    """
    if not INCLUSION_CSV.exists():
        return pd.DataFrame(), (
            f"`{INCLUSION_CSV.name}` 파일이 없습니다. "
            "`python run_poc.py --refresh` 를 먼저 실행해 주세요."
        )
    try:
        df = pd.read_csv(INCLUSION_CSV)
        df.columns = df.columns.str.strip()

        if df.empty:
            return pd.DataFrame(), (
                "편입 관찰 후보 데이터가 비어 있습니다. "
                "데이터 품질 리포트를 확인하거나 `--refresh` 로 다시 수집해 주세요."
            )

        # 숫자 변환
        if "market_cap" in df.columns:
            df["market_cap_fmt"] = df["market_cap"].apply(fmt_market_cap)
            df["market_cap"] = df["market_cap"].apply(_safe_float)

        # 빈 섹터 처리
        for col in ("sector", "eligibility_status", "exclusion_reason"):
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).replace("nan", "")

        return df, ""
    except Exception as exc:
        return pd.DataFrame(), f"파일 읽기 오류: {exc}"


@st.cache_data(ttl=300)
def load_exclusion_candidates() -> tuple[pd.DataFrame, str]:
    """
    exclusion_watch_top10.csv 로드.
    Returns (DataFrame, warning_message).
    """
    if not EXCLUSION_CSV.exists():
        return pd.DataFrame(), (
            f"`{EXCLUSION_CSV.name}` 파일이 없습니다. "
            "`python run_poc.py --refresh` 를 먼저 실행해 주세요."
        )
    try:
        df = pd.read_csv(EXCLUSION_CSV)
        df.columns = df.columns.str.strip()

        if df.empty:
            return pd.DataFrame(), "편출 관찰 후보 데이터가 비어 있습니다."

        if "market_cap" in df.columns:
            df["market_cap_fmt"] = df["market_cap"].apply(fmt_market_cap)
            df["market_cap"] = df["market_cap"].apply(_safe_float)

        for col in ("sector", "rationale", "limitation"):
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).replace("nan", "")

        return df, ""
    except Exception as exc:
        return pd.DataFrame(), f"파일 읽기 오류: {exc}"


@st.cache_data(ttl=300)
def load_data_quality_report() -> tuple[dict, str]:
    """
    data_quality_report.json 로드.
    Returns (dict, warning_message).
    """
    if not QUALITY_JSON.exists():
        return {}, (
            f"`{QUALITY_JSON.name}` 파일이 없습니다. "
            "`python run_poc.py --refresh` 를 먼저 실행해 주세요."
        )
    try:
        data = json.loads(QUALITY_JSON.read_text(encoding="utf-8"))
        return data, ""
    except json.JSONDecodeError as exc:
        return {}, f"JSON 파싱 오류: {exc}"


@st.cache_data(ttl=300)
def load_poc_result() -> tuple[dict, str]:
    """
    poc_result.json 로드.
    Returns (dict, warning_message).
    """
    if not RESULT_JSON.exists():
        return {}, (
            f"`{RESULT_JSON.name}` 파일이 없습니다. "
            "`python run_poc.py --refresh` 를 먼저 실행해 주세요."
        )
    try:
        data = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
        return data, ""
    except json.JSONDecodeError as exc:
        return {}, f"JSON 파싱 오류: {exc}"


def outputs_exist() -> bool:
    """outputs/ 파일 4개가 모두 존재하는지 확인한다."""
    return all(p.exists() for p in [INCLUSION_CSV, EXCLUSION_CSV, QUALITY_JSON, RESULT_JSON])
