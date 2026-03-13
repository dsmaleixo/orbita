import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaType?: "positive" | "negative" | "neutral";
  icon?: ReactNode;
  iconBg?: string;
  className?: string;
}

export function MetricCard({
  label,
  value,
  delta,
  deltaType = "neutral",
  icon,
  iconBg = "bg-blue-50",
  className,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "bg-white rounded-2xl border border-gray-100 p-5 transition-all duration-200 hover:shadow-md hover:border-gray-200 hover:-translate-y-0.5 group relative overflow-hidden",
        className
      )}
    >
      <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-[#4686fe] to-[#659bff] opacity-0 group-hover:opacity-100 transition-opacity" />
      {icon && (
        <div
          className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center mb-3 text-lg",
            iconBg
          )}
        >
          {icon}
        </div>
      )}
      <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
        {label}
      </div>
      <div className="text-2xl font-extrabold text-gray-900 tracking-tight">
        {value}
      </div>
      {delta && (
        <div
          className={cn(
            "inline-flex items-center gap-1 text-xs font-medium mt-2 px-2 py-0.5 rounded-full",
            deltaType === "positive" &&
              "text-emerald-600 bg-emerald-50",
            deltaType === "negative" &&
              "text-red-500 bg-red-50",
            deltaType === "neutral" &&
              "text-gray-500 bg-gray-100"
          )}
        >
          {delta}
        </div>
      )}
    </div>
  );
}
