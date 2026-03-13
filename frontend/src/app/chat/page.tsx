"use client";

import { useState, useRef, useEffect } from "react";
import { PageHeader } from "@/components/page-header";
import { sendChatMessage } from "@/lib/api";
import type { ChatResponse, Citation } from "@/lib/api";
import { Send, Bot, User, BookOpen, BarChart3, MessageCircle, ShieldX, Loader2, Trash2, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  citations?: Citation[];
}

const SUGGESTIONS = [
  { icon: "📚", route: "rag", text: "O que o Pai Rico ensina sobre ativos e passivos?" },
  { icon: "📚", route: "rag", text: "Como funciona o juros compostos?" },
  { icon: "📊", route: "data", text: "Quanto gastei este mês?" },
  { icon: "📊", route: "data", text: "Quais são minhas maiores despesas?" },
  { icon: "💬", route: "general", text: "Como posso usar o Órbita?" },
  { icon: "💬", route: "general", text: "O que é o Open Finance Brasil?" },
];

const ROUTE_CONFIG: Record<string, { icon: typeof BookOpen; label: string; color: string; bg: string }> = {
  rag: { icon: BookOpen, label: "Base de Conhecimento", color: "text-blue-600", bg: "bg-blue-50" },
  data: { icon: BarChart3, label: "Seus Dados", color: "text-amber-600", bg: "bg-amber-50" },
  general: { icon: MessageCircle, label: "Resposta Direta", color: "text-gray-600", bg: "bg-gray-100" },
  refuse: { icon: ShieldX, label: "Fora do Escopo", color: "text-red-600", bg: "bg-red-50" },
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(text.trim());
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.response,
        intent: res.intent,
        citations: res.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
          intent: "general",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      <PageHeader
        title="Assistente Financeiro"
        subtitle="Pergunte sobre seus dados, conceitos financeiros ou livros clássicos"
      >
        {messages.length > 0 && (
          <button
            onClick={() => setMessages([])}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Trash2 size={14} />
            Limpar
          </button>
        )}
      </PageHeader>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 ? (
          <div className="animate-fade-in-up">
            {/* Suggestion chips */}
            <div className="grid grid-cols-3 gap-2 mb-6">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => send(s.text)}
                  className="text-left p-3 rounded-xl border border-gray-100 bg-white text-sm text-gray-600 hover:border-[#4686fe]/30 hover:shadow-sm transition-all"
                >
                  <span className="mr-1.5">{s.icon}</span>
                  {s.text}
                </button>
              ))}
            </div>

            {/* How it works */}
            <div className="bg-white rounded-2xl border border-gray-100 p-5 max-w-lg mx-auto">
              <h3 className="text-sm font-bold text-gray-800 mb-3">
                Como funciona o assistente
              </h3>
              <div className="space-y-2.5">
                {[
                  { badge: "📚 Conhecimento", desc: "Conceitos financeiros e livros clássicos", cls: "text-blue-600 bg-blue-50" },
                  { badge: "📊 Seus Dados", desc: "Gastos, saldo e transações via Open Finance", cls: "text-amber-600 bg-amber-50" },
                  { badge: "💬 Direto", desc: "Perguntas gerais respondidas sem RAG", cls: "text-gray-600 bg-gray-100" },
                ].map((item) => (
                  <div key={item.badge} className="flex items-center gap-2.5 text-sm">
                    <span className={cn("text-[10px] font-semibold px-2 py-0.5 rounded-full", item.cls)}>
                      {item.badge}
                    </span>
                    <span className="text-gray-500">{item.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-3 animate-fade-in-up",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#4686fe] to-[#659bff] flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot size={16} className="text-white" />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[70%] rounded-2xl px-4 py-3",
                  msg.role === "user"
                    ? "bg-[#4686fe] text-white"
                    : "bg-white border border-gray-100"
                )}
              >
                {msg.role === "assistant" && msg.intent && (
                  <div className="mb-2">
                    {(() => {
                      const config = ROUTE_CONFIG[msg.intent] || ROUTE_CONFIG.general;
                      const Icon = config.icon;
                      return (
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full",
                            config.color,
                            config.bg
                          )}
                        >
                          <Icon size={10} />
                          {config.label}
                        </span>
                      );
                    })()}
                  </div>
                )}
                <div
                  className={cn(
                    "text-sm leading-relaxed whitespace-pre-wrap",
                    msg.role === "user" ? "text-white" : "text-gray-700"
                  )}
                >
                  {msg.content}
                </div>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-100 space-y-1">
                    <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
                      Fontes
                    </div>
                    {msg.citations.map((c, ci) => (
                      <div
                        key={ci}
                        className="text-[11px] text-gray-500 flex items-start gap-1"
                      >
                        <span className="text-[#4686fe]">•</span>
                        <span>
                          {c.source}
                          {c.page ? `, p.${c.page}` : ""}
                          {c.passage && (
                            <span className="text-gray-400 italic ml-1">
                              &ldquo;{c.passage.slice(0, 80)}...&rdquo;
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User size={16} className="text-gray-500" />
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-3 animate-fade-in-up">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#4686fe] to-[#659bff] flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Loader2 size={14} className="animate-spin" />
                Pensando...
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-100 pt-4 pb-2">
        <div className="flex items-end gap-2 bg-white rounded-2xl border border-gray-200 p-2 focus-within:border-[#4686fe] focus-within:ring-2 focus-within:ring-[#4686fe]/10 transition-all">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte sobre suas finanças ou conceitos financeiros..."
            rows={1}
            className="flex-1 text-sm px-2 py-1.5 resize-none focus:outline-none text-gray-800 placeholder:text-gray-400"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className={cn(
              "w-9 h-9 rounded-xl flex items-center justify-center transition-all flex-shrink-0",
              input.trim() && !loading
                ? "bg-[#4686fe] text-white hover:bg-[#3570e0]"
                : "bg-gray-100 text-gray-400"
            )}
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
