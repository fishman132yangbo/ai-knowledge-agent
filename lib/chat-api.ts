import type { Citation } from "./types";

export type ChatApiRequest = {
  session_id: string;
  query: string;
  collection: string;
  top_k: number;
  score_threshold: number;
};

export type ChatApiResponse = {
  answer: string;
  citations?: Citation[];
};

export async function sendChatMessage(query: string): Promise<ChatApiResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      session_id: "local-session",
      query,
      collection: "default",
      top_k: 5,
      score_threshold: 0.3
    } satisfies ChatApiRequest)
  });

  if (!response.ok) {
    throw new Error(`请求 /api/chat 失败：${response.status}`);
  }

  return response.json() as Promise<ChatApiResponse>;
}
