"use client";

import { useCallback, useEffect, useState } from "react";

import { ChatPanel } from "@/components/ChatPanel";
import { NewsList } from "@/components/NewsList";
import { StockChart } from "@/components/StockChart";
import { StockSearch } from "@/components/StockSearch";
import type { DataSource, MarketResponse, NewsArticle, NewsResponse, PricePoint, PriceRange, StockQuote } from "@/lib/types";

export default function Home() {
  const [symbol, setSymbol] = useState("IONQ");
  const [range, setRange] = useState<PriceRange>("1D");
  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [history, setHistory] = useState<PricePoint[]>([]);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [marketSource, setMarketSource] = useState<DataSource>("unavailable");
  const [newsSource, setNewsSource] = useState<DataSource>("unavailable");
  const [loadingMarket, setLoadingMarket] = useState(true);
  const [loadingNews, setLoadingNews] = useState(true);
  const [message, setMessage] = useState("초기 로딩 중입니다.");
  const [error, setError] = useState("");

  const loadMarket = useCallback(async (nextSymbol: string, nextRange: PriceRange) => {
    setLoadingMarket(true);
    setError("");
    try {
      const response = await fetch(`/api/market/${encodeURIComponent(nextSymbol)}?range=${nextRange}`, {
        cache: "no-store"
      });
      const payload = (await response.json()) as MarketResponse;
      setQuote(payload.quote);
      setHistory(payload.history);
      setMarketSource(payload.source);
      setMessage(payload.message ?? "");
      if (!response.ok) {
        setError(payload.message ?? "가격 데이터를 조회할 수 없습니다.");
      }
    } catch {
      setQuote(null);
      setHistory([]);
      setMarketSource("unavailable");
      setError("가격 데이터 조회 중 오류가 발생했습니다.");
    } finally {
      setLoadingMarket(false);
    }
  }, []);

  const loadNews = useCallback(async (nextSymbol: string) => {
    setLoadingNews(true);
    try {
      const response = await fetch(`/api/news/${encodeURIComponent(nextSymbol)}?limit=3`, {
        cache: "no-store"
      });
      const payload = (await response.json()) as NewsResponse;
      setNews(payload.articles);
      setNewsSource(payload.source);
    } catch {
      setNews([]);
      setNewsSource("unavailable");
    } finally {
      setLoadingNews(false);
    }
  }, []);

  useEffect(() => {
    void loadMarket(symbol, range);
  }, [symbol, range, loadMarket]);

  useEffect(() => {
    void loadNews(symbol);
  }, [symbol, loadNews]);

  function handleSubmit(nextSymbol: string) {
    const normalized = nextSymbol.trim().toUpperCase();
    if (!normalized) {
      setError("티커를 입력하세요.");
      return;
    }
    setSymbol(normalized);
    setRange("1D");
    setMessage("검색 중입니다.");
  }

  return (
    <div className="min-h-screen bg-[#f8f9ff] text-[#121c2a]">
      <aside className="fixed left-0 top-0 z-50 hidden h-screen w-64 flex-col border-r border-[#bfc9c3] bg-[#e6eeff] px-4 py-8 md:flex">
        <div className="mb-10 px-2">
          <h1 className="text-2xl font-black text-[#003527]">터미널 알파</h1>
          <p className="text-xs font-bold tracking-wide text-[#404944]">인증 소스 모드</p>
        </div>
        <nav className="flex-1 space-y-2">
          {[
            ["account_tree", "파이프라인"],
            ["monitoring", "시장 데이터"]
          ].map(([icon, label]) => (
            <button
              key={label}
              type="button"
              disabled
              className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-semibold text-[#404944] opacity-80"
            >
              <span className="material-symbols-outlined">{icon}</span>
              {label}
            </button>
          ))}
          <div className="flex scale-95 items-center gap-3 rounded-lg border-r-4 border-[#003527] bg-[#dde1d5] px-4 py-3 text-sm font-bold text-[#003527]">
            <span className="material-symbols-outlined">analytics</span>
            분석 도구
          </div>
        </nav>
        <div className="mt-auto space-y-2 border-t border-[#bfc9c3] pt-6">
          <button type="button" disabled className="mb-6 w-full rounded-xl bg-[#003527] py-3 text-sm font-bold text-white">
            새 분석 시작
          </button>
          <div className="flex items-center gap-3 px-4 py-2 text-sm font-semibold text-[#404944]">
            <span className="material-symbols-outlined">help</span>
            고객 지원
          </div>
          <div className="flex items-center gap-3 px-4 py-2 text-sm font-semibold text-[#404944]">
            <span className="material-symbols-outlined">logout</span>
            로그아웃
          </div>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col md:ml-64">
        <header className="flex h-16 items-center justify-between border-b border-[#bfc9c3] bg-[#f8f9ff] px-4 md:px-10">
          <div className="flex items-center gap-4">
            <span className="text-2xl font-bold text-[#003527]">NASDAQ Pulse</span>
            <StockSearch value={symbol} loading={loadingMarket || loadingNews} onSubmit={handleSubmit} />
          </div>
          <div className="flex items-center gap-4 text-[#404944]">
            <button type="button" disabled className="hidden p-2 md:block">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button type="button" disabled className="hidden p-2 md:block">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <div className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full border border-[#bfc9c3] bg-[#d9e3f6] text-sm font-black text-[#003527]">
              HI
            </div>
          </div>
        </header>

        <main className="mx-auto grid w-full max-w-[1440px] flex-1 grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-12 lg:px-10 lg:py-10">
          <div className="flex flex-col gap-8 lg:col-span-8">
          {(message || error) && (
            <div
              className={`rounded-xl border px-4 py-3 text-sm ${
                error
                  ? "border-[#ffdad6] bg-[#ffdad6] text-[#93000a]"
                  : marketSource === "fallback" || newsSource === "fallback"
                    ? "border-[#dde1d5] bg-[#e6eeff] text-[#404944]"
                    : "border-[#bfc9c3] bg-white text-[#404944]"
              }`}
            >
              {error || message}
            </div>
          )}
          <StockChart
            data={history}
            range={range}
            loading={loadingMarket}
            onRangeChange={setRange}
            quote={quote}
            source={marketSource}
          />
          <NewsList articles={news} source={newsSource} loading={loadingNews} />
        </div>
          <div className="lg:col-span-4">
            <ChatPanel symbol={symbol} quote={quote} history={history} news={news} />
          </div>
        </main>

        <footer className="border-t border-[#bfc9c3] bg-[#eff4ff] px-4 py-8 md:px-10">
          <div className="mx-auto flex max-w-[1440px] flex-col items-center justify-between gap-4 text-xs font-bold text-[#404944] md:flex-row">
            <p>© 2024 NASDAQ Pulse Terminal. 모든 데이터는 실시간으로 검증됩니다.</p>
            <div className="flex items-center gap-6">
              <span>개인정보처리방침</span>
              <span>데이터 신뢰 규정</span>
              <span>문의하기</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
