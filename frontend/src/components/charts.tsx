"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  LineChart,
  Line,
} from "recharts";
import { formatCompact, formatCurrency, CATEGORY_CONFIG } from "@/lib/utils";
import type { MonthlyData, CategoryTotals, BalancePoint } from "@/lib/api";

const TOOLTIP_STYLE = {
  contentStyle: {
    background: "white",
    border: "1px solid #f1f5f9",
    borderRadius: "12px",
    boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
    fontSize: "12px",
    padding: "8px 12px",
  },
  labelStyle: { fontWeight: 600, color: "#1e293b", marginBottom: 4 },
};

export function IncomeExpenseChart({ data }: { data: MonthlyData[] }) {
  if (!data.length) return <EmptyChart />;
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Fluxo de Caixa Mensal
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} barGap={4} barCategoryGap="25%">
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="month"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => formatCompact(v)}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            formatter={(v: number, name: string) => [
              formatCurrency(v),
              name === "income" ? "Receitas" : "Despesas",
            ]}
          />
          <Bar
            dataKey="income"
            fill="#10b981"
            radius={[6, 6, 0, 0]}
            maxBarSize={32}
          />
          <Bar
            dataKey="expenses"
            fill="#ef4444"
            radius={[6, 6, 0, 0]}
            maxBarSize={32}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CategoryDonut({ data }: { data: CategoryTotals }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return <EmptyChart />;

  const total = entries.reduce((s, [, v]) => s + v, 0);
  const chartData = entries.map(([key, value]) => ({
    name: CATEGORY_CONFIG[key]?.label || key,
    value,
    color: CATEGORY_CONFIG[key]?.color || "#64748b",
  }));

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Gastos por Categoria
      </h3>
      <div className="flex items-center">
        <div className="relative">
          <ResponsiveContainer width={200} height={200}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
                stroke="white"
                strokeWidth={2}
              >
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                {...TOOLTIP_STYLE}
                formatter={(v: number) => [formatCurrency(v)]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <div className="text-lg font-extrabold text-gray-900">
                {formatCompact(total)}
              </div>
              <div className="text-[10px] text-gray-400">Total</div>
            </div>
          </div>
        </div>
        <div className="flex-1 ml-4 space-y-1.5">
          {chartData.slice(0, 6).map((item) => (
            <div
              key={item.name}
              className="flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: item.color }}
                />
                <span className="text-gray-600">{item.name}</span>
              </div>
              <span className="text-gray-800 font-medium tabular-nums">
                {formatCurrency(item.value)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function BalanceLineChart({ data }: { data: BalancePoint[] }) {
  if (!data.length) return <EmptyChart />;
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Evolução do Saldo
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4686fe" stopOpacity={0.12} />
              <stop offset="95%" stopColor="#4686fe" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(d) =>
              new Date(d + "T00:00:00").toLocaleDateString("pt-BR", {
                day: "2-digit",
                month: "short",
              })
            }
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => formatCompact(v)}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            formatter={(v: number) => [formatCurrency(v), "Saldo"]}
          />
          <Area
            type="monotone"
            dataKey="balance"
            stroke="#4686fe"
            strokeWidth={2.5}
            fill="url(#balanceGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CashFlowAreaChart({
  data,
}: {
  data: { date: string; cumulative: number }[];
}) {
  if (!data.length) return <EmptyChart />;
  const isPositive = (data[data.length - 1]?.cumulative ?? 0) >= 0;
  const color = isPositive ? "#10b981" : "#ef4444";

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Fluxo Acumulado
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="cfGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.12} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => formatCompact(v)}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            formatter={(v: number) => [formatCurrency(v), "Acumulado"]}
          />
          <Area
            type="monotone"
            dataKey="cumulative"
            stroke={color}
            strokeWidth={2.5}
            fill="url(#cfGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function HorizontalBarCategories({ data }: { data: CategoryTotals }) {
  const entries = Object.entries(data)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);
  if (!entries.length) return <EmptyChart />;

  const chartData = entries.map(([key, value]) => ({
    name: CATEGORY_CONFIG[key]?.label || key,
    value,
    color: CATEGORY_CONFIG[key]?.color || "#64748b",
  }));

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Maiores Categorias
      </h3>
      <ResponsiveContainer width="100%" height={Math.max(220, chartData.length * 36)}>
        <BarChart data={chartData} layout="vertical" barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
          <XAxis
            type="number"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => formatCompact(v)}
          />
          <YAxis
            dataKey="name"
            type="category"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#64748b", fontSize: 11 }}
            width={90}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            formatter={(v: number) => [formatCurrency(v)]}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]} maxBarSize={24}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SavingsRateChart({
  data,
}: {
  data: MonthlyData[];
}) {
  if (!data.length) return <EmptyChart />;
  const chartData = data.map((d) => ({
    ...d,
    rate: d.income > 0 ? ((d.income - d.expenses) / d.income) * 100 : 0,
  }));

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-bold text-gray-800 mb-4">
        Taxa de Poupança
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="month"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            formatter={(v: number) => [`${v.toFixed(1)}%`, "Poupança"]}
          />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="#4686fe"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#4686fe", strokeWidth: 2, stroke: "white" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 flex items-center justify-center h-[200px]">
      <p className="text-sm text-gray-400">Sem dados para exibir</p>
    </div>
  );
}
