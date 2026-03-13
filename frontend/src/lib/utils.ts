import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

export function formatCompact(value: number): string {
  if (Math.abs(value) >= 1000) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);
  }
  return formatCurrency(value);
}

export function formatDate(date: string): string {
  return new Date(date + "T00:00:00").toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
  });
}

export function formatDateFull(date: string): string {
  return new Date(date + "T00:00:00").toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export function getDateRange(period: string): { start: string; end: string } {
  const today = new Date();
  const end = today.toISOString().split("T")[0];
  let start: string;

  switch (period) {
    case "this-month":
      start = new Date(today.getFullYear(), today.getMonth(), 1)
        .toISOString()
        .split("T")[0];
      break;
    case "30d":
      start = new Date(Date.now() - 30 * 86400000).toISOString().split("T")[0];
      break;
    case "90d":
      start = new Date(Date.now() - 90 * 86400000).toISOString().split("T")[0];
      break;
    case "180d":
      start = new Date(Date.now() - 180 * 86400000).toISOString().split("T")[0];
      break;
    default:
      start = new Date(today.getFullYear(), today.getMonth(), 1)
        .toISOString()
        .split("T")[0];
  }
  return { start, end };
}

export const CATEGORY_CONFIG: Record<
  string,
  { label: string; color: string; emoji: string }
> = {
  alimentacao: { label: "Alimentação", color: "#f59e0b", emoji: "🍽️" },
  transporte: { label: "Transporte", color: "#3b82f6", emoji: "🚗" },
  moradia: { label: "Moradia", color: "#6366f1", emoji: "🏠" },
  saude: { label: "Saúde", color: "#10b981", emoji: "💊" },
  lazer: { label: "Lazer", color: "#ec4899", emoji: "🎉" },
  educacao: { label: "Educação", color: "#8b5cf6", emoji: "📚" },
  vestuario: { label: "Vestuário", color: "#f97316", emoji: "👕" },
  investimentos: { label: "Investimentos", color: "#06b6d4", emoji: "📈" },
  receita: { label: "Receita", color: "#10b981", emoji: "💰" },
  outros: { label: "Outros", color: "#64748b", emoji: "📦" },
};
