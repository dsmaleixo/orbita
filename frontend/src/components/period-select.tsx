"use client";

import { cn } from "@/lib/utils";

const PERIODS = [
  { value: "this-month", label: "Este mês" },
  { value: "30d", label: "30 dias" },
  { value: "90d", label: "3 meses" },
  { value: "180d", label: "6 meses" },
];

interface PeriodSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export function PeriodSelect({ value, onChange }: PeriodSelectProps) {
  return (
    <div className="flex items-center bg-gray-50 rounded-xl p-1 gap-0.5">
      {PERIODS.map((p) => (
        <button
          key={p.value}
          onClick={() => onChange(p.value)}
          className={cn(
            "px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150",
            value === p.value
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-400 hover:text-gray-600"
          )}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
