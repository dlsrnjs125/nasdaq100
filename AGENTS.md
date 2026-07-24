# AGENTS.md

## Project Goal
공개 데이터(Nasdaq API, SEC EDGAR)를 기반으로 Nasdaq-100 편입·편출 **관찰 후보**를 계산하고 Streamlit으로 시각화하는 PoC 및 Prototype입니다.  
공식 Nasdaq 편입·편출 예측 또는 투자 추천 서비스가 **아닙니다**.

## Architecture

```
PoC (src/)
├── 데이터 수집: nasdaq_collector, sec_collector, market_collector
├── 정규화: normalize.py
├── 자격 판정: eligibility.py
├── 순위 산정: rank_candidates.py
└── 검증: data_quality.py, reproducibility.py

Retrieval (src/retrieval/)
├── config.py          — 모델명, 경로, 청킹 파라미터
├── schemas.py         — DocumentChunk, SearchResult 데이터 타입
├── embedding_model.py — BAAI/bge-m3 로더 (MPS→CPU fallback)
├── document_loader.py — TXT 문서 + raw JSON → DocumentChunk
├── chunker.py         — 텍스트 분할 및 임베딩 입력 생성
├── indexer.py         — 인덱스 생성 진입점
└── search.py          — 코사인 유사도 검색 + CLI

Streamlit Prototype (ui/ + app.py)
├── data_loader.py  — outputs/ 파일 읽기만 담당
├── components.py   — 재사용 가능한 UI 컴포넌트
├── pages.py        — 4개 탭 (Overview / 편입 / 편출 / 문서검색+AI예정)
└── app.py          — 진입점 + 사이드바

문서 (data/documents/)
├── nasdaq100_methodology.txt   — Nasdaq-100 공식 방법론
└── sec_reporting_requirements.txt — SEC EDGAR 보고 요건
```

## Retrieval AI (BGE-M3)

- **Model**: `BAAI/bge-m3` (Hugging Face 캐시 사용, Git 미포함)
- **Purpose**: 공식 문서 의미 검색 및 인용 후보 탐색
- **Device**: MPS (Apple Silicon) → CUDA → CPU 순서 자동 선택
- **Not Used For**: 답변 생성, 투자 추천, 편입 사유 생성, 자동 요약

## Retrieval Rules
- 공식 자료(`nasdaq_official`, `sec_official`)를 기본 인덱스로 사용
- 출처 URL과 원문 메타데이터 유지 필수
- 임의의 문서·인용 생성 **금지**
- 검색 결과를 공식 확정 결론으로 표현 **금지**
- 인덱스는 입력 문서 변경 시에만 재생성 (`--refresh`)
- 모델 파일과 `.npy` 임베딩을 Git에 저장하지 않음

## Development Rules
- 가짜 데이터 또는 하드코딩된 기업 데이터 생성 **금지**
- 기존 PoC 계산 로직을 Streamlit 코드에 **복사·중복 구현 금지**
- 기존 `outputs/` 결과만 읽어 시각화
- 데이터 출처와 기준일 항상 표시
- 결측값 임의 보간 **금지**
- 공식 사실과 AI 분석 역할 분리
- 투자 추천 표현 **금지** (매수, 매도, 목표주가, 편입 확률 등)
- 기존 PoC 실행과 pytest를 깨뜨리지 않음

## Commands

```bash
# 설치
pip install -r requirements.txt

# PoC 데이터 수집
python run_poc.py --refresh

# BGE-M3 인덱스 생성
python -m src.retrieval.indexer --refresh

# CLI 검색
python -m src.retrieval.search --query "Nasdaq-100 편출 기준은 무엇인가?" --top-k 3

# Streamlit 실행
streamlit run app.py

# 테스트 (모델 없이)
pytest -q

# 모델 smoke test (모델 다운로드 필요)
RUN_MODEL_TESTS=1 pytest -q -m model
```

## Definition of Done
- 기존 `outputs/` 파일로 앱 정상 실행
- Overview / 편입 후보 / 편출 후보 / 문서 검색+AI 예정 4개 탭 확인
- BGE-M3 인덱스 생성 및 CLI 검색 동작 확인
- Streamlit 검색 탭에서 실제 결과 표시 확인
- AI 예정 화면에서 실제 AI 호출 없음
- pytest 전체 통과
- README 명령과 실제 실행 일치
