import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 知识库 Agent",
  description: "知识库问答与 Agent 工作台原型。"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
