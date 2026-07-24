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
      className="hidden items-center rounded-full bg-[#e6eeff] px-4 py-1.5 lg:flex"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        onSubmit(String(formData.get("symbol") ?? ""));
      }}
    >
      <span className="material-symbols-outlined mr-2 text-sm text-[#707974]">search</span>
      <input
        key={value}
        name="symbol"
        defaultValue={value}
        placeholder="종목 또는 데이터 검색..."
        className="w-64 border-none bg-transparent px-2 py-1 text-sm font-semibold uppercase text-[#121c2a] outline-none placeholder:text-[#bfc9c3] focus:ring-0"
        list="symbols"
        aria-label="종목 티커 검색"
      />
      <datalist id="symbols">
        {SUPPORTED_SYMBOLS.map((symbol) => (
          <option key={symbol} value={symbol} />
        ))}
      </datalist>
      <button type="submit" disabled={loading} className="sr-only">
        {loading ? "검색 중" : "검색"}
      </button>
    </form>
  );
}
