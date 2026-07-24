# Nasdaq Pulse MVP

NASDAQ 종목 분석을 시연하기 위한 제한적 MVP입니다. 완성형 금융 서비스, 투자 추천, 목표주가 제시, 편입·편출 예측 서비스가 아닙니다.

## 실행 방법

```bash
npm install
npm run dev
```

검증:

```bash
npm run lint
npm run typecheck
npm run build
```

기존 Python/Streamlit PoC 파일은 레포에 유지되어 있으며, 별도 실행이 필요하면 `streamlit run app.py`를 사용할 수 있습니다.

## 환경 변수

```bash
MCP_ENABLED=false
MCP_SERVER_URL=
MCP_MARKET_TOOL=
MCP_HISTORY_TOOL=
MCP_NEWS_TOOL=
OPENAI_API_KEY=
OPENAI_MODEL=
```

## MCP 연결 위치

- 서버 전용 adapter: `src/lib/mcp-client.ts`
- provider 선택 및 fallback 전환: `src/lib/providers.ts`
- 브라우저는 MCP 서버나 비밀키를 직접 호출하지 않고 Next.js Route Handler만 호출합니다.
- MCP 서버 이름과 tool 이름은 환경 변수로만 관리하며 특정 MCP 서버 구현에 결합하지 않습니다.

## Fallback 데이터 주의사항

- fallback 데이터는 실제 최신 시장 데이터가 아닙니다.
- MCP가 꺼져 있거나 실패하면 local fallback을 사용합니다.
- fallback 기본 지원 종목은 `IONQ`, `NVDA`, `MSFT`, `AAPL`, `GOOGL`입니다.
- IONQ는 1D 가격 포인트와 샘플 뉴스 3건으로 기본 화면을 시연할 수 있습니다.
- 준비되지 않은 기간은 다른 기간 데이터로 대체하지 않고 “해당 기간의 차트 데이터가 없습니다.”를 표시합니다.

## 지원 기능

- 상단 종목 검색
- 회사명, 티커, 현재가, 등락률, 기준 시각 표시
- `1D`, `5D`, `1M`, `3M`, `6M`, `YTD`, `1Y` 기간 선택
- Recharts 가격 라인 차트
- 관련 뉴스 최대 3건 및 외부 링크
- 현재 화면 데이터 기반 챗봇
- OpenAI API 실패 또는 미설정 시 규칙 기반 챗봇 fallback
- 모바일 세로 배치

## 제외 범위

- FastAPI, DB, LangGraph, LangChain, Neo4j, RAG
- 로그인, 알림, 설정, 실제 거래 기능
- 매수·매도 추천
- 목표주가 및 미래 가격 예측
- 데이터에 없는 사실이나 숫자 생성
