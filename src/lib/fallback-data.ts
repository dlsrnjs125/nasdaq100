import type { NewsArticle, PricePoint, PriceRange, StockQuote } from "./types";

export const SUPPORTED_SYMBOLS = ["IONQ", "NVDA", "MSFT", "AAPL", "GOOGL"] as const;

type SupportedSymbol = (typeof SUPPORTED_SYMBOLS)[number];

const fallbackQuotes: Record<SupportedSymbol, StockQuote> = {
  IONQ: {
    symbol: "IONQ",
    companyName: "IonQ, Inc.",
    price: 22.45,
    change: -0.78,
    changePercent: -3.36,
    currency: "USD",
    asOf: "2025-07-24T15:59:00-04:00",
    sourceNote: "Fallback demo data. Not current market data."
  },
  NVDA: {
    symbol: "NVDA",
    companyName: "NVIDIA Corporation",
    price: 171.63,
    change: -0.88,
    changePercent: -0.51,
    currency: "USD",
    asOf: "2026-07-24T12:00:00-04:00",
    sourceNote: "Fallback demo data. Not current market data."
  },
  MSFT: {
    symbol: "MSFT",
    companyName: "Microsoft Corporation",
    price: 514.72,
    change: 2.16,
    changePercent: 0.42,
    currency: "USD",
    asOf: "2026-07-24T12:00:00-04:00",
    sourceNote: "Fallback demo data. Not current market data."
  },
  AAPL: {
    symbol: "AAPL",
    companyName: "Apple Inc.",
    price: 213.27,
    change: -1.07,
    changePercent: -0.5,
    currency: "USD",
    asOf: "2026-07-24T12:00:00-04:00",
    sourceNote: "Fallback demo data. Not current market data."
  },
  GOOGL: {
    symbol: "GOOGL",
    companyName: "Alphabet Inc.",
    price: 196.84,
    change: 0.91,
    changePercent: 0.46,
    currency: "USD",
    asOf: "2026-07-24T12:00:00-04:00",
    sourceNote: "Fallback demo data. Not current market data."
  }
};

const ionqOneDay: PricePoint[] = [
  { time: "09:30", price: 21.1 },
  { time: "10:00", price: 20.75 },
  { time: "10:30", price: 21.35 },
  { time: "11:00", price: 21.78 },
  { time: "11:30", price: 22.25 },
  { time: "12:00", price: 21.92 },
  { time: "12:30", price: 22.68 },
  { time: "13:00", price: 23.02 },
  { time: "13:30", price: 22.52 },
  { time: "14:00", price: 22.85 },
  { time: "14:30", price: 22.08 },
  { time: "15:00", price: 21.7 },
  { time: "15:30", price: 22.45 }
];

const fallbackHistory: Partial<Record<SupportedSymbol, Partial<Record<PriceRange, PricePoint[]>>>> = {
  IONQ: {
    "1D": ionqOneDay
  },
  NVDA: {
    "1D": [
      { time: "09:30", price: 172.51 },
      { time: "10:30", price: 171.84 },
      { time: "11:30", price: 170.96 },
      { time: "12:30", price: 171.42 },
      { time: "13:30", price: 171.63 }
    ]
  },
  MSFT: {
    "1D": [
      { time: "09:30", price: 512.56 },
      { time: "10:30", price: 513.08 },
      { time: "11:30", price: 514.28 },
      { time: "12:30", price: 514.05 },
      { time: "13:30", price: 514.72 }
    ]
  },
  AAPL: {
    "1D": [
      { time: "09:30", price: 214.34 },
      { time: "10:30", price: 214.02 },
      { time: "11:30", price: 213.76 },
      { time: "12:30", price: 213.41 },
      { time: "13:30", price: 213.27 }
    ]
  },
  GOOGL: {
    "1D": [
      { time: "09:30", price: 195.93 },
      { time: "10:30", price: 196.31 },
      { time: "11:30", price: 196.05 },
      { time: "12:30", price: 196.72 },
      { time: "13:30", price: 196.84 }
    ]
  }
};

const fallbackNews: Record<SupportedSymbol, NewsArticle[]> = {
  IONQ: [
    {
      id: "ionq-1",
      title: "IONQ, 차세대 양자컴퓨터 성능 공개... 산업용 활용 가속 기대",
      publisher: "Reuters",
      url: "https://www.ionq.com/news",
      publishedAt: "2025-07-22T14:00:00Z",
      summary: "Fallback demo article. 실제 최신 뉴스가 아닙니다."
    },
    {
      id: "ionq-2",
      title: "Microsoft, IONQ와의 파트너십 확대 발표",
      publisher: "Bloomberg",
      url: "https://www.ionq.com/news",
      publishedAt: "2025-07-21T15:30:00Z",
      summary: "Fallback news does not represent current reporting."
    },
    {
      id: "ionq-3",
      title: "IONQ, 2분기 실적 발표... 매출 성장과 손실 축소",
      publisher: "CNBC",
      url: "https://www.ionq.com/news",
      publishedAt: "2025-07-17T12:15:00Z",
      summary: "Used only to exercise news and chatbot flows."
    }
  ],
  NVDA: [],
  MSFT: [],
  AAPL: [],
  GOOGL: []
};

export function normalizeSymbol(symbol: string) {
  return symbol.trim().toUpperCase();
}

export function isSupportedSymbol(symbol: string): symbol is SupportedSymbol {
  return SUPPORTED_SYMBOLS.includes(symbol as SupportedSymbol);
}

export function getFallbackQuote(symbol: string): StockQuote | null {
  const normalized = normalizeSymbol(symbol);
  return isSupportedSymbol(normalized) ? fallbackQuotes[normalized] : null;
}

export function getFallbackHistory(symbol: string, range: PriceRange): PricePoint[] {
  const normalized = normalizeSymbol(symbol);
  if (!isSupportedSymbol(normalized)) {
    return [];
  }
  return fallbackHistory[normalized]?.[range] ?? [];
}

export function getFallbackNews(symbol: string, limit: number): NewsArticle[] {
  const normalized = normalizeSymbol(symbol);
  if (!isSupportedSymbol(normalized)) {
    return [];
  }
  return fallbackNews[normalized].slice(0, limit);
}
