import { cn, formatCurrency, formatDate, CATEGORY_CONFIG } from "@/lib/utils";
import type { Transaction } from "@/lib/api";

interface TransactionRowProps {
  txn: Transaction;
}

export function TransactionRow({ txn }: TransactionRowProps) {
  const isIncome = txn.amount > 0;
  const cat = CATEGORY_CONFIG[txn.category] || CATEGORY_CONFIG.outros;

  return (
    <div className="flex items-center justify-between py-3 px-4 bg-white rounded-xl border border-gray-100 mb-1.5 transition-all duration-150 hover:border-gray-200 hover:shadow-sm hover:translate-x-0.5 group">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center text-sm flex-shrink-0"
          style={{
            background: isIncome ? "rgba(16,185,129,0.1)" : `${cat.color}15`,
          }}
        >
          {isIncome ? "💰" : cat.emoji}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[13px] font-medium text-gray-800 truncate">
            {txn.description}
          </div>
          <div className="text-[11px] text-gray-400 mt-0.5 flex items-center gap-1.5">
            {formatDate(txn.date)}
            <span className="w-0.5 h-0.5 rounded-full bg-gray-300" />
            <span style={{ color: cat.color }}>{cat.label}</span>
          </div>
        </div>
      </div>
      <div
        className={cn(
          "text-sm font-bold tabular-nums flex-shrink-0 ml-4",
          isIncome ? "text-emerald-500" : "text-gray-800"
        )}
      >
        {isIncome ? "+" : "-"}
        {formatCurrency(Math.abs(txn.amount))}
      </div>
    </div>
  );
}
