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
    role: "user",
    content: "IONQ의 최근 주가 흐름은 어때?"
  },
  {
    role: "assistant",
    content:
      "IONQ는 오늘 -3.36% 하락한 22.45 USD로 마감했어요. 장중 상승 구간이 있었지만, 오후 들어 하락세로 전환되었습니다."
  },
  {
    role: "user",
    content: "IONQ의 주요 최근 뉴스는 뭐가 있어?"
  },
  {
    role: "assistant",
    content:
      "IONQ의 최근 주요 뉴스는 다음과 같아요:\n• 차세대 양자컴퓨터 성능 발표\n• Microsoft와 파트너십 확대\n• 2분기 실적 발표"
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
    <aside className="flex min-h-[620px] flex-col overflow-hidden rounded-xl border border-[#bfc9c3] bg-white shadow-sm lg:h-full">
      <div className="flex items-center justify-between border-b border-[#bfc9c3] bg-[#eff4ff]/50 p-6">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full bg-black text-sm font-black text-[#95d3ba]">
              AI
            </div>
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-[#003527]" />
          </div>
          <div>
            <h4 className="text-lg font-bold text-[#003527]">황인권</h4>
          </div>
        </div>
        <button
          type="button"
          onClick={() => {
            setMessages(initialMessages);
            setError("");
          }}
          className="p-2 text-[#404944] transition-colors hover:text-[#003527]"
          aria-label="대화 초기화"
        >
          <span className="material-symbols-outlined">refresh</span>
        </button>
      </div>
      <div className="flex-1 space-y-6 overflow-y-auto bg-[#e6eeff]/10 p-6">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
          >
            {message.role === "assistant" ? (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#dde1d5] text-[#003527]">
                <span className="material-symbols-outlined text-[16px]">smart_toy</span>
              </div>
            ) : null}
            <div
              className={`max-w-[85%] whitespace-pre-line p-4 text-sm leading-6 shadow-sm ${
                message.role === "user"
                  ? "rounded-2xl rounded-tr-none bg-[#003527] text-white"
                  : "rounded-2xl rounded-tl-none border border-[#bfc9c3]/30 bg-[#d9e3f6] text-[#121c2a]"
              }`}
            >
              <p>{message.content}</p>
              <span className={`mt-2 block text-[10px] ${message.role === "user" ? "text-right text-white/60" : "text-[#404944]"}`}>
                {index < 2 ? "15:44" : "15:45"}
              </span>
            </div>
          </div>
        ))}
        {loading ? (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#dde1d5] text-[#003527]">
              <span className="material-symbols-outlined text-[16px]">smart_toy</span>
            </div>
            <div className="rounded-2xl rounded-tl-none border border-[#bfc9c3]/30 bg-[#d9e3f6] p-4 text-sm font-semibold text-[#404944]">
              응답 생성 중
            </div>
          </div>
        ) : null}
      </div>
      <div className="border-t border-[#bfc9c3] bg-[#f8f9ff] p-6">
        {error ? <p className="mb-2 text-xs font-bold text-[#ba1a1a]">{error}</p> : null}
        <div className="relative flex items-center">
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void sendMessage();
              }
            }}
            placeholder="메시지를 입력하세요..."
            rows={1}
            className="min-h-[48px] w-full resize-none rounded-xl border-none bg-[#e6eeff] py-3 pl-4 pr-14 text-sm text-[#121c2a] outline-none placeholder:text-[#707974] focus:ring-2 focus:ring-[#003527]"
          />
          <button
            type="button"
            onClick={() => void sendMessage()}
            disabled={loading}
            className="absolute right-2 rounded-lg bg-[#003527] p-2 text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            aria-label="메시지 전송"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
