import "server-only";

import type { ChatMessage, ChatRequest, ChatResponse, NewsArticle, PricePoint, StockQuote } from "./types";

function formatCurrency(value: number) {
  return `$${value.toFixed(2)}`;
}

function describeTrend(history: PricePoint[]) {
  if (history.length < 2) {
    return "해당 기간의 가격 흐름을 판단할 차트 데이터가 부족합니다.";
  }
  const first = history[0].price;
  const last = history[history.length - 1].price;
  const delta = last - first;
  const direction = delta > 0 ? "상승" : delta < 0 ? "하락" : "보합";
  return `화면의 가격 데이터 기준으로 ${history[0].time} ${formatCurrency(first)}에서 ${history[history.length - 1].time} ${formatCurrency(last)}로 ${direction}했습니다.`;
}

function highLow(history: PricePoint[]) {
  if (history.length === 0) {
    return "해당 기간의 최고가와 최저가를 계산할 차트 데이터가 없습니다.";
  }
  const high = history.reduce((max, point) => (point.price > max.price ? point : max), history[0]);
  const low = history.reduce((min, point) => (point.price < min.price ? point : min), history[0]);
  return `화면의 가격 데이터 기준 최고가는 ${high.time} ${formatCurrency(high.price)}, 최저가는 ${low.time} ${formatCurrency(low.price)}입니다.`;
}

function newsSummary(news: NewsArticle[]) {
  if (news.length === 0) {
    return "현재 화면에 표시된 뉴스가 없습니다.";
  }
  return `최근 주요 뉴스는 ${news.map((article) => `「${article.title}」(${article.publisher})`).join(", ")}입니다.`;
}

export function answerWithRules(request: ChatRequest): string {
  const question = request.messages[request.messages.length - 1]?.content.toLowerCase() ?? "";
  const quote = request.quote;
  const history = request.history;
  const news = request.news;

  if (!quote) {
    return "현재 선택된 종목의 quote 데이터가 없어 답변할 수 없습니다.";
  }
  if (question.includes("가격") || question.includes("현재가") || question.includes("price")) {
    return `${quote.companyName}(${quote.symbol})의 현재 화면 기준 가격은 ${formatCurrency(quote.price)}입니다.`;
  }
  if (question.includes("등락") || question.includes("변동") || question.includes("change")) {
    return `${quote.symbol}의 화면 기준 등락은 ${formatCurrency(quote.change)} (${quote.changePercent.toFixed(2)}%)입니다.`;
  }
  if (question.includes("흐름") || question.includes("추세") || question.includes("trend")) {
    return describeTrend(history);
  }
  if (question.includes("최고") || question.includes("최저") || question.includes("high") || question.includes("low")) {
    return highLow(history);
  }
  if (question.includes("뉴스") || question.includes("news")) {
    return newsSummary(news);
  }
  if (question.includes("회사") || question.includes("정보") || question.includes("company")) {
    return `${quote.companyName}(${quote.symbol})입니다. MVP 챗봇은 화면에 제공된 quote, 가격 차트, 뉴스 외의 회사 사실은 생성하지 않습니다.`;
  }

  return `${quote.symbol}에 대해 답변할 수 있는 범위는 현재 가격, 등락률, 최근 주가 흐름, 최고가와 최저가, 화면의 주요 뉴스, 회사명입니다. 투자 추천이나 미래 가격 예측은 제공하지 않습니다.`;
}

export async function answerChat(request: ChatRequest): Promise<ChatResponse> {
  if (!request.messages.at(-1)?.content.trim()) {
    return {
      source: "unavailable",
      message: { role: "assistant", content: "빈 메시지는 전송할 수 없습니다." }
    };
  }

  if (process.env.OPENAI_API_KEY) {
    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${process.env.OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: process.env.OPENAI_MODEL || "gpt-4o-mini",
          messages: [
            {
              role: "system",
              content:
                "You answer only from the provided quote, price history, and news. Do not give buy/sell advice, target prices, future price predictions, or unsupported facts. If evidence is insufficient, say so."
            },
            {
              role: "user",
              content: JSON.stringify({
                symbol: request.symbol,
                quote: request.quote,
                history: request.history,
                news: request.news,
                latestQuestion: request.messages.at(-1)?.content
              })
            }
          ],
          temperature: 0.2
        }),
        cache: "no-store"
      });
      if (!response.ok) {
        throw new Error(`OpenAI request failed with ${response.status}`);
      }
      const payload = (await response.json()) as { choices?: Array<{ message?: { content?: string } }> };
      const content = payload.choices?.[0]?.message?.content?.trim();
      if (content) {
        return { source: "openai", message: { role: "assistant", content } };
      }
    } catch (error) {
      console.error("OpenAI chat failed", error);
    }
  }

  return {
    source: "rules",
    message: {
      role: "assistant",
      content: answerWithRules(request)
    }
  };
}
