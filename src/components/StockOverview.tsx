import type { DataSource, StockQuote } from "@/lib/types";

function formatAsOf(asOf: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Seoul"
  }).format(new Date(asOf));
}

export function StockOverview({ quote, source }: { quote: StockQuote | null; source: DataSource }) {
  if (!quote) {
    return (
      <section className="rounded-lg border border-slate-800 bg-slate-800 p-5 shadow-sm">
        <p className="text-sm text-slate-400">선택한 종목의 가격 데이터가 없습니다.</p>
      </section>
    );
  }

  const positive = quote.changePercent >= 0;

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-800 p-5 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="font-mono text-sm text-blue-300">{quote.symbol}</p>
          <h2 className="mt-1 text-2xl font-bold text-slate-100">{quote.companyName}</h2>
          <p className="mt-2 text-xs text-slate-500">기준 시각 {formatAsOf(quote.asOf)}</p>
        </div>
        <div className="text-left md:text-right">
          <p className="font-mono text-3xl font-semibold tabular-nums text-slate-100">${quote.price.toFixed(2)}</p>
          <p className={`mt-1 font-mono text-sm tabular-nums ${positive ? "text-emerald-400" : "text-red-400"}`}>
            {positive ? "+" : ""}
            {quote.change.toFixed(2)} ({positive ? "+" : ""}
            {quote.changePercent.toFixed(2)}%)
          </p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
        <span className="rounded bg-slate-900 px-2 py-1">source: {source}</span>
        {source === "fallback" ? <span className="rounded bg-amber-950 px-2 py-1 text-amber-300">Fallback demo data. 실제 최신 데이터가 아닙니다.</span> : null}
      </div>
    </section>
  );
}
