import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Nasdaq Pulse MVP",
  description: "Limited Nasdaq stock analysis MVP with MCP fallback support"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
