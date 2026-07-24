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

const ranges: PriceRange[] = ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y"];

type Props = {
  data: PricePoint[];
  range: PriceRange;
  loading: boolean;
  onRangeChange: (range: PriceRange) => void;
};

export function StockChart({ data, range, loading, onRangeChange }: Props) {
  return (
    <section className="rounded-lg border border-slate-800 bg-slate-800 p-5 shadow-sm">
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-100">가격 라인 차트</h2>
          <p className="text-xs text-slate-500">기간 변경 시 market API를 다시 호출합니다.</p>
        </div>
        <div className="flex flex-wrap gap-1">
          {ranges.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => onRangeChange(item)}
              className={`h-8 rounded-md px-3 font-mono text-xs ${
                item === range ? "bg-blue-500 text-white" : "bg-slate-900 text-slate-400 hover:text-slate-100"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="h-80 rounded-md border border-slate-700 bg-slate-950 p-2">
        {loading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">가격 데이터 로딩 중</div>
        ) : data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
            해당 기간의 차트 데이터가 없습니다.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 16, right: 20, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#1E293B" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: "#94A3B8", fontSize: 12 }} stroke="#334155" />
              <YAxis
                domain={["dataMin - 1", "dataMax + 1"]}
                tick={{ fill: "#94A3B8", fontSize: 12 }}
                stroke="#334155"
                tickFormatter={(value: number) => `$${value.toFixed(0)}`}
              />
              <Tooltip
                contentStyle={{ background: "#0F172A", border: "1px solid #334155", borderRadius: 6 }}
                labelStyle={{ color: "#F1F5F9" }}
                formatter={(value: number) => [`$${value.toFixed(2)}`, "price"]}
              />
              <Line type="monotone" dataKey="price" stroke="#3B82F6" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
