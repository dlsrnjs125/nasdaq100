"""
app.py — Nasdaq-100 편입·편출 관찰 후보 Streamlit Prototype 진입점

실행:
    streamlit run app.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st

# ── 페이지 설정 ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nasdaq-100 관찰 리포트 Prototype",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 모듈 로드 (프로젝트 루트를 sys.path에 추가) ────────────────────────────────
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ui.data_loader import (
    load_data_quality_report,
    load_poc_result,
    outputs_exist,
    OUTPUTS_DIR,
    INCLUSION_CSV,
    EXCLUSION_CSV,
    QUALITY_JSON,
    RESULT_JSON,
)
from ui.pages import page_overview, page_inclusion, page_exclusion, page_ai_search


# ── 사이드바 ──────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.title("📊 Nasdaq-100 관찰 리포트")
        st.caption("Prototype — 공개 데이터 기반 PoC")

        st.divider()

        # 데이터 기준일 / PoC 상태
        quality, _ = load_data_quality_report()
        result,  _ = load_poc_result()

        collected_at = quality.get("collected_at", "")
        if collected_at:
            st.markdown(f"**데이터 수집 시각**  \n`{collected_at[:19].replace('T', ' ')} UTC`")
        else:
            st.markdown("**데이터 수집 시각:** N/A")

        overall = result.get("overall_result", "UNKNOWN")
        st.markdown(f"**PoC 상태:** `{overall}`")

        st.divider()

        # 데이터 새로고침 버튼
        st.subheader("🔄 데이터 새로고침")
        st.caption(
            "외부 데이터 수집에는 시간이 걸리거나 "
            "일부 출처 접근이 실패할 수 있습니다."
        )

        if st.button("PoC 데이터 새로고침", use_container_width=True, key="refresh_btn"):
            _run_refresh()

        st.divider()

        # 데이터 출처 안내
        st.subheader("📁 데이터 출처")
        st.caption("• Nasdaq 공식 API (1순위)")
        st.caption("• SEC EDGAR 공식 API")
        st.caption("• yfinance (보조, 필요 시)")

        st.divider()

        st.warning(
            "⚠️ **투자 추천이 아닙니다.**  \n"
            "공개 데이터 기반 관찰 후보이며, "
            "공식 Nasdaq 편입·편출 확정 결과와 다릅니다."
        )


def _run_refresh() -> None:
    """기존 pipeline.run() 함수를 직접 호출하거나 run_poc.py를 subprocess로 실행한다."""
    with st.spinner("PoC 파이프라인 실행 중... (수 분이 소요될 수 있습니다)"):
        try:
            # 직접 호출 시도
            from src.pipeline import run as _run_pipeline
            _run_pipeline(refresh=True)

            # 캐시 초기화
            st.cache_data.clear()
            st.success("✅ 데이터 새로고침 완료! 화면을 다시 로드합니다.")
            st.rerun()

        except ImportError:
            # src 모듈을 찾을 수 없는 경우 subprocess fallback
            run_poc_path = _ROOT / "run_poc.py"
            result = subprocess.run(
                [sys.executable, str(run_poc_path), "--refresh"],
                capture_output=True,
                text=True,
                cwd=str(_ROOT),
                timeout=600,
            )
            if result.returncode in (0, 1):  # 0=PASS, 1=CONDITIONAL/FAIL
                st.cache_data.clear()
                st.success("✅ 데이터 새로고침 완료!")
                st.rerun()
            else:
                st.error(
                    f"파이프라인 실행 실패 (exit code {result.returncode})\n\n"
                    f"```\n{result.stderr[-500:] or result.stdout[-500:]}\n```"
                )

        except Exception as exc:
            st.error(f"새로고침 중 오류가 발생했습니다: {exc}")


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    render_sidebar()

    st.title("Nasdaq-100 편입·편출 관찰 리포트 Prototype")
    st.caption(
        "공개 데이터를 기반으로 편입·편출 관찰 후보를 보여주는 Prototype입니다. "
        "공식 Nasdaq 편입·편출 확정 결과가 아니며, **투자 추천이 아닙니다.**"
    )

    # outputs 파일 없을 때 안내
    if not outputs_exist():
        st.warning(
            "⚠️ PoC 출력 파일이 없습니다. 아래 명령으로 먼저 데이터를 수집해 주세요."
        )
        st.code("python run_poc.py --refresh", language="bash")
        st.stop()

    # 4개 탭
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📈 편입 관찰 후보",
        "📉 편출 관찰 후보",
        "🤖 AI 분석 기능 예정",
    ])

    with tab1:
        page_overview()
    with tab2:
        page_inclusion()
    with tab3:
        page_exclusion()
    with tab4:
        page_ai_search()


if __name__ == "__main__":
    main()
