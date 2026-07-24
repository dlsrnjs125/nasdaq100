import { NextResponse } from "next/server";

import { isSupportedSymbol, normalizeSymbol } from "@/lib/fallback-data";
import { getNewsData } from "@/lib/providers";

export async function GET(request: Request, context: { params: { symbol: string } }) {
  const symbol = normalizeSymbol(context.params.symbol);
  const requestedLimit = Number(new URL(request.url).searchParams.get("limit") ?? 3);
  const limit = Number.isFinite(requestedLimit) ? Math.min(Math.max(requestedLimit, 1), 3) : 3;

  if (!isSupportedSymbol(symbol)) {
    return NextResponse.json(
      {
        source: "unavailable",
        articles: [],
        message: "MVP 지원 종목은 IONQ, NVDA, MSFT, AAPL, GOOGL입니다."
      },
      { status: 404 }
    );
  }

  return NextResponse.json(await getNewsData(symbol, limit));
}
