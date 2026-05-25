import type { AgentStep, ChatMessage, Conversation, KnowledgeDocument } from "./types";

export const documents: KnowledgeDocument[] = [
  {
    id: "doc-1",
    title: "Q2 产品手册.pdf",
    type: "pdf",
    status: "indexed",
    chunks: 128,
    updatedAt: "10 分钟前",
    summary: "当前产品周期的定价规则、开通政策、功能限制和发布说明。",
    tags: ["定价", "政策", "发布"]
  },
  {
    id: "doc-2",
    title: "客户支持手册.md",
    type: "markdown",
    status: "indexed",
    chunks: 74,
    updatedAt: "1 小时前",
    summary: "客服标准回复、升级路径、退款政策和对外沟通语气规范。",
    tags: ["客服", "退款", "话术"]
  },
  {
    id: "doc-3",
    title: "企业安全问答",
    type: "note",
    status: "needs_review",
    chunks: 42,
    updatedAt: "昨天",
    summary: "面向企业安全问卷的回答，覆盖 SSO、数据保留、审计日志、加密和数据驻留。",
    tags: ["安全", "企业", "问答"]
  }
];

export const conversations: Conversation[] = [
  {
    id: "conv-1",
    title: "退款政策总结",
    updatedAt: "刚刚",
    messageCount: 8
  },
  {
    id: "conv-2",
    title: "企业客户开通风险",
    updatedAt: "24 分钟前",
    messageCount: 5
  },
  {
    id: "conv-3",
    title: "发布说明改写",
    updatedAt: "昨天",
    messageCount: 12
  }
];

export const initialMessages: ChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "帮我总结退款政策，并标出答案来自哪些文档。"
  },
  {
    id: "msg-2",
    role: "assistant",
    content:
      "自助套餐客户可以在购买后 14 天内申请退款；企业客户退款需要由客户团队审核。客服在给出最终回复前，应先确认套餐类型、购买时间和是否存在特殊使用情况。",
    citations: [
      {
        id: "cite-1",
        documentTitle: "客户支持手册.md",
        excerpt: "自助套餐客户可在购买后 14 天内进入退款审核流程。",
        confidence: 0.91
      },
      {
        id: "cite-2",
        documentTitle: "Q2 产品手册.pdf",
        excerpt: "企业商业例外情况必须转交客户团队处理。",
        confidence: 0.86
      }
    ]
  }
];

export const agentSteps: AgentStep[] = [
  {
    id: "step-1",
    tool: "search_docs",
    label: "混合文档检索",
    detail: "命中了客服手册和产品手册中的相关片段。",
    status: "done"
  },
  {
    id: "step-2",
    tool: "rerank",
    label: "证据重排",
    detail: "选择前 4 个片段作为答案依据。",
    status: "done"
  },
  {
    id: "step-3",
    tool: "draft_response",
    label: "生成客户回复草稿",
    detail: "对外发送前等待人工审批。",
    status: "waiting"
  }
];
