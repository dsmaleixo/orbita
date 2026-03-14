"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Receipt,
  TrendingUp,
  Landmark,
  PiggyBank,
  Repeat,
  PieChart,
  Flag,
  FileBarChart,
  Bot,
  Link2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import type { AppConfig } from "@/lib/api";
import { getConfig } from "@/lib/api";

const NAV_SECTIONS = [
  {
    label: "Visão Geral",
    items: [
      { href: "/", icon: LayoutDashboard, label: "Dashboard" },
    ],
  },
  {
    label: "Finanças",
    items: [
      { href: "/transactions", icon: Receipt, label: "Transações" },
      { href: "/cash-flow", icon: TrendingUp, label: "Fluxo de Caixa" },
      { href: "/accounts", icon: Landmark, label: "Contas" },
      { href: "/assets", icon: PiggyBank, label: "Patrimônio" },
      { href: "/recurring", icon: Repeat, label: "Recorrentes" },
      { href: "/categories", icon: PieChart, label: "Categorias" },
      { href: "/goals", icon: Flag, label: "Metas" },
      { href: "/reports", icon: FileBarChart, label: "Relatórios" },
    ],
  },
  {
    label: "Assistente",
    items: [
      { href: "/chat", icon: Bot, label: "Assistente IA" },
    ],
  },
  {
    label: "Configurações",
    items: [
      { href: "/connect", icon: Link2, label: "Conectar Banco" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [config, setConfig] = useState<AppConfig | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});
  }, []);

  const statusDot = config
    ? config.connected
      ? "bg-emerald-400"
      : "bg-slate-400"
    : "bg-slate-400";

  const statusLabel = config
    ? config.connected
      ? "Open Finance"
      : "Desconectado"
    : "...";

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen bg-white border-r border-gray-100 flex flex-col z-40 transition-all duration-300",
        collapsed ? "w-[68px]" : "w-[240px]"
      )}
    >
      {/* Logo */}
      <div className={cn(
        "flex items-center gap-3 px-5 py-5 border-b border-gray-50",
        collapsed && "justify-center px-0"
      )}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#4686fe] to-[#659bff] flex items-center justify-center text-white text-lg font-bold flex-shrink-0">
          ◎
        </div>
        {!collapsed && (
          <div>
            <div className="text-[15px] font-bold text-gray-900 tracking-tight">
              Órbita
            </div>
            <div className="text-[10px] text-gray-400 tracking-wide uppercase">
              Finanças Pessoais
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2.5">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label} className="mb-4">
            {!collapsed && (
              <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider px-3 mb-1.5">
                {section.label}
              </div>
            )}
            {section.items.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-150 mb-0.5",
                    isActive
                      ? "bg-[#eef4ff] text-[#4686fe]"
                      : "text-gray-500 hover:bg-gray-50 hover:text-gray-700",
                    collapsed && "justify-center px-0"
                  )}
                >
                  <Icon
                    size={18}
                    className={cn(
                      "flex-shrink-0",
                      isActive ? "text-[#4686fe]" : "text-gray-400"
                    )}
                  />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className={cn(
        "border-t border-gray-50 px-4 py-3",
        collapsed && "px-2"
      )}>
        {!collapsed && (
          <div className="space-y-1 text-[11px] text-gray-400 mb-3">
            <div className="flex items-center gap-2">
              <span className={cn("w-1.5 h-1.5 rounded-full", statusDot)} />
              {statusLabel}
            </div>
            {config?.ollama_model && (
              <div className="flex items-center gap-2 text-[#4686fe]">
                <Bot size={12} />
                {config.ollama_model}
              </div>
            )}
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center py-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
}
