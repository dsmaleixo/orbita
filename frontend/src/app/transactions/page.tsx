"use client";

import { useEffect, useState, useMemo } from "react";
import { PageHeader } from "@/components/page-header";
import { PeriodSelect } from "@/components/period-select";
import { TransactionRow } from "@/components/transaction-row";
import { SkeletonRow } from "@/components/skeleton";
import { getTransactions } from "@/lib/api";
import type { Transaction } from "@/lib/api";
import { getDateRange, CATEGORY_CONFIG } from "@/lib/utils";
import { Search, Filter } from "lucide-react";

export default function TransactionsPage() {
  const [period, setPeriod] = useState("this-month");
  const [loading, setLoading] = useState(true);
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | "income" | "expense">("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  useEffect(() => {
    const { start, end } = getDateRange(period);
    let cancelled = false;
    setLoading(true);
    setTxns([]);

    getTransactions(start, end)
      .catch(() => [] as Transaction[])
      .then((t) => {
        if (!cancelled) setTxns(t);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [period]);

  const filtered = useMemo(() => {
    let result = [...txns].sort((a, b) => b.date.localeCompare(a.date));
    if (search) {
      const s = search.toLowerCase();
      result = result.filter((t) => t.description.toLowerCase().includes(s));
    }
    if (typeFilter === "income") result = result.filter((t) => t.amount > 0);
    if (typeFilter === "expense") result = result.filter((t) => t.amount < 0);
    if (categoryFilter !== "all")
      result = result.filter((t) => t.category === categoryFilter);
    return result;
  }, [txns, search, typeFilter, categoryFilter]);

  const categories = useMemo(() => {
    const set = new Set(txns.map((t) => t.category));
    return Array.from(set).sort();
  }, [txns]);

  return (
    <>
      <PageHeader title="Transações" subtitle="Lista completa de movimentações">
        <PeriodSelect value={period} onChange={setPeriod} />
      </PageHeader>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-5 animate-fade-in-up">
        <div className="relative flex-1 max-w-xs">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar transação..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-gray-200 bg-white focus:outline-none focus:border-[#4686fe] focus:ring-2 focus:ring-[#4686fe]/10 transition-all"
          />
        </div>
        <div className="flex items-center bg-gray-50 rounded-xl p-1 gap-0.5">
          {(["all", "income", "expense"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                typeFilter === t
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-400 hover:text-gray-600"
              }`}
            >
              {t === "all" ? "Todos" : t === "income" ? "Receitas" : "Despesas"}
            </button>
          ))}
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="text-sm rounded-xl border border-gray-200 bg-white px-3 py-2 focus:outline-none focus:border-[#4686fe] transition-all"
        >
          <option value="all">Todas categorias</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {CATEGORY_CONFIG[c]?.label || c}
            </option>
          ))}
        </select>
      </div>

      {/* Count */}
      <div className="text-xs text-gray-400 mb-3">
        {filtered.length} transação{filtered.length !== 1 ? "ões" : ""}
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-1.5">
          {Array.from({ length: 10 }).map((_, i) => (
            <SkeletonRow key={i} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400 text-sm">
          Nenhuma transação encontrada.
        </div>
      ) : (
        <div>
          {filtered.map((txn) => (
            <TransactionRow key={txn.id} txn={txn} />
          ))}
        </div>
      )}
    </>
  );
}
