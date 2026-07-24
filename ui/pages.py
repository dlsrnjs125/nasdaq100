"""
ui/pages.py
4개 탭 페이지 구현

모든 데이터는 ui/data_loader.py를 통해 읽는다.
기존 PoC 계산 로직을 복사하거나 재실행하지 않는다.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.data_loader import (
    load_inclusion_candidates,
    load_exclusion_candidates,
    load_data_quality_report,
    load_poc_result,
    fmt_market_cap,
)
from ui.components import (
    status_badge,
    bool_badge,
    disclaimer_box,
    ai_pending_card,
    inclusion_detail_panel,
    exclusion_detail_panel,
    pass_conditions_table,
)


# ── 1. Overview ───────────────────────────────────────────────────────────────

def page_overview() -> None:
    st.header("📊 Overview")
    disclaimer_box()

    quality, q_warn = load_data_quality_report()
    result,  r_warn = load_poc_result()
    inc_df,  _      = load_inclusion_candidates()
    exc_df,  _      = load_exclusion_candidates()

    if q_warn and not quality:
        st.warning(q_warn)
        st.markdown(
            "**실행 방법:**\n```bash\npython run_poc.py --refresh\n```"
        )
        return

    # ── 상단 지표 카드 ────────────────────────────────────────────────────────
    st.subheader("핵심 지표")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("전체 분석 기업", quality.get("total_universe_count", "N/A"))
    c2.metric("Nasdaq-100 구성 종목", quality.get("constituent_count", "N/A"))
    c3.metric("편입 관찰 후보", len(inc_df) if not inc_df.empty else 0)
    c4.metric("편출 관찰 후보", len(exc_df) if not exc_df.empty else 0)

    completeness = result.get("data_completeness_rate")
    c5.metric("데이터 완전성", f"{completeness * 100:.1f}%" if completeness is not None else "N/A")

    overall = result.get("overall_result", "UNKNOWN")
    with c6:
        st.markdown("**PoC 상태**")
        status_badge(overall)

    st.divider()

    # ── PoC 결과 요약 ─────────────────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.subheader("PoC 결과 요약")
        repro = result.get("reproducibility_passed")
        src_ratio = result.get("official_source_ratio")
        st.markdown(f"- {bool_badge(repro, '재현성 검증')}")
        st.markdown(
            f"- 데이터 완전성: **{completeness * 100:.1f}%**" if completeness else "- 데이터 완전성: N/A"
        )
        st.markdown(
            f"- 공식 출처 비율: **{src_ratio * 100:.1f}%**" if src_ratio else "- 공식 출처 비율: N/A"
        )
        st.markdown(f"- 전체 결과: **{overall}**")

        if result.get("pass_conditions"):
            with st.expander("PASS 조건 세부 내역"):
                pass_conditions_table(result["pass_conditions"])

    with right:
        st.subheader("데이터 출처")
        official = quality.get("official_sources_used", [])
        secondary = quality.get("secondary_sources_used", [])
        collected_at = quality.get("collected_at", "N/A")

        st.markdown("**공식 출처**")
        for src in official:
            st.caption(f"• {src}")

        if secondary:
            st.markdown("**보조 출처**")
            for src in secondary:
                st.caption(f"• {src}")

        st.markdown(f"**데이터 수집 시각:** `{collected_at[:19].replace('T', ' ')}`")

        # 데이터 품질 경고
        missing_sector = quality.get("missing_sector_count", 0)
        if missing_sector and missing_sector > 0:
            st.warning(
                f"⚠️ {missing_sector}개 기업의 섹터 정보가 없어 "
                "편입 후보 자격 판정이 불가능했습니다. "
                "`--refresh` 로 재수집 시 Nasdaq screener의 sector 제공 여부에 따라 달라집니다."
            )

    st.divider()

    # ── 제한 사항 ─────────────────────────────────────────────────────────────
    st.subheader("주요 제한 사항")
    for lim in result.get("limitations", []):
        st.caption(f"• {lim}")

    st.caption(
        "• 이 Prototype은 기존 PoC outputs를 시각화한 것으로, "
        "공식 Nasdaq 편입·편출 기준을 재현하지 않습니다."
    )


# ── 2. 편입 관찰 후보 ─────────────────────────────────────────────────────────

def page_inclusion() -> None:
    st.header("📈 편입 관찰 후보")
    st.markdown(
        "> **아래 목록은 공개 데이터와 PoC 규칙으로 계산한 편입 관찰 후보입니다. "
        "공식 Nasdaq 예상 순위나 편입 확정 목록이 아닙니다.**"
    )
    disclaimer_box()

    df, warn = load_inclusion_candidates()

    if warn or df.empty:
        st.warning(warn or "편입 관찰 후보 데이터가 없습니다.")

        # 왜 없는지 품질 리포트에서 설명
        quality, _ = load_data_quality_report()
        missing_sector = quality.get("missing_sector_count", 0)
        unknown_elig   = quality.get("unknown_eligibility_count", 0)
        if missing_sector:
            st.info(
                f"**데이터 품질 안내:** {missing_sector}개 기업의 섹터 데이터가 없어 "
                f"{unknown_elig}개 기업의 편입 자격이 `unknown`으로 분류됐습니다. "
                "섹터를 알 수 없는 기업은 금융업 여부 판단 불가로 편입 후보에서 제외됩니다."
            )
        return

    # ── 필터 ──────────────────────────────────────────────────────────────────
    col_search, col_sector, col_status = st.columns([3, 2, 2])

    with col_search:
        search = st.text_input("🔍 티커 / 기업명 검색", key="inc_search")
    with col_sector:
        sectors = ["전체"] + sorted(df["sector"].dropna().unique().tolist()) if "sector" in df.columns else ["전체"]
        sel_sector = st.selectbox("업종 필터", sectors, key="inc_sector")
    with col_status:
        statuses = ["전체"] + sorted(df["eligibility_status"].dropna().unique().tolist()) if "eligibility_status" in df.columns else ["전체"]
        sel_status = st.selectbox("적격 상태 필터", statuses, key="inc_status")

    filtered = df.copy()
    if search:
        mask = (
            filtered["ticker"].str.contains(search, case=False, na=False)
            | filtered["company_name"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if sel_sector != "전체" and "sector" in filtered.columns:
        filtered = filtered[filtered["sector"] == sel_sector]
    if sel_status != "전체" and "eligibility_status" in filtered.columns:
        filtered = filtered[filtered["eligibility_status"] == sel_status]

    # ── 표 ────────────────────────────────────────────────────────────────────
    display_cols = [c for c in [
        "watch_rank", "ticker", "company_name", "market_cap_fmt",
        "sector", "market_data_date", "eligibility_status",
    ] if c in filtered.columns]

    col_labels = {
        "watch_rank": "순위", "ticker": "티커", "company_name": "기업명",
        "market_cap_fmt": "시가총액", "sector": "업종",
        "market_data_date": "데이터 기준일", "eligibility_status": "적격 상태",
    }

    st.dataframe(
        filtered[display_cols].rename(columns=col_labels),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"총 {len(filtered)}개 표시 (전체 {len(df)}개)")

    # ── 기업 선택 상세 ────────────────────────────────────────────────────────
    if not filtered.empty:
        tickers = filtered["ticker"].tolist()
        sel = st.selectbox("기업 상세 보기", ["선택하세요"] + tickers, key="inc_detail_sel")
        if sel != "선택하세요":
            row = filtered[filtered["ticker"] == sel].iloc[0].to_dict()
            inclusion_detail_panel(row)


# ── 3. 편출 관찰 후보 ─────────────────────────────────────────────────────────

def page_exclusion() -> None:
    st.header("📉 편출 관찰 후보")
    st.markdown(
        "> **아래 목록은 현재 구성 종목 가운데 공개 데이터 기준 시가총액 하위권에 있는 관찰 대상입니다. "
        "편출 확정 또는 기업 부실을 의미하지 않습니다.**"
    )
    disclaimer_box()

    df, warn = load_exclusion_candidates()

    if warn or df.empty:
        st.warning(warn or "편출 관찰 후보 데이터가 없습니다.")
        return

    # ── 필터 ──────────────────────────────────────────────────────────────────
    col_search, col_sector = st.columns([3, 2])
    with col_search:
        search = st.text_input("🔍 티커 / 기업명 검색", key="exc_search")
    with col_sector:
        sectors = ["전체"] + sorted(df["sector"].dropna().replace("", None).dropna().unique().tolist()) if "sector" in df.columns else ["전체"]
        sel_sector = st.selectbox("업종 필터", sectors, key="exc_sector")

    filtered = df.copy()
    if search:
        mask = (
            filtered["ticker"].str.contains(search, case=False, na=False)
            | filtered["company_name"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if sel_sector != "전체" and "sector" in filtered.columns:
        filtered = filtered[filtered["sector"] == sel_sector]

    display_cols = [c for c in [
        "watch_rank", "ticker", "company_name", "market_cap_fmt",
        "sector", "market_data_date",
    ] if c in filtered.columns]

    col_labels = {
        "watch_rank": "순위", "ticker": "티커", "company_name": "기업명",
        "market_cap_fmt": "시가총액", "sector": "업종",
        "market_data_date": "데이터 기준일",
    }

    st.dataframe(
        filtered[display_cols].rename(columns=col_labels),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"총 {len(filtered)}개 표시 (전체 {len(df)}개)")

    # ── 기업 선택 상세 ────────────────────────────────────────────────────────
    if not filtered.empty:
        tickers = filtered["ticker"].tolist()
        sel = st.selectbox("기업 상세 보기", ["선택하세요"] + tickers, key="exc_detail_sel")
        if sel != "선택하세요":
            row = filtered[filtered["ticker"] == sel].iloc[0].to_dict()
            exclusion_detail_panel(row)



# ── 4. 공식 문서 검색 + AI 기능 예정 ─────────────────────────────────────────

def page_ai_search() -> None:
    """BGE-M3 공식 문서 의미 검색 + 나머지 AI 예정 기능 화면."""
    st.header("🔍 공식 문서 근거 검색")
    st.markdown(
        "> **이 기능은 생성형 답변이 아닙니다.** "
        "질문과 관련된 Nasdaq·SEC 공식 원문을 검색해 보여줍니다."
    )

    # ── 검색 연결 상태 표시 ───────────────────────────────────────────────────
    _status_col1, _status_col2, _status_col3, _status_col4 = st.columns(4)
    _status_col1.success("✅ 공식 문서 근거 검색: 연결됨")
    _status_col2.warning("🔌 공식 문서 요약: AI 연결 대기")
    _status_col3.warning("🔌 기업 사건 추출: AI 연결 대기")
    _status_col4.info("🗓️ Bull/Bear 시나리오: 추후 검토")

    st.divider()

    # ── 인덱스 상태 확인 ─────────────────────────────────────────────────────
    try:
        from src.retrieval.config import MANIFEST_FILE, EMBEDDINGS_FILE
        index_ready = MANIFEST_FILE.exists() and EMBEDDINGS_FILE.exists()
    except Exception:
        index_ready = False

    if not index_ready:
        st.warning(
            "⚠️ 검색 인덱스가 없습니다. 아래 명령으로 먼저 인덱스를 생성하세요."
        )
        st.code("python -m src.retrieval.indexer --refresh", language="bash")
        st.stop()

    # 인덱스 메타 표시
    try:
        import json
        from src.retrieval.config import MANIFEST_FILE
        manifest = json.loads(MANIFEST_FILE.read_text())
        c1, c2, c3 = st.columns(3)
        c1.metric("인덱스 청크 수", manifest.get("chunk_count", "?"))
        c2.metric("임베딩 차원", manifest.get("embedding_dimension", "?"))
        c3.metric(
            "사용 디바이스",
            manifest.get("device", "?"),
            help="mps = Apple Silicon GPU, cpu = CPU",
        )
        st.caption(
            f"모델: `{manifest.get('model_name', 'BAAI/bge-m3')}`  |  "
            f"인덱스 생성: `{(manifest.get('built_at') or '')[:19].replace('T', ' ')} UTC`"
        )
    except Exception as e:
        st.caption(f"인덱스 정보 로딩 오류: {e}")

    st.divider()

    # ── 검색 입력 ─────────────────────────────────────────────────────────────
    st.subheader("질문 입력")
    col_q, col_k = st.columns([4, 1])
    with col_q:
        query = st.text_input(
            "질문 (한국어·영어 모두 가능)",
            placeholder="예: Nasdaq-100 편출 기준은 무엇인가?",
            key="retrieval_query",
        )
    with col_k:
        top_k = st.selectbox("결과 수", [3, 5], index=0, key="retrieval_top_k")

    # source_type 필터
    st.markdown("**출처 필터**")
    src_cols = st.columns(3)
    use_nasdaq = src_cols[0].checkbox("📊 Nasdaq 공식", value=True, key="src_nasdaq")
    use_sec    = src_cols[1].checkbox("🏛️ SEC 공식",    value=True, key="src_sec")
    use_ir     = src_cols[2].checkbox("🏢 기업 IR",      value=False, key="src_ir")

    source_types: list[str] = []
    if use_nasdaq: source_types.append("nasdaq_official")
    if use_sec:    source_types.append("sec_official")
    if use_ir:     source_types.append("company_ir")

    search_btn = st.button(
        "🔍 검색", key="retrieval_search_btn",
        disabled=(not query.strip() or not source_types),
    )

    if search_btn:
        if not source_types:
            st.warning("출처를 하나 이상 선택해 주세요.")
        elif not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            _run_search(query.strip(), top_k, source_types)

    st.divider()

    # ── 나머지 AI 예정 기능 카드 ──────────────────────────────────────────────
    st.subheader("🤖 추가 AI 기능 예정")
    st.caption("아래 기능들은 현재 AI 모델이 연결되지 않아 UI만 구현되었습니다.")

    ai_pending_card(
        "📄 공식 문서 요약",
        "Nasdaq 방법론과 공식 변경 발표를 쉬운 문장으로 요약할 예정입니다. "
        "(BGE-M3 검색 결과 → Decoder 모델 요약)",
    )
    ai_pending_card(
        "🔍 기업 사건 추출",
        "SEC 공시에서 인수합병, 상장폐지, 기업분할 등 주요 사건을 추출할 예정입니다.",
    )
    ai_pending_card(
        "📋 Bull / Base / Bear 조건 시나리오",
        "목표주가나 수익률 예측이 아니라, 후보 상태를 변경할 수 있는 조건을 정리할 예정입니다.",
        planned=True,
    )


def _run_search(query: str, top_k: int, source_types: list[str]) -> None:
    """검색 실행 및 결과 렌더링."""
    with st.spinner("BGE-M3로 관련 문서를 검색 중..."):
        try:
            from src.retrieval.search import search_documents
            results = search_documents(
                query=query,
                top_k=top_k,
                source_types=source_types,
            )
        except FileNotFoundError:
            st.error(
                "인덱스 파일을 찾을 수 없습니다. "
                "`python -m src.retrieval.indexer --refresh` 를 먼저 실행하세요."
            )
            return
        except Exception as e:
            st.error(f"검색 오류: {e}")
            return

    if not results:
        st.info(
            "현재 저장된 공식 문서에서 관련 근거를 찾지 못했습니다.\n\n"
            "검색어를 바꾸거나 출처 필터를 넓혀보세요."
        )
        return

    st.success(f"총 {len(results)}개 관련 문단을 찾았습니다.")

    for r in results:
        source_icon = {
            "nasdaq_official": "📊",
            "sec_official": "🏛️",
            "company_ir": "🏢",
        }.get(r.source_type, "📄")

        with st.container(border=True):
            header_cols = st.columns([1, 6, 2])
            with header_cols[0]:
                st.markdown(f"### #{r.rank}")
                st.metric("유사도", f"{r.score:.4f}")
            with header_cols[1]:
                st.markdown(f"**{source_icon} {r.title}**")
                st.caption(f"섹션: {r.section}")
                if r.published_at:
                    st.caption(f"기준일: {r.published_at}")
            with header_cols[2]:
                st.markdown(f"`{r.source_type}`")
                if r.item_number:
                    st.caption(f"Item: {r.item_number}")

            # 원문 미리보기
            preview = r.text[:600]
            if len(r.text) > 600:
                preview += "..."
            st.markdown(f"```\n{preview}\n```")

            if r.source_url:
                st.markdown(f"[📎 원문 출처]({r.source_url})")

    st.caption(
        "⚠️ 이 검색 결과는 생성형 AI 답변이 아닙니다. "
        "질문과 관련된 공식 원문 문단을 유사도 순으로 표시한 것입니다. "
        "투자 추천이 아닙니다."
    )

