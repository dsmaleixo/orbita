"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/metric-card";
import { PeriodSelect } from "@/components/period-select";
import {
  IncomeExpenseChart,
  SavingsRateChart,
  CashFlowAreaChart,
} from "@/components/charts";
import { SkeletonCard, SkeletonChart } from "@/components/skeleton";
import { getDateRange, formatCurrency } from "@/lib/utils";
import { getCashFlow } from "@/lib/api";
import type { Summary, MonthlyData } from "@/lib/api";
import { TrendingUp, TrendingDown, PiggyBank } from "lucide-react";

export default function CashFlowPage() {
  const [period, setPeriod] = useState("180d");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<Summary>({ income: 0, expenses: 0, net: 0, count: 0 });
  const [monthly, setMonthly] = useState<MonthlyData[]>([]);
  const [cumulative, setCumulative] = useState<{ date: string; cumulative: number }[]>([]);

  useEffect(() => {
    const { start, end } = getDateRange(period);
    let cancelled = false;
    setLoading(true);
    setSummary({ income: 0, expenses: 0, net: 0, count: 0 });
    setMonthly([]);
    setCumulative([]);

    getCashFlow(start, end)
      .then((data) => {
        if (cancelled) return;
        setSummary(data.summary);
        setMonthly(data.monthly);
        const sorted = [...data.transactions].sort((a, b) => a.date.localeCompare(b.date));
        let running = 0;
        const cum = sorted.map((t) => {
          running += t.amount;
          return { date: t.date, cumulative: running };
        });
        setCumulative(cum);
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

  return (
    <>
      <PageHeader title="Fluxo de Caixa" subtitle="Receitas versus despesas ao longo do tempo">
        <PeriodSelect value={period} onChange={setPeriod} />
      </PageHeader>

      {loading ? (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
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
            label="Taxa de Poupança"
            value={`${savingsRate.toFixed(1)}%`}
            delta={savingsRate >= 20 ? "Saudável" : "Abaixo da meta"}
            deltaType={savingsRate >= 20 ? "positive" : "negative"}
            icon={<PiggyBank size={18} className="text-[#4686fe]" />}
            iconBg="bg-blue-50"
          />
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          <SkeletonChart />
          <div className="grid grid-cols-2 gap-4">
            <SkeletonChart />
            <SkeletonChart />
          </div>
        </div>
      ) : (
        <>
          <div className="mb-4 animate-fade-in-up">
            <IncomeExpenseChart data={monthly} />
          </div>
          <div className="grid grid-cols-2 gap-4 stagger">
            <CashFlowAreaChart data={cumulative} />
            <SavingsRateChart data={monthly} />
          </div>
        </>
      )}
    </>
  );
}
