import "server-only";

import type { NewsArticle, PricePoint, PriceRange, StockQuote } from "./types";

type ToolPayload = Record<string, unknown>;

async function callMcpTool(toolName: string | undefined, payload: ToolPayload) {
  if (process.env.MCP_ENABLED !== "true" || !process.env.MCP_SERVER_URL || !toolName) {
    return null;
  }

  const response = await fetch(process.env.MCP_SERVER_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({
      tool: toolName,
      arguments: payload
    }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`MCP request failed with ${response.status}`);
  }

  return response.json() as Promise<unknown>;
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function toNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function toStringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

export function mapQuote(raw: unknown, symbol: string): StockQuote | null {
  const item = asRecord(raw);
  const price = toNumber(item.price ?? item.currentPrice ?? item.last);
  const change = toNumber(item.change ?? item.priceChange) ?? 0;
  const changePercent = toNumber(item.changePercent ?? item.percentChange) ?? 0;
  if (price === null) {
    return null;
  }
  return {
    symbol,
    companyName: toStringValue(item.companyName ?? item.name) ?? symbol,
    price,
    change,
    changePercent,
    currency: "USD",
    asOf: toStringValue(item.asOf ?? item.timestamp) ?? new Date().toISOString()
  };
}

export function mapHistory(raw: unknown): PricePoint[] {
  const points = asRecord(raw).points;
  const rows: unknown[] = Array.isArray(raw) ? raw : Array.isArray(points) ? points : [];
  return rows
    .map((row) => {
      const item = asRecord(row);
      const price = toNumber(item.price ?? item.close ?? item.value);
      const time = toStringValue(item.time ?? item.date ?? item.timestamp);
      return price !== null && time ? { time, price } : null;
    })
    .filter((point): point is PricePoint => point !== null);
}

export function mapNews(raw: unknown): NewsArticle[] {
  const articles = asRecord(raw).articles;
  const rows: unknown[] = Array.isArray(raw) ? raw : Array.isArray(articles) ? articles : [];
  return rows
    .map((row, index) => {
      const item = asRecord(row);
      const title = toStringValue(item.title ?? item.headline);
      const url = toStringValue(item.url ?? item.link);
      if (!title || !url) {
        return null;
      }
      const article: NewsArticle = {
        id: toStringValue(item.id) ?? `mcp-${index}`,
        title,
        publisher: toStringValue(item.publisher ?? item.source) ?? "MCP",
        url,
        publishedAt: toStringValue(item.publishedAt ?? item.datetime ?? item.date) ?? new Date().toISOString()
      };
      const summary = toStringValue(item.summary ?? item.description);
      if (summary) {
        article.summary = summary;
      }
      return article;
    })
    .filter((article): article is NewsArticle => article !== null);
}

export async function getMcpQuote(symbol: string): Promise<StockQuote | null> {
  const raw = await callMcpTool(process.env.MCP_MARKET_TOOL, { symbol });
  return raw ? mapQuote(raw, symbol) : null;
}

export async function getMcpHistory(symbol: string, range: PriceRange): Promise<PricePoint[]> {
  const raw = await callMcpTool(process.env.MCP_HISTORY_TOOL, { symbol, range });
  return raw ? mapHistory(raw) : [];
}

export async function getMcpNews(symbol: string, limit: number): Promise<NewsArticle[]> {
  const raw = await callMcpTool(process.env.MCP_NEWS_TOOL, { symbol, limit });
  return raw ? mapNews(raw).slice(0, limit) : [];
}
