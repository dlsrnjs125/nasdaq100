"use client";

import { useCallback, useEffect, useState } from "react";

import { ChatPanel } from "@/components/ChatPanel";
import { NewsList } from "@/components/NewsList";
import { StockChart } from "@/components/StockChart";
import { StockOverview } from "@/components/StockOverview";
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
    <main className="min-h-screen bg-slate-900 text-slate-100">
      <StockSearch value={symbol} loading={loadingMarket || loadingNews} onSubmit={handleSubmit} />
      <div className="mx-auto grid max-w-7xl gap-5 px-4 py-5 lg:grid-cols-[minmax(0,1fr)_400px] lg:px-8">
        <div className="space-y-5">
          {(message || error) && (
            <div
              className={`rounded-md border px-4 py-3 text-sm ${
                error
                  ? "border-red-900 bg-red-950/50 text-red-200"
                  : marketSource === "fallback" || newsSource === "fallback"
                    ? "border-amber-900 bg-amber-950/50 text-amber-200"
                    : "border-slate-800 bg-slate-800 text-slate-300"
              }`}
            >
              {error || message}
            </div>
          )}
          <StockOverview quote={quote} source={marketSource} />
          <StockChart data={history} range={range} loading={loadingMarket} onRangeChange={setRange} />
          <NewsList articles={news} source={newsSource} loading={loadingNews} />
        </div>
        <ChatPanel symbol={symbol} quote={quote} history={history} news={news} />
      </div>
    </main>
  );
}
