"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

import type { PricePoint, PriceRange } from "@/lib/types";
import type { DataSource, StockQuote } from "@/lib/types";

const ranges: PriceRange[] = ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y"];
const disabledRanges = ["5Y", "Max"];

type Props = {
  data: PricePoint[];
  range: PriceRange;
  loading: boolean;
  onRangeChange: (range: PriceRange) => void;
  quote: StockQuote | null;
  source: DataSource;
};

function formatAsOf(asOf: string) {
  const date = new Date(asOf);
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "America/New_York",
    hour12: false
  })
    .format(date)
    .replace(/\. /g, ".")
    .replace(".", ".")
    .replace(",", "");
}

export function StockChart({ data, range, loading, onRangeChange, quote, source }: Props) {
  const positive = (quote?.changePercent ?? 0) >= 0;

  return (
    <section className="rounded-[28px] border border-[#bfc9c3]/30 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-0.5 hover:shadow-md md:p-8">
      <div className="flex flex-col gap-8 md:flex-row">
        <div className="w-full md:w-1/3">
          {quote ? (
            <>
              <div className="mb-4 flex items-baseline gap-2">
                <h2 className="text-xl font-bold text-[#003527]">{quote.companyName}</h2>
                <span className="text-sm font-semibold text-[#404944]">{quote.symbol}</span>
              </div>
              <div className="mb-6">
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold leading-tight tracking-tight text-[#121c2a]">
                    {quote.price.toFixed(2)}
                  </span>
                  <span className="text-sm font-bold text-[#404944]">USD</span>
                </div>
                <div className={`mt-1 flex items-center gap-2 font-bold ${positive ? "text-[#2b6954]" : "text-[#ba1a1a]"}`}>
                  <span className="material-symbols-outlined text-sm">
                    {positive ? "arrow_upward" : "arrow_downward"}
                  </span>
                  <span>
                    {positive ? "+" : ""}
                    {quote.change.toFixed(2)} ({positive ? "+" : ""}
                    {quote.changePercent.toFixed(2)}%)
                  </span>
                </div>
                <p className="mt-1 text-xs font-semibold text-[#404944]">{formatAsOf(quote.asOf)} ET</p>
              </div>
            </>
          ) : (
            <div className="mb-6 rounded-xl bg-[#eff4ff] p-4 text-sm font-semibold text-[#404944]">
              선택한 종목의 가격 데이터가 없습니다.
            </div>
          )}
          <div className="grid grid-cols-4 gap-2">
            {ranges.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => onRangeChange(item)}
                className={`rounded-lg px-2 py-1.5 text-xs font-bold ${
                  item === range ? "bg-[#003527] text-white" : "bg-[#e6eeff] text-[#404944] hover:bg-[#dde1d5]"
                }`}
              >
                {item}
              </button>
            ))}
            {disabledRanges.map((item, index) => (
              <button
                key={item}
                type="button"
                disabled
                className={`${index === 1 ? "col-span-2" : ""} rounded-lg bg-[#e6eeff] px-2 py-1.5 text-xs font-bold text-[#404944] opacity-80`}
              >
                {item}
              </button>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-2 text-xs font-bold text-[#404944]">
            <span className="rounded-lg bg-[#eff4ff] px-2 py-1">source: {source}</span>
            {source === "fallback" ? (
              <span className="rounded-lg bg-[#dde1d5] px-2 py-1 text-[#003527]">실제 최신 데이터가 아닙니다.</span>
            ) : null}
          </div>
        </div>
        <div className="h-64 flex-1 md:h-[240px]">
          {loading ? (
            <div className="flex h-full items-center justify-center text-sm font-semibold text-[#404944]">
              가격 데이터 로딩 중
            </div>
          ) : data.length === 0 ? (
            <div className="flex h-full items-center justify-center rounded-xl bg-[#eff4ff] text-sm font-semibold text-[#404944]">
              해당 기간의 차트 데이터가 없습니다.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 16, right: 20, bottom: 22, left: 0 }}>
                <CartesianGrid stroke="#E5E7EB" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="time" tick={{ fill: "#404944", fontSize: 10 }} stroke="transparent" tickLine={false} />
                <YAxis
                  domain={["dataMin - 1", "dataMax + 1"]}
                  tick={{ fill: "#404944", fontSize: 10 }}
                  stroke="transparent"
                  tickLine={false}
                  width={42}
                  tickFormatter={(value: number) => value.toFixed(2)}
                />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #bfc9c3", borderRadius: 12 }}
                  labelStyle={{ color: "#121c2a", fontWeight: 700 }}
                  formatter={(value: number) => [`${value.toFixed(2)} USD`, "price"]}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#2b6954"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 4, fill: "#2b6954" }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </section>
  );
}
