"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/metric-card";
import { SkeletonCard, SkeletonRow } from "@/components/skeleton";
import { getRecurring } from "@/lib/api";
import type { RecurringItem } from "@/lib/api";
import { getDateRange, formatCurrency, formatDate, CATEGORY_CONFIG } from "@/lib/utils";
import { Repeat, DollarSign, Hash } from "lucide-react";

export default function RecurringPage() {
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState<RecurringItem[]>([]);

  useEffect(() => {
    const { start, end } = getDateRange("180d");
    setLoading(true);
    getRecurring(start, end)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const totalMonthly = items.reduce((s, i) => s + i.avg_amount, 0);

  return (
    <>
      <PageHeader
        title="Recorrentes"
        subtitle="Cobranças e assinaturas detectadas automaticamente"
      />

      {loading ? (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
          <MetricCard
            label="Gasto Mensal Estimado"
            value={formatCurrency(totalMonthly)}
            icon={<DollarSign size={18} className="text-[#4686fe]" />}
            iconBg="bg-blue-50"
          />
          <MetricCard
            label="Assinaturas Detectadas"
            value={String(items.length)}
            icon={<Repeat size={18} className="text-violet-500" />}
            iconBg="bg-violet-50"
          />
          <MetricCard
            label="Gasto Anual Estimado"
            value={formatCurrency(totalMonthly * 12)}
            icon={<Hash size={18} className="text-amber-500" />}
            iconBg="bg-amber-50"
          />
        </div>
      )}

      {loading ? (
        <div className="space-y-1.5">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonRow key={i} />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-400 text-sm">
          Nenhuma cobrança recorrente detectada.
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-5 py-3 border-b border-gray-50 text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
            <span>Descrição</span>
            <span>Categoria</span>
            <span className="text-right">Valor Médio</span>
            <span className="text-center">Meses</span>
            <span className="text-right">Última Data</span>
          </div>
          {items.map((item, i) => {
            const cat = CATEGORY_CONFIG[item.category] || CATEGORY_CONFIG.outros;
            return (
              <div
                key={i}
                className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-5 py-3.5 border-b border-gray-50 last:border-b-0 hover:bg-gray-50/50 transition-colors items-center"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                    style={{ background: `${cat.color}15` }}
                  >
                    {cat.emoji}
                  </div>
                  <span className="text-sm font-medium text-gray-800 truncate">
                    {item.description}
                  </span>
                </div>
                <span
                  className="text-xs font-medium"
                  style={{ color: cat.color }}
                >
                  {cat.label}
                </span>
                <span className="text-sm font-bold text-gray-800 text-right tabular-nums">
                  {formatCurrency(item.avg_amount)}
                </span>
                <span className="text-xs text-gray-500 text-center">
                  {item.months}x
                </span>
                <span className="text-xs text-gray-400 text-right">
                  {formatDate(item.last_date)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
