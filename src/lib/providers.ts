import "server-only";

import { getFallbackHistory, getFallbackNews, getFallbackQuote, normalizeSymbol } from "./fallback-data";
import { getMcpHistory, getMcpNews, getMcpQuote } from "./mcp-client";
import type { DataSource, MarketProvider, NewsProvider, PriceRange } from "./types";

class McpMarketProvider implements MarketProvider {
  async getQuote(symbol: string) {
    return getMcpQuote(normalizeSymbol(symbol));
  }

  async getHistory(symbol: string, range: PriceRange) {
    return getMcpHistory(normalizeSymbol(symbol), range);
  }
}

class FallbackMarketProvider implements MarketProvider {
  async getQuote(symbol: string) {
    return getFallbackQuote(symbol);
  }

  async getHistory(symbol: string, range: PriceRange) {
    return getFallbackHistory(symbol, range);
  }
}

class McpNewsProvider implements NewsProvider {
  async getNews(symbol: string, limit: number) {
    return getMcpNews(normalizeSymbol(symbol), limit);
  }
}

class FallbackNewsProvider implements NewsProvider {
  async getNews(symbol: string, limit: number) {
    return getFallbackNews(symbol, limit);
  }
}

export async function getMarketData(symbol: string, range: PriceRange) {
  const normalized = normalizeSymbol(symbol);
  if (process.env.MCP_ENABLED === "true") {
    try {
      const provider = new McpMarketProvider();
      const [quote, history] = await Promise.all([
        provider.getQuote(normalized),
        provider.getHistory(normalized, range)
      ]);
      if (quote || history.length > 0) {
        return { source: "mcp" as DataSource, quote, history };
      }
    } catch (error) {
      console.error("MCP market provider failed", error);
    }
  }

  const fallback = new FallbackMarketProvider();
  const [quote, history] = await Promise.all([fallback.getQuote(normalized), fallback.getHistory(normalized, range)]);
  return {
    source: quote || history.length > 0 ? ("fallback" as DataSource) : ("unavailable" as DataSource),
    quote,
    history,
    message:
      quote || history.length > 0
        ? "MCP 미설정 또는 실패로 fallback demo data를 사용했습니다."
        : "지원하지 않는 티커이거나 사용 가능한 데이터가 없습니다."
  };
}

export async function getNewsData(symbol: string, limit: number) {
  const normalized = normalizeSymbol(symbol);
  if (process.env.MCP_ENABLED === "true") {
    try {
      const provider = new McpNewsProvider();
      const articles = await provider.getNews(normalized, limit);
      if (articles.length > 0) {
        return { source: "mcp" as DataSource, articles };
      }
    } catch (error) {
      console.error("MCP news provider failed", error);
    }
  }

  const provider = new FallbackNewsProvider();
  const articles = await provider.getNews(normalized, limit);
  return {
    source: articles.length > 0 ? ("fallback" as DataSource) : ("unavailable" as DataSource),
    articles,
    message:
      articles.length > 0
        ? "MCP 미설정 또는 실패로 fallback demo news를 사용했습니다."
        : "표시할 뉴스가 없습니다."
  };
}
