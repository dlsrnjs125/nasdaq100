# Nasdaq-100 편입·편출 관찰 후보 PoC & Prototype

공개 데이터(Nasdaq API, SEC EDGAR)를 기반으로 Nasdaq-100 편입·편출 **관찰 후보**를 계산하고 Streamlit으로 확인하는 PoC 및 Prototype입니다. 공식 편입·편출 예측이나 투자 추천 서비스가 아닙니다.

---

## 주요 기능

- PoC 결과 요약 (PASS / CONDITIONAL_PASS / FAIL)
- 편입 관찰 후보 Top 10
- 편출 관찰 후보 Top 10
- 데이터 품질 및 출처 확인
- AI 분석 기능 연결 예정 화면

---

## 프로젝트 구조

```
nasdaq100-candidate-poc/
├── app.py                        # Streamlit 진입점
├── ui/
│   ├── data_loader.py            # outputs/ 파일 로더
│   ├── components.py             # 재사용 UI 컴포넌트
│   └── pages.py                  # 4개 탭 페이지
├── src/
│   ├── pipeline.py               # PoC 파이프라인 오케스트레이터
│   ├── collectors/               # Nasdaq·SEC·시장 데이터 수집
│   ├── processing/               # 정규화·자격판정·순위산정
│   └── validation/               # 품질리포트·재현성검증
├── data/raw/                     # 수집 스냅숏 (재현성 기준)
├── data/processed/
│   └── candidate_universe.csv
├── outputs/
│   ├── inclusion_watch_top10.csv
│   ├── exclusion_watch_top10.csv
│   ├── data_quality_report.json
│   └── poc_result.json
├── tests/
├── run_poc.py                    # PoC CLI 진입점
└── requirements.txt
```

---

## 설치 및 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

기존 PoC 데이터가 이미 있는 경우:

```bash
streamlit run app.py
```

실제 데이터를 다시 수집하는 경우:

```bash
python run_poc.py --refresh
streamlit run app.py
```

테스트:

```bash
pytest -q
```

---

## 출력 파일

| 파일 | 위치 |
|------|------|
| 편입 관찰 후보 | `outputs/inclusion_watch_top10.csv` |
| 편출 관찰 후보 | `outputs/exclusion_watch_top10.csv` |
| 데이터 품질 리포트 | `outputs/data_quality_report.json` |
| PoC 결과 | `outputs/poc_result.json` |

---

## AI 기능 상태

- 현재 AI 모델 **미연결**
- 공식 문서 요약, 기업 사건 추출, 원문 인용 연결은 **추후 구현 예정**
- 가짜 AI 결과를 제공하지 않음

---

## 실제 데이터 출처

| 데이터 | 출처 | 유형 |
|--------|------|------|
| Nasdaq-100 구성 종목 | `api.nasdaq.com/api/quote/list-type/nasdaq100` | 공식 |
| Nasdaq 상장 기업 | `api.nasdaq.com/api/screener/stocks` | 공식 |
| SEC CIK 매핑 | `www.sec.gov/files/company_tickers.json` | 공식 |
| SEC 제출 이력 | `data.sec.gov/submissions/` | 공식 |
| 시장 데이터 보완 | yfinance | 보조 |

---

## 제한 사항

- 공식 Nasdaq 내부 순위(75·100·125위 기준)가 아님
- 공개 데이터 기반 관찰 후보
- **투자 추천이 아님**
- 일부 시장 데이터는 보조 출처에 의존할 수 있음
