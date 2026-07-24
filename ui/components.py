"""
ui/components.py
재사용 가능한 Streamlit UI 컴포넌트
"""
from __future__ import annotations

import streamlit as st

from ui.data_loader import fmt_market_cap


# ── 상태 배지 ──────────────────────────────────────────────────────────────────

def status_badge(status: str) -> None:
    """PASS / CONDITIONAL_PASS / FAIL 상태를 Streamlit 메시지로 표시한다."""
    s = str(status).upper()
    if s == "PASS":
        st.success(f"✅ {s}")
    elif s == "CONDITIONAL_PASS":
        st.warning(f"⚠️ {s}")
    elif s == "FAIL":
        st.error(f"❌ {s}")
    else:
        st.info(f"ℹ️ {s or 'UNKNOWN'}")


def bool_badge(val: bool, label: str = "") -> str:
    """True/False를 이모지 문자열로 변환한다."""
    prefix = f"{label}: " if label else ""
    return f"{prefix}{'✅' if val else '❌'}"


# ── 공통 면책 문구 ─────────────────────────────────────────────────────────────

def disclaimer_box() -> None:
    st.info(
        "⚠️ **본 화면은 투자 추천이 아닙니다.** "
        "공개 데이터를 기반으로 계산한 관찰 후보이며, "
        "공식 Nasdaq 편입·편출 확정 결과와 다릅니다."
    )


# ── AI 연결 대기 카드 ──────────────────────────────────────────────────────────

def ai_pending_card(
    title: str,
    description: str,
    status: str = "🔌 AI 연결 대기 중",
    planned: bool = False,
) -> None:
    """AI 미연결 기능 플레이스홀더 카드."""
    badge = "🗓️ 추후 검토 예정" if planned else "🔌 AI 연결 대기 중"
    with st.container(border=True):
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"**{title}**")
            st.caption(description)
        with cols[1]:
            st.caption(badge)


# ── 기업 상세 패널 ─────────────────────────────────────────────────────────────

def inclusion_detail_panel(row: dict) -> None:
    """편입 후보 선택 시 상세 정보를 표시한다."""
    with st.container(border=True):
        st.markdown(f"### {row.get('company_name', '')}  `{row.get('ticker', '')}`")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("시가총액", fmt_market_cap(row.get("market_cap")))
            st.markdown(f"**업종:** {row.get('sector') or '미확인'}")
            st.markdown(f"**현재 구성 여부:** 비구성 종목")
        with c2:
            st.markdown(f"**데이터 기준일:** {row.get('market_data_date', 'N/A')}")
            st.markdown(f"**적격 상태:** `{row.get('eligibility_status', 'N/A')}`")
            src = row.get("market_cap_source") or "N/A"
            st.markdown(f"**시가총액 출처:** {src}")
        st.markdown(f"**관찰 이유:** {row.get('rationale', 'N/A')}")
        st.caption(f"⚠️ 제한 사항: {row.get('limitation', 'N/A')}")
        st.caption("공식 Nasdaq 내부 선정 기준을 재현하지 않으며, 투자 추천이 아닙니다.")


def exclusion_detail_panel(row: dict) -> None:
    """편출 후보 선택 시 상세 정보를 표시한다."""
    with st.container(border=True):
        st.markdown(f"### {row.get('company_name', '')}  `{row.get('ticker', '')}`")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("시가총액", fmt_market_cap(row.get("market_cap")))
            st.markdown(f"**업종:** {row.get('sector') or '미확인'}")
            st.markdown(f"**현재 구성 여부:** 구성 종목")
        with c2:
            st.markdown(f"**데이터 기준일:** {row.get('market_data_date', 'N/A')}")
        st.markdown(f"**관찰 이유:** {row.get('rationale', 'N/A')}")
        st.info(
            "시가총액 하위권에 있다는 것이 편출 확정을 의미하지 않습니다. "
            "Nasdaq은 내부 기준과 재량으로 최종 결정합니다."
        )
        st.caption(f"⚠️ 제한 사항: {row.get('limitation', 'N/A')}")


# ── Pass condition 테이블 ──────────────────────────────────────────────────────

def pass_conditions_table(conditions: dict) -> None:
    """pass_conditions dict를 간단한 표로 렌더링한다."""
    labels = {
        "constituents_ok":  "구성 종목 90개 이상",
        "universe_ok":      "유니버스 150개 이상",
        "market_cap_rate":  "시가총액 확보율 90%↑",
        "sec_match_rate":   "SEC CIK 매핑 90%↑",
        "inclusion_ok":     "편입 관찰 후보 5개 이상",
        "exclusion_ok":     "편출 관찰 후보 5개 이상",
        "reproducibility":  "재현성 검증 통과",
        "output_files":     "출력 파일 4개 생성",
    }
    rows = []
    for key, label in labels.items():
        val = conditions.get(key)
        rows.append({"항목": label, "결과": "✅ 통과" if val else "❌ 미통과"})

    import pandas as pd
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
