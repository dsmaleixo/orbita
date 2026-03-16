"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/metric-card";
import { SkeletonCard } from "@/components/skeleton";
import { getAccountsOverview } from "@/lib/api";
import type { Balance, Account } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Wallet, TrendingUp, Landmark, CreditCard } from "lucide-react";

const TYPE_COLORS: Record<string, string> = {
  BANK: "#4686fe",
  SAVINGS: "#10b981",
  INVESTMENT: "#8b5cf6",
  CREDIT: "#ef4444",
};

export default function AssetsPage() {
  const [loading, setLoading] = useState(true);
  const [balances, setBalances] = useState<Balance[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);

  useEffect(() => {
    setLoading(true);
    getAccountsOverview()
      .then((data) => {
        setBalances(data.balances);
        setAccounts(data.accounts);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const accountMap = new Map(accounts.map((a) => [a.account_id, a]));

  // Group by type
  const byType: Record<string, number> = {};
  balances.forEach((b) => {
    const type = accountMap.get(b.account_id)?.account_type?.toUpperCase() || "BANK";
    byType[type] = (byType[type] || 0) + b.balance;
  });

  const totalBalance = balances.reduce((s, b) => s + b.balance, 0);
  const positiveBalance = balances
    .filter((b) => b.balance > 0)
    .reduce((s, b) => s + b.balance, 0);

  const chartData = Object.entries(byType)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({
      name: key,
      value,
      color: TYPE_COLORS[key] || "#64748b",
    }));

  return (
    <>
      <PageHeader title="Patrimônio" subtitle="Visão consolidada dos seus ativos" />

      {loading ? (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4 mb-6 stagger">
          <MetricCard
            label="Patrimônio Líquido"
            value={formatCurrency(totalBalance)}
            icon={<Wallet size={18} className="text-[#4686fe]" />}
            iconBg="bg-blue-50"
          />
          <MetricCard
            label="Total em Ativos"
            value={formatCurrency(positiveBalance)}
            icon={<TrendingUp size={18} className="text-emerald-500" />}
            iconBg="bg-emerald-50"
          />
          <MetricCard
            label="Contas"
            value={String(balances.length)}
            icon={<Landmark size={18} className="text-violet-500" />}
            iconBg="bg-violet-50"
          />
        </div>
      )}

      {!loading && chartData.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 animate-fade-in-up">
          <h3 className="text-sm font-bold text-gray-800 mb-4">
            Distribuição por Tipo
          </h3>
          <div className="flex items-center gap-8">
            <div className="relative">
              <ResponsiveContainer width={220} height={220}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="white"
                    strokeWidth={3}
                  >
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "white",
                      border: "1px solid #f1f5f9",
                      borderRadius: "12px",
                      boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                      fontSize: "12px",
                    }}
                    formatter={(v: number) => [formatCurrency(v)]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                  <div className="text-xl font-extrabold text-gray-900">
                    {formatCurrency(totalBalance)}
                  </div>
                  <div className="text-[10px] text-gray-400">Patrimônio</div>
                </div>
              </div>
            </div>
            <div className="flex-1 space-y-3">
              {chartData.map((item) => {
                const pct = totalBalance > 0 ? (item.value / totalBalance) * 100 : 0;
                return (
                  <div key={item.name}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ background: item.color }}
                        />
                        <span className="text-gray-600 font-medium">{item.name}</span>
                      </div>
                      <span className="text-gray-800 font-bold tabular-nums">
                        {formatCurrency(item.value)}
                      </span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%`, background: item.color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
