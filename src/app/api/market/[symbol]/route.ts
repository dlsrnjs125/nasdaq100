import { NextResponse } from "next/server";

import { isSupportedSymbol, normalizeSymbol } from "@/lib/fallback-data";
import { getMarketData } from "@/lib/providers";
import type { PriceRange } from "@/lib/types";

const ranges: PriceRange[] = ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y"];

export async function GET(request: Request, context: { params: { symbol: string } }) {
  const symbol = normalizeSymbol(context.params.symbol);
  const rangeParam = new URL(request.url).searchParams.get("range") ?? "1D";
  const range = ranges.includes(rangeParam as PriceRange) ? (rangeParam as PriceRange) : "1D";

  if (!isSupportedSymbol(symbol)) {
    return NextResponse.json(
      {
        source: "unavailable",
        quote: null,
        history: [],
        message: "MVP 지원 종목은 IONQ, NVDA, MSFT, AAPL, GOOGL입니다."
      },
      { status: 404 }
    );
  }

  return NextResponse.json(await getMarketData(symbol, range));
}
