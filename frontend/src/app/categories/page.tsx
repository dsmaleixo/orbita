"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { PeriodSelect } from "@/components/period-select";
import { CategoryDonut, HorizontalBarCategories } from "@/components/charts";
import { SkeletonChart } from "@/components/skeleton";
import { getCategoriesOverview } from "@/lib/api";
import type { CategoryTotals, Transaction } from "@/lib/api";
import { getDateRange, formatCurrency, CATEGORY_CONFIG } from "@/lib/utils";

export default function CategoriesPage() {
  const [period, setPeriod] = useState("this-month");
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState<CategoryTotals>({});
  const [txns, setTxns] = useState<Transaction[]>([]);

  useEffect(() => {
    const { start, end } = getDateRange(period);
    let cancelled = false;
    setLoading(true);
    setCategories({});
    setTxns([]);

    getCategoriesOverview(start, end)
      .then((data) => {
        if (cancelled) return;
        setCategories(data.categories);
        setTxns(data.transactions);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [period]);

  const totalExpenses = Object.values(categories).reduce((s, v) => s + v, 0);
  const sortedEntries = Object.entries(categories).sort((a, b) => b[1] - a[1]);

  return (
    <>
      <PageHeader title="Categorias" subtitle="Gastos organizados por categoria">
        <PeriodSelect value={period} onChange={setPeriod} />
      </PageHeader>

      {loading ? (
        <div className="grid grid-cols-2 gap-4 stagger">
          <SkeletonChart />
          <SkeletonChart />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 mb-6 stagger">
            <CategoryDonut data={categories} />
            <HorizontalBarCategories data={categories} />
          </div>

          {/* Category breakdown table */}
          <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-in-up">
            <div className="px-5 py-4 border-b border-gray-50">
              <h3 className="text-sm font-bold text-gray-800">
                Detalhamento por Categoria
              </h3>
            </div>
            {sortedEntries.map(([key, value]) => {
              const cat = CATEGORY_CONFIG[key] || CATEGORY_CONFIG.outros;
              const pct = totalExpenses > 0 ? (value / totalExpenses) * 100 : 0;
              const count = txns.filter(
                (t) => t.category === key && t.amount < 0
              ).length;
              return (
                <div
                  key={key}
                  className="px-5 py-4 border-b border-gray-50 last:border-b-0 hover:bg-gray-50/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center text-sm"
                        style={{ background: `${cat.color}15` }}
                      >
                        {cat.emoji}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-gray-800">
                          {cat.label}
                        </div>
                        <div className="text-[11px] text-gray-400">
                          {count} transação{count !== 1 ? "ões" : ""}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-gray-800 tabular-nums">
                        {formatCurrency(value)}
                      </div>
                      <div className="text-[11px] text-gray-400">
                        {pct.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${pct}%`, background: cat.color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
