import { NextResponse } from "next/server";

import { answerChat } from "@/lib/chatbot";
import type { ChatRequest } from "@/lib/types";

export async function POST(request: Request) {
  const body = (await request.json()) as ChatRequest;
  const latest = body.messages?.at(-1)?.content?.trim();

  if (!latest) {
    return NextResponse.json(
      {
        source: "unavailable",
        message: { role: "assistant", content: "빈 메시지는 전송할 수 없습니다." }
      },
      { status: 400 }
    );
  }

  return NextResponse.json(await answerChat(body));
}
