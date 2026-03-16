"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { PeriodSelect } from "@/components/period-select";
import { MetricCard } from "@/components/metric-card";
import { SkeletonCard, SkeletonRow } from "@/components/skeleton";
import { getReports } from "@/lib/api";
import type { Summary, MonthlyData, CategoryTotals, RecurringItem } from "@/lib/api";
import { getDateRange, formatCurrency, CATEGORY_CONFIG } from "@/lib/utils";
import { FileBarChart, TrendingUp, TrendingDown, PiggyBank, ArrowRight } from "lucide-react";

export default function ReportsPage() {
  const [period, setPeriod] = useState("this-month");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<Summary>({ income: 0, expenses: 0, net: 0, count: 0 });
  const [monthly, setMonthly] = useState<MonthlyData[]>([]);
  const [categories, setCategories] = useState<CategoryTotals>({});
  const [recurring, setRecurring] = useState<RecurringItem[]>([]);

  useEffect(() => {
    const { start, end } = getDateRange(period);
    let cancelled = false;
    setLoading(true);
    setSummary({ income: 0, expenses: 0, net: 0, count: 0 });
    setMonthly([]);
    setCategories({});
    setRecurring([]);

    getReports(start, end)
      .then((data) => {
        if (cancelled) return;
        setSummary(data.summary);
        setMonthly(data.monthly);
        setCategories(data.categories);
        setRecurring(data.recurring);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [period]);

  const savingsRate =
    summary.income > 0
      ? ((summary.income - summary.expenses) / summary.income) * 100
      : 0;

  const topCategories = Object.entries(categories)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <>
      <PageHeader title="Relatórios" subtitle="Resumo financeiro consolidado">
        <PeriodSelect value={period} onChange={setPeriod} />
      </PageHeader>

      {loading ? (
        <div className="grid grid-cols-4 gap-4 mb-6 stagger">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4 mb-6 stagger">
          <MetricCard
            label="Receitas"
            value={formatCurrency(summary.income)}
            icon={<TrendingUp size={18} className="text-emerald-500" />}
            iconBg="bg-emerald-50"
          />
          <MetricCard
            label="Despesas"
            value={formatCurrency(summary.expenses)}
            icon={<TrendingDown size={18} className="text-red-400" />}
            iconBg="bg-red-50"
          />
          <MetricCard
            label="Resultado"
            value={formatCurrency(summary.net)}
            delta={summary.net >= 0 ? "Superávit" : "Déficit"}
            deltaType={summary.net >= 0 ? "positive" : "negative"}
            icon={<FileBarChart size={18} className="text-[#4686fe]" />}
            iconBg="bg-blue-50"
          />
          <MetricCard
            label="Taxa de Poupança"
            value={`${savingsRate.toFixed(1)}%`}
            icon={<PiggyBank size={18} className="text-violet-500" />}
            iconBg="bg-violet-50"
          />
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 stagger">
        {/* Top categories */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 className="text-sm font-bold text-gray-800 mb-4">
            Top 5 Categorias
          </h3>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <SkeletonRow key={i} />
              ))}
            </div>
          ) : topCategories.length === 0 ? (
            <p className="text-sm text-gray-400">Sem dados</p>
          ) : (
            <div className="space-y-3">
              {topCategories.map(([key, value], i) => {
                const cat = CATEGORY_CONFIG[key] || CATEGORY_CONFIG.outros;
                const totalExp = Object.values(categories).reduce((s, v) => s + v, 0);
                const pct = totalExp > 0 ? (value / totalExp) * 100 : 0;
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-4 font-bold">
                      {i + 1}
                    </span>
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                      style={{ background: `${cat.color}15` }}
                    >
                      {cat.emoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">
                          {cat.label}
                        </span>
                        <span className="text-sm font-bold text-gray-800 tabular-nums">
                          {formatCurrency(value)}
                        </span>
                      </div>
                      <div className="h-1 bg-gray-100 rounded-full mt-1 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${pct}%`, background: cat.color }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Monthly trend */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 className="text-sm font-bold text-gray-800 mb-4">
            Evolução Mensal
          </h3>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <SkeletonRow key={i} />
              ))}
            </div>
          ) : monthly.length === 0 ? (
            <p className="text-sm text-gray-400">Sem dados</p>
          ) : (
            <div className="space-y-2">
              {monthly.map((m) => (
                <div
                  key={m.key}
                  className="flex items-center justify-between py-2 border-b border-gray-50 last:border-b-0"
                >
                  <span className="text-sm text-gray-600 font-medium">
                    {m.month}
                  </span>
                  <div className="flex items-center gap-4 text-xs tabular-nums">
                    <span className="text-emerald-500 font-medium">
                      +{formatCurrency(m.income)}
                    </span>
                    <ArrowRight size={12} className="text-gray-300" />
                    <span className="text-red-400 font-medium">
                      -{formatCurrency(m.expenses)}
                    </span>
                    <span
                      className={`font-bold ${
                        m.net >= 0 ? "text-emerald-600" : "text-red-500"
                      }`}
                    >
                      {m.net >= 0 ? "+" : ""}
                      {formatCurrency(m.net)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recurring summary */}
      {!loading && recurring.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mt-4 animate-fade-in-up">
          <h3 className="text-sm font-bold text-gray-800 mb-3">
            Recorrentes ({recurring.length})
          </h3>
          <div className="text-sm text-gray-500">
            Gasto fixo mensal estimado:{" "}
            <span className="font-bold text-gray-800">
              {formatCurrency(recurring.reduce((s, r) => s + r.avg_amount, 0))}
            </span>
          </div>
        </div>
      )}
    </>
  );
}
