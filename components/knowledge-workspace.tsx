"use client";

import {
  AlertTriangle,
  Bot,
  Check,
  CheckCircle2,
  Clock3,
  FileText,
  FolderOpen,
  Loader2,
  MessageSquare,
  MoreHorizontal,
  Pause,
  Plus,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Upload,
  User,
  X
} from "lucide-react";
import { FormEvent, useMemo, useRef, useState } from "react";
import { sendChatMessage } from "@/lib/chat-api";
import { uploadDocument } from "@/lib/document-api";
import { agentSteps, conversations, documents, initialMessages } from "@/lib/mock-data";
import type { AgentStep, ChatMessage, KnowledgeDocument } from "@/lib/types";

const statusStyles: Record<KnowledgeDocument["status"], string> = {
  indexed: "border-emerald-200 bg-emerald-50 text-emerald-800",
  processing: "border-blue-200 bg-blue-50 text-blue-800",
  needs_review: "border-amber-200 bg-amber-50 text-amber-800"
};

const typeLabels: Record<KnowledgeDocument["type"], string> = {
  pdf: "PDF",
  markdown: "MD",
  note: "笔记"
};

const statusLabels: Record<KnowledgeDocument["status"], string> = {
  indexed: "已入库",
  processing: "处理中",
  needs_review: "待复核"
};

export function KnowledgeWorkspace() {
  const [knowledgeDocs, setKnowledgeDocs] = useState(documents);
  const [messages, setMessages] = useState(initialMessages);
  const [steps, setSteps] = useState(agentSteps);
  const [prompt, setPrompt] = useState("");
  const [selectedDocId, setSelectedDocId] = useState(documents[0].id);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectedDoc = useMemo(
    () => knowledgeDocs.find((doc) => doc.id === selectedDocId) ?? knowledgeDocs[0],
    [knowledgeDocs, selectedDocId]
  );

  async function handleFileUpload(files: FileList | null) {
    if (!files?.length) {
      return;
    }

    const uploadStartedAt = Date.now();
    const fileList = Array.from(files);
    setIsUploading(true);

    try {
      const nextDocs = await Promise.all(
        fileList.map(async (file, index) => {
          const result = await uploadDocument(file);

          return {
            id: `upload-${uploadStartedAt}-${index}`,
            title: result.filename || file.name,
            type: file.name.endsWith(".md") ? "markdown" : file.name.endsWith(".pdf") ? "pdf" : "note",
            status: "processing",
            chunks: Math.max(8, Math.round(file.size / 1500)),
            updatedAt: "刚刚",
            summary: "文件已上传，等待后端解析、切片和向量化。",
            tags: ["已上传", "待处理"]
          } satisfies KnowledgeDocument;
        })
      );

      setKnowledgeDocs((current) => [...nextDocs, ...current]);
      setSelectedDocId(nextDocs[0].id);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "上传失败";
      window.alert(`${errorMessage}。请确认 FastAPI 后端已启动，并已实现 /api/documents/upload。`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function submitPrompt(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = prompt.trim();

    if (!trimmed || isGenerating) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-user`,
      role: "user",
      content: trimmed
    };

    const assistantMessage: ChatMessage = {
      id: `msg-${Date.now()}-assistant`,
      role: "assistant",
      content: "正在检索已入库文档、重排片段，并生成带依据的回答...",
      citations: []
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setPrompt("");
    setIsGenerating(true);
    setIsApproved(false);
    setSteps((current) =>
      current.map((step) =>
        step.id === "step-3"
          ? {
              ...step,
              status: "running",
              detail: "正在基于高相关片段组织答案。"
            }
          : step
      )
    );

    try {
      const data = await sendChatMessage(trimmed);

      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessage.id
            ? {
                ...message,
                content: data.answer,
                citations: data.citations ?? []
              }
            : message
        )
      );
      setSteps((current) =>
        current.map((step) =>
          step.id === "step-3"
            ? {
                ...step,
                status: "waiting",
                detail: "接口已返回回答，等待人工审批。"
              }
            : step
        )
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "请求 /api/chat 失败";

      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessage.id
            ? {
                ...message,
                content: `${errorMessage}。请确认 FastAPI 后端已启动，并且前端能够访问 /api/chat。`,
                citations: []
              }
            : message
        )
      );
      setSteps((current) =>
        current.map((step) =>
          step.id === "step-3"
            ? {
                ...step,
                status: "waiting",
                detail: "接口请求失败，需要检查后端服务或代理配置。"
              }
            : step
        )
      );
    } finally {
      setIsGenerating(false);
    }
  }

  function approveDraft() {
    setIsApproved(true);
    setSteps((current) =>
      current.map((step) =>
        step.id === "step-3"
          ? {
              ...step,
              status: "done",
              detail: "人工复核已通过该回复草稿。"
            }
          : step
      )
    );
  }

  return (
    <main className="min-h-screen px-3 py-3 text-[var(--ink)] sm:px-5 lg:px-6">
      <div className="mx-auto flex min-h-[calc(100vh-24px)] max-w-[1600px] flex-col overflow-hidden rounded-[18px] border border-[var(--line)] bg-[var(--surface)] shadow-panel lg:grid lg:grid-cols-[310px_minmax(0,1fr)_340px]">
        <aside className="flex min-h-0 flex-col border-b border-[var(--line)] bg-[#eef3eb] lg:border-b-0 lg:border-r">
          <WorkspaceHeader />
          <div className="border-y border-[var(--line)] p-3">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-[var(--ink)] text-sm font-semibold text-white transition hover:bg-[#243532] disabled:bg-[#7f8d88]"
            >
              {isUploading ? <Loader2 size={17} className="animate-spin" /> : <Upload size={17} />}
              {isUploading ? "上传中" : "上传文档"}
            </button>
            <input
              ref={fileInputRef}
              className="sr-only"
              type="file"
              multiple
              accept=".pdf,.md,.txt"
              disabled={isUploading}
              onChange={(event) => {
                void handleFileUpload(event.target.files);
              }}
            />
          </div>

          <div className="thin-scrollbar min-h-[240px] flex-1 overflow-y-auto p-3">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--muted)]">知识库</h2>
              <button
                type="button"
                className="grid h-8 w-8 place-items-center rounded-md border border-[var(--line)] bg-white text-[var(--muted)] transition hover:text-[var(--ink)]"
                aria-label="更多文档操作"
              >
                <MoreHorizontal size={17} />
              </button>
            </div>

            <div className="space-y-2">
              {knowledgeDocs.map((doc) => (
                <button
                  key={doc.id}
                  type="button"
                  onClick={() => setSelectedDocId(doc.id)}
                  className={`w-full rounded-lg border p-3 text-left transition ${
                    selectedDocId === doc.id
                      ? "border-[var(--green)] bg-white shadow-inset"
                      : "border-transparent bg-white/60 hover:border-[var(--line)] hover:bg-white"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-[#dfe9e3] text-[var(--green)]">
                      <FileText size={18} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-bold">{doc.title}</span>
                      <span className="mt-1 block line-clamp-2 text-xs leading-5 text-[var(--muted)]">
                        {doc.summary}
                      </span>
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px]">
                    <span className="rounded border border-[var(--line)] bg-white px-2 py-1 font-bold text-[var(--blue)]">
                      {typeLabels[doc.type]}
                    </span>
                    <span className={`rounded border px-2 py-1 font-bold ${statusStyles[doc.status]}`}>
                      {statusLabels[doc.status]}
                    </span>
                    <span className="ml-auto text-[var(--muted)]">{doc.chunks} 个片段</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="border-t border-[var(--line)] p-3">
            <h2 className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-[var(--muted)]">会话</h2>
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  className="flex w-full items-center gap-3 rounded-lg border border-transparent bg-white/60 p-2 text-left transition hover:border-[var(--line)] hover:bg-white"
                >
                  <MessageSquare size={16} className="text-[var(--blue)]" />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-xs font-bold">{conversation.title}</span>
                    <span className="text-[11px] text-[var(--muted)]">
                      {conversation.messageCount} 条消息 - {conversation.updatedAt}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="flex min-h-[620px] min-w-0 flex-col bg-[var(--surface)]">
          <div className="border-b border-[var(--line)] px-4 py-4 sm:px-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-[var(--green)]">
                  检索工作台
                </p>
                <h1 className="mt-1 font-display text-2xl font-black text-[var(--ink)] sm:text-3xl">
                  AI 知识库 Agent
                </h1>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <Metric label="文档" value={knowledgeDocs.length.toString()} />
                <Metric label="片段" value={knowledgeDocs.reduce((sum, doc) => sum + doc.chunks, 0).toString()} />
                <Metric label="均分" value="0.88" />
              </div>
            </div>
          </div>

          <div className="thin-scrollbar flex-1 overflow-y-auto px-4 py-5 sm:px-6">
            <div className="mx-auto flex max-w-4xl flex-col gap-4">
              <SelectedDocument doc={selectedDoc} />

              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {isGenerating ? (
                <div className="flex items-center gap-3 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-[var(--blue)]">
                  <Loader2 size={17} className="animate-spin" />
                  正在执行检索、重排和答案生成
                </div>
              ) : null}
            </div>
          </div>

          <div className="border-t border-[var(--line)] bg-[#f7f8f1] p-3 sm:p-4">
            <form onSubmit={submitPrompt} className="mx-auto flex max-w-4xl flex-col gap-3">
              <div className="flex items-center justify-between gap-3 text-xs text-[var(--muted)]">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center gap-1 rounded border border-[var(--line)] bg-white px-2 py-1 font-bold text-[var(--green)]">
                    <ShieldCheck size={14} />
                    必须带引用
                  </span>
                  <span className="inline-flex items-center gap-1 rounded border border-[var(--line)] bg-white px-2 py-1">
                    <Search size={14} />
                    混合检索
                  </span>
                </div>
                <button
                  type="button"
                  className="hidden items-center gap-1 rounded-md px-2 py-1 font-bold text-[var(--muted)] transition hover:bg-white hover:text-[var(--ink)] sm:inline-flex"
                >
                  <Pause size={14} />
                  停止
                </button>
              </div>

              <div className="flex items-end gap-2 rounded-xl border border-[var(--line)] bg-white p-2 shadow-inset">
                <textarea
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  rows={2}
                  placeholder="询问政策、对比文档，或生成带引用的回复..."
                  className="max-h-32 min-h-[52px] flex-1 resize-none border-0 bg-transparent px-2 py-2 text-sm leading-6 outline-none placeholder:text-[#9aa6a3]"
                />
                <button
                  type="submit"
                  disabled={!prompt.trim() || isGenerating}
                  className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-[var(--green)] text-white transition hover:bg-[#0b5947] disabled:bg-[#aeb9b5]"
                  aria-label="发送问题"
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
        </section>

        <aside className="flex min-h-0 flex-col border-t border-[var(--line)] bg-[#f4f0e8] lg:border-l lg:border-t-0">
          <div className="border-b border-[var(--line)] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-[var(--clay)]">Agent 运行</p>
                <h2 className="mt-1 font-display text-xl font-black">工具活动</h2>
              </div>
              <span className="grid h-10 w-10 place-items-center rounded-lg bg-white text-[var(--clay)]">
                <Bot size={20} />
              </span>
            </div>
          </div>

          <div className="thin-scrollbar flex-1 overflow-y-auto p-4">
            <div className="space-y-3">
              {steps.map((step) => (
                <AgentStepItem key={step.id} step={step} />
              ))}
            </div>

            <div className="mt-5 rounded-lg border border-[var(--line)] bg-white p-4">
              <div className="flex items-start gap-3">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-amber-50 text-[var(--amber)]">
                  <AlertTriangle size={18} />
                </span>
                <div>
                  <h3 className="text-sm font-black">人工审批</h3>
                  <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                    对外回复和数据变更会保持阻塞，直到复核人员批准草稿。
                  </p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={approveDraft}
                  disabled={isApproved}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[var(--green)] text-sm font-bold text-white transition hover:bg-[#0b5947] disabled:bg-[#9cad9f]"
                >
                  <Check size={16} />
                  {isApproved ? "已批准" : "批准"}
                </button>
                <button
                  type="button"
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-[var(--line)] bg-white text-sm font-bold transition hover:border-[var(--clay)] hover:text-[var(--clay)]"
                >
                  <X size={16} />
                  拒绝
                </button>
              </div>
            </div>

            <div className="mt-5 rounded-lg border border-[var(--line)] bg-[#172120] p-4 text-white">
              <div className="flex items-center gap-2 text-sm font-black">
                <Sparkles size={17} className="text-[#e3b45f]" />
                下一步后端接入
              </div>
              <p className="mt-2 text-xs leading-5 text-white/70">
                将当前 mock 状态替换为 FastAPI 接口：上传、流式聊天、检索和运行轨迹。
              </p>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

function WorkspaceHeader() {
  return (
    <div className="p-4">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-[var(--ink)] text-white">
          <FolderOpen size={21} />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-black">运营知识库</p>
          <p className="text-xs text-[var(--muted)]">本地原型</p>
        </div>
        <button
          type="button"
          className="ml-auto grid h-9 w-9 place-items-center rounded-lg border border-[var(--line)] bg-white text-[var(--muted)] transition hover:text-[var(--ink)]"
          aria-label="新建会话"
        >
          <Plus size={17} />
        </button>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-[84px] rounded-lg border border-[var(--line)] bg-white px-3 py-2 shadow-inset">
      <p className="font-bold text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-lg font-black text-[var(--ink)]">{value}</p>
    </div>
  );
}

function SelectedDocument({ doc }: { doc: KnowledgeDocument }) {
  return (
    <section className="rounded-lg border border-[var(--line)] bg-[#eef3eb] p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--muted)]">当前来源</p>
          <h2 className="mt-1 truncate font-display text-xl font-black">{doc.title}</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--muted)]">{doc.summary}</p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          {doc.tags.map((tag) => (
            <span key={tag} className="rounded border border-[var(--line)] bg-white px-2 py-1 text-xs font-bold">
              {tag}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser ? (
        <span className="mt-1 grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[var(--ink)] text-white">
          <Bot size={18} />
        </span>
      ) : null}

      <div className={`max-w-[760px] ${isUser ? "order-first" : ""}`}>
        <div
          className={`rounded-xl border px-4 py-3 text-sm leading-6 ${
            isUser
              ? "border-[var(--green)] bg-[var(--green)] text-white"
              : "border-[var(--line)] bg-white text-[var(--ink)]"
          }`}
        >
          {message.content}
        </div>

        {message.citations?.length ? (
          <div className="mt-2 space-y-2">
            {message.citations.map((citation) => (
              <div
                key={citation.id}
                className="rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-xs leading-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="truncate font-black text-[var(--blue)]">{citation.documentTitle}</span>
                  <span className="shrink-0 font-bold text-[var(--green)]">
                    {Math.round(citation.confidence * 100)}%
                  </span>
                </div>
                <p className="mt-1 text-[var(--muted)]">{citation.excerpt}</p>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {isUser ? (
        <span className="mt-1 grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[#dde7ef] text-[var(--blue)]">
          <User size={18} />
        </span>
      ) : null}
    </article>
  );
}

function AgentStepItem({ step }: { step: AgentStep }) {
  const icon =
    step.status === "done" ? (
      <CheckCircle2 size={17} />
    ) : step.status === "running" ? (
      <Loader2 size={17} className="animate-spin" />
    ) : (
      <Clock3 size={17} />
    );

  const tone =
    step.status === "done"
      ? "bg-emerald-50 text-emerald-700"
      : step.status === "running"
        ? "bg-blue-50 text-blue-700"
        : "bg-amber-50 text-amber-700";

  return (
    <div className="rounded-lg border border-[var(--line)] bg-white p-3">
      <div className="flex items-start gap-3">
        <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-md ${tone}`}>{icon}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <h3 className="truncate text-sm font-black">{step.label}</h3>
            <span className="rounded bg-[#edf1eb] px-2 py-1 text-[10px] font-black uppercase tracking-[0.08em] text-[var(--muted)]">
              {step.tool}
            </span>
          </div>
          <p className="mt-1 text-xs leading-5 text-[var(--muted)]">{step.detail}</p>
        </div>
      </div>
    </div>
  );
}
