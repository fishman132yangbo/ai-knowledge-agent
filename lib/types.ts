export type DocumentStatus = "indexed" | "processing" | "needs_review";

export type KnowledgeDocument = {
  id: string;
  title: string;
  type: "pdf" | "markdown" | "note";
  status: DocumentStatus;
  chunks: number;
  updatedAt: string;
  summary: string;
  tags: string[];
};

export type Citation = {
  id: string;
  documentTitle: string;
  excerpt: string;
  confidence: number;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

export type AgentStepStatus = "done" | "running" | "waiting";

export type AgentStep = {
  id: string;
  tool: string;
  label: string;
  detail: string;
  status: AgentStepStatus;
};

export type Conversation = {
  id: string;
  title: string;
  updatedAt: string;
  messageCount: number;
};
