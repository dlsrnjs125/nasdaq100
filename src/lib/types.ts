export type PriceRange = "1D" | "5D" | "1M" | "3M" | "6M" | "YTD" | "1Y";

export type DataSource = "mcp" | "fallback" | "unavailable";

export type StockQuote = {
  symbol: string;
  companyName: string;
  price: number;
  change: number;
  changePercent: number;
  currency: "USD";
  asOf: string;
  sourceNote?: string;
};

export type PricePoint = {
  time: string;
  price: number;
};

export type NewsArticle = {
  id: string;
  title: string;
  publisher: string;
  url: string;
  publishedAt: string;
  summary?: string;
};

export type MarketResponse = {
  source: DataSource;
  quote: StockQuote | null;
  history: PricePoint[];
  message?: string;
};

export type NewsResponse = {
  source: DataSource;
  articles: NewsArticle[];
  message?: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatRequest = {
  symbol: string;
  quote: StockQuote | null;
  history: PricePoint[];
  news: NewsArticle[];
  messages: ChatMessage[];
};

export type ChatResponse = {
  source: "openai" | "rules" | "unavailable";
  message: ChatMessage;
};

export interface MarketProvider {
  getQuote(symbol: string): Promise<StockQuote | null>;
  getHistory(symbol: string, range: PriceRange): Promise<PricePoint[]>;
}

export interface NewsProvider {
  getNews(symbol: string, limit: number): Promise<NewsArticle[]>;
}
