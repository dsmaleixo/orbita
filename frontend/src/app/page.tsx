"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/metric-card";
import { PeriodSelect } from "@/components/period-select";
import { TransactionRow } from "@/components/transaction-row";
import {
  IncomeExpenseChart,
  CategoryDonut,
  BalanceLineChart,
} from "@/components/charts";
import { SkeletonCard, SkeletonRow, SkeletonChart } from "@/components/skeleton";
import { getDateRange, formatCurrency } from "@/lib/utils";
import { getDashboard } from "@/lib/api";
import type {
  Transaction,
  Summary,
  MonthlyData,
  CategoryTotals,
  BalancePoint,
} from "@/lib/api";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Zap,
} from "lucide-react";

export default function DashboardPage() {
  const [period, setPeriod] = useState("this-month");
  const [loading, setLoading] = useState(true);
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary>({ income: 0, expenses: 0, net: 0, count: 0 });
  const [monthly, setMonthly] = useState<MonthlyData[]>([]);
  const [categories, setCategories] = useState<CategoryTotals>({});
  const [balanceHistory, setBalanceHistory] = useState<BalancePoint[]>([]);
  const [totalBalance, setTotalBalance] = useState(0);

  useEffect(() => {
    const { start, end } = getDateRange(period);
    let cancelled = false;
    setLoading(true);

    getDashboard(start, end)
      .then((data) => {
        if (cancelled) return;
        setTxns(data.transactions);
        setTotalBalance(data.balances.reduce((sum, x) => sum + (x.balance || 0), 0));
        setSummary(data.summary);
        setMonthly(data.monthly);
        setCategories(data.categories);
        setBalanceHistory(data.balanceHistory);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [period]);

  const recentTxns = [...txns]
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 8);

  return (
    <>
      <PageHeader title="Visão Geral" subtitle="Resumo financeiro do período">
        <PeriodSelect value={period} onChange={setPeriod} />
      </PageHeader>

      {/* Hero card */}
      <div className="bg-gradient-to-br from-[#4686fe] via-[#5a94ff] to-[#659bff] rounded-2xl p-7 mb-6 text-white relative overflow-hidden animate-fade-in-up">
        <div className="absolute top-[-50%] right-[-10%] w-[300px] h-[300px] bg-white/[0.06] rounded-full" />
        <div className="absolute bottom-[-40%] left-[-5%] w-[200px] h-[200px] bg-white/[0.04] rounded-full" />
        <div className="relative">
          <div className="text-xs font-semibold text-white/60 uppercase tracking-wider">
            Saldo Total
          </div>
          <div className="text-4xl font-extrabold mt-1 tracking-tight">
            {loading ? "..." : formatCurrency(totalBalance)}
          </div>
          <div className="text-sm text-white/50 mt-1">
            Atualizado agora
          </div>
        </div>
      </div>

      {/* KPI cards */}
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
            label="Saldo"
            value={formatCurrency(totalBalance)}
            icon={<Wallet size={18} className="text-[#4686fe]" />}
            iconBg="bg-blue-50"
          />
          <MetricCard
            label="Receitas"
            value={formatCurrency(summary.income)}
            delta={`↑ ${txns.filter((t) => t.amount > 0).length} entradas`}
            deltaType="positive"
            icon={<TrendingUp size={18} className="text-emerald-500" />}
            iconBg="bg-emerald-50"
          />
          <MetricCard
            label="Despesas"
            value={formatCurrency(summary.expenses)}
            delta={`↓ ${txns.filter((t) => t.amount < 0).length} saídas`}
            deltaType="negative"
            icon={<TrendingDown size={18} className="text-red-400" />}
            iconBg="bg-red-50"
          />
          <MetricCard
            label="Resultado"
            value={formatCurrency(summary.net)}
            delta={summary.net >= 0 ? "Positivo" : "Negativo"}
            deltaType={summary.net >= 0 ? "positive" : "negative"}
            icon={<Zap size={18} className="text-amber-500" />}
            iconBg="bg-amber-50"
          />
        </div>
      )}

      {/* Charts */}
      {loading ? (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <SkeletonChart className="col-span-3" />
          <SkeletonChart className="col-span-2" />
        </div>
      ) : (
        <div className="grid grid-cols-5 gap-4 mb-6 stagger">
          <div className="col-span-3">
            <IncomeExpenseChart data={monthly} />
          </div>
          <div className="col-span-2">
            <CategoryDonut data={categories} />
          </div>
        </div>
      )}

      {/* Balance chart */}
      {!loading && balanceHistory.length > 0 && (
        <div className="mb-6 animate-fade-in-up">
          <BalanceLineChart data={balanceHistory} />
        </div>
      )}

      {/* Recent transactions */}
      <div className="animate-fade-in-up">
        <h3 className="text-sm font-bold text-gray-800 mb-3 pb-2 border-b border-gray-100">
          Transações Recentes
        </h3>
        {loading ? (
          <div className="space-y-1.5">
            {Array.from({ length: 5 }).map((_, i) => (
              <SkeletonRow key={i} />
            ))}
          </div>
        ) : recentTxns.length === 0 ? (
          <p className="text-sm text-gray-400 py-8 text-center">
            Nenhuma transação encontrada no período.
          </p>
        ) : (
          <div>
            {recentTxns.map((txn) => (
              <TransactionRow key={txn.id} txn={txn} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
