import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Órbita — Finanças Pessoais",
  description: "Veja seu dinheiro com clareza",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#f8fafc] text-gray-900 antialiased">
        <Sidebar />
        <main className="ml-[240px] min-h-screen">
          <div className="max-w-[1400px] mx-auto px-8 py-8">{children}</div>
        </main>
      </body>
    </html>
  );
}
