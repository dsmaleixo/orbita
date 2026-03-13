"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { SkeletonCard } from "@/components/skeleton";
import { getBalances, getAccounts } from "@/lib/api";
import type { Balance, Account } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { Landmark, CreditCard, PiggyBank, TrendingUp } from "lucide-react";

const ACCOUNT_ICONS: Record<string, typeof Landmark> = {
  BANK: Landmark,
  CREDIT: CreditCard,
  SAVINGS: PiggyBank,
  INVESTMENT: TrendingUp,
};

export default function AccountsPage() {
  const [loading, setLoading] = useState(true);
  const [balances, setBalances] = useState<Balance[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);

  useEffect(() => {
    setLoading(true);
    Promise.all([getBalances(), getAccounts()])
      .then(([b, a]) => {
        setBalances(b);
        setAccounts(a);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalBalance = balances.reduce((s, b) => s + (b.balance || 0), 0);

  const accountMap = new Map(accounts.map((a) => [a.account_id, a]));

  return (
    <>
      <PageHeader title="Contas" subtitle="Saldo por instituição e conta" />

      {/* Total banner */}
      <div className="bg-gradient-to-br from-[#4686fe] to-[#659bff] rounded-2xl p-6 mb-6 text-white animate-fade-in-up">
        <div className="text-xs font-semibold text-white/60 uppercase tracking-wider">
          Patrimônio Total
        </div>
        <div className="text-3xl font-extrabold mt-1 tracking-tight">
          {loading ? "..." : formatCurrency(totalBalance)}
        </div>
        <div className="text-sm text-white/50 mt-1">
          {balances.length} conta{balances.length !== 1 ? "s" : ""} conectada{balances.length !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Account cards */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4 stagger">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : balances.length === 0 ? (
        <div className="text-center py-12 text-gray-400 text-sm">
          Nenhuma conta encontrada. Conecte seu banco.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 stagger">
          {balances.map((bal) => {
            const acct = accountMap.get(bal.account_id);
            const type = acct?.account_type?.toUpperCase() || "BANK";
            const Icon = ACCOUNT_ICONS[type] || Landmark;
            const isPositive = bal.balance >= 0;
            return (
              <div
                key={bal.account_id}
                className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md hover:border-gray-200 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                      <Icon size={18} className="text-[#4686fe]" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-800">
                        {acct?.name || `Conta ${bal.account_id.slice(-4)}`}
                      </div>
                      <div className="text-[11px] text-gray-400">
                        {acct?.account_type || "Conta"} · {bal.currency || "BRL"}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      acct?.status === "active"
                        ? "text-emerald-600 bg-emerald-50"
                        : "text-gray-500 bg-gray-100"
                    }`}
                  >
                    {acct?.status || "ativa"}
                  </span>
                </div>
                <div
                  className={`text-2xl font-extrabold tracking-tight ${
                    isPositive ? "text-gray-900" : "text-red-500"
                  }`}
                >
                  {formatCurrency(bal.balance)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
