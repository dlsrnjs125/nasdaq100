"use client";

import { useState } from "react";

import type { ChatMessage, ChatResponse, NewsArticle, PricePoint, StockQuote } from "@/lib/types";

type Props = {
  symbol: string;
  quote: StockQuote | null;
  history: PricePoint[];
  news: NewsArticle[];
};

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content: "현재 화면의 가격 데이터와 뉴스만 근거로 답변합니다. 매수·매도 추천과 미래 가격 예측은 제공하지 않습니다."
  }
];

export function ChatPanel({ symbol, quote, history, news }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage() {
    const content = draft.trim();
    if (!content || loading) {
      setError(content ? "" : "빈 메시지는 전송할 수 없습니다.");
      return;
    }

    const nextMessages: ChatMessage[] = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    setDraft("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ symbol, quote, history, news, messages: nextMessages })
      });
      const payload = (await response.json()) as ChatResponse;
      if (!response.ok) {
        throw new Error(payload.message.content);
      }
      setMessages((current) => [...current, payload.message]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "챗봇 응답 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <aside className="flex min-h-[620px] flex-col rounded-lg border border-slate-800 bg-slate-800 shadow-sm">
      <div className="border-b border-slate-700 p-5">
        <h2 className="text-base font-semibold text-slate-100">AI Q&A</h2>
        <p className="mt-1 text-xs text-slate-500">화면 데이터 기반 제한 답변</p>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-5">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded-md px-3 py-2 text-sm leading-6 ${
              message.role === "user" ? "ml-8 bg-blue-500 text-white" : "mr-8 bg-slate-900 text-slate-300"
            }`}
          >
            {message.content}
          </div>
        ))}
        {loading ? <div className="mr-8 rounded-md bg-slate-900 px-3 py-2 text-sm text-slate-400">응답 생성 중</div> : null}
      </div>
      <div className="border-t border-slate-700 p-4">
        {error ? <p className="mb-2 text-xs text-red-400">{error}</p> : null}
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void sendMessage();
            }
          }}
          placeholder="현재 가격, 등락률, 최근 뉴스 등을 질문"
          className="h-24 w-full resize-none rounded-md border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
        />
        <div className="mt-3 flex gap-2">
          <button
            type="button"
            onClick={() => void sendMessage()}
            disabled={loading}
            className="flex-1 rounded-md bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-400"
          >
            전송
          </button>
          <button
            type="button"
            onClick={() => {
              setMessages(initialMessages);
              setError("");
            }}
            className="rounded-md border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300 hover:border-blue-500 hover:text-blue-300"
          >
            초기화
          </button>
        </div>
      </div>
    </aside>
  );
}
