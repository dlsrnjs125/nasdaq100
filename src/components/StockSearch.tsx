"use client";

import { SUPPORTED_SYMBOLS } from "@/lib/fallback-data";

type Props = {
  value: string;
  loading: boolean;
  onSubmit: (symbol: string) => void;
};

export function StockSearch({ value, loading, onSubmit }: Props) {
  return (
    <form
      className="flex flex-col gap-3 border-b border-slate-800 bg-slate-900/80 px-4 py-4 backdrop-blur md:flex-row md:items-center md:justify-between md:px-8"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        onSubmit(String(formData.get("symbol") ?? ""));
      }}
    >
      <div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">NASDAQ PULSE MVP</p>
        <h1 className="text-xl font-semibold text-slate-100">종목 분석 대시보드</h1>
      </div>
      <div className="flex w-full gap-2 md:w-auto">
        <input
          key={value}
          name="symbol"
          defaultValue={value}
          placeholder="IONQ"
          className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm uppercase text-slate-100 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 md:w-72"
          list="symbols"
          aria-label="종목 티커 검색"
        />
        <datalist id="symbols">
          {SUPPORTED_SYMBOLS.map((symbol) => (
            <option key={symbol} value={symbol} />
          ))}
        </datalist>
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {loading ? "검색 중" : "검색"}
        </button>
      </div>
    </form>
  );
}
