"use client";

import { useState } from "react";
import { PageHeader } from "@/components/page-header";
import { formatCurrency } from "@/lib/utils";
import { Flag, Plus, Target, TrendingUp, X } from "lucide-react";

interface Goal {
  id: string;
  name: string;
  target: number;
  current: number;
  deadline: string;
}

const DEFAULT_GOALS: Goal[] = [
  {
    id: "1",
    name: "Reserva de Emergência",
    target: 15000,
    current: 8500,
    deadline: "2026-12-31",
  },
  {
    id: "2",
    name: "Viagem",
    target: 5000,
    current: 2200,
    deadline: "2026-07-01",
  },
  {
    id: "3",
    name: "Notebook Novo",
    target: 4000,
    current: 3600,
    deadline: "2026-04-15",
  },
];

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>(DEFAULT_GOALS);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [current, setCurrent] = useState("");
  const [deadline, setDeadline] = useState("");

  const addGoal = () => {
    if (!name || !target) return;
    setGoals((prev) => [
      ...prev,
      {
        id: String(Date.now()),
        name,
        target: Number(target),
        current: Number(current) || 0,
        deadline,
      },
    ]);
    setName("");
    setTarget("");
    setCurrent("");
    setDeadline("");
    setShowForm(false);
  };

  const totalTarget = goals.reduce((s, g) => s + g.target, 0);
  const totalCurrent = goals.reduce((s, g) => s + g.current, 0);

  return (
    <>
      <PageHeader title="Metas" subtitle="Acompanhe o progresso dos seus objetivos financeiros">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1.5 px-4 py-2 bg-[#4686fe] text-white text-sm font-medium rounded-xl hover:bg-[#3570e0] transition-colors shadow-sm"
        >
          <Plus size={16} />
          Nova Meta
        </button>
      </PageHeader>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6 stagger">
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <Flag size={18} className="text-[#4686fe]" />
            </div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Metas Ativas
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900">{goals.length}</div>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
              <TrendingUp size={18} className="text-emerald-500" />
            </div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Total Acumulado
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900">
            {formatCurrency(totalCurrent)}
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-violet-50 flex items-center justify-center">
              <Target size={18} className="text-violet-500" />
            </div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Progresso Geral
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900">
            {totalTarget > 0 ? ((totalCurrent / totalTarget) * 100).toFixed(0) : 0}%
          </div>
        </div>
      </div>

      {/* Add form */}
      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-6 animate-fade-in-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-gray-800">Nova Meta</h3>
            <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
              <X size={16} />
            </button>
          </div>
          <div className="grid grid-cols-4 gap-3">
            <input
              type="text"
              placeholder="Nome da meta"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="text-sm rounded-xl border border-gray-200 px-3 py-2 focus:outline-none focus:border-[#4686fe] focus:ring-2 focus:ring-[#4686fe]/10"
            />
            <input
              type="number"
              placeholder="Valor alvo"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="text-sm rounded-xl border border-gray-200 px-3 py-2 focus:outline-none focus:border-[#4686fe] focus:ring-2 focus:ring-[#4686fe]/10"
            />
            <input
              type="number"
              placeholder="Valor atual"
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              className="text-sm rounded-xl border border-gray-200 px-3 py-2 focus:outline-none focus:border-[#4686fe] focus:ring-2 focus:ring-[#4686fe]/10"
            />
            <div className="flex gap-2">
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="flex-1 text-sm rounded-xl border border-gray-200 px-3 py-2 focus:outline-none focus:border-[#4686fe] focus:ring-2 focus:ring-[#4686fe]/10"
              />
              <button
                onClick={addGoal}
                className="px-4 py-2 bg-[#4686fe] text-white text-sm font-medium rounded-xl hover:bg-[#3570e0] transition-colors"
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Goal cards */}
      <div className="space-y-3 stagger">
        {goals.map((goal) => {
          const pct = goal.target > 0 ? (goal.current / goal.target) * 100 : 0;
          const remaining = goal.target - goal.current;
          const isComplete = pct >= 100;
          return (
            <div
              key={goal.id}
              className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md hover:border-gray-200 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      isComplete ? "bg-emerald-50" : "bg-blue-50"
                    }`}
                  >
                    {isComplete ? (
                      <span className="text-lg">🎉</span>
                    ) : (
                      <Flag
                        size={18}
                        className="text-[#4686fe]"
                      />
                    )}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-gray-800">
                      {goal.name}
                    </div>
                    {goal.deadline && (
                      <div className="text-[11px] text-gray-400">
                        Prazo: {new Date(goal.deadline + "T00:00:00").toLocaleDateString("pt-BR")}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-gray-800 tabular-nums">
                    {formatCurrency(goal.current)}{" "}
                    <span className="text-gray-400 font-normal">
                      / {formatCurrency(goal.target)}
                    </span>
                  </div>
                  {!isComplete && (
                    <div className="text-[11px] text-gray-400">
                      Faltam {formatCurrency(remaining)}
                    </div>
                  )}
                </div>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    isComplete ? "bg-emerald-400" : "bg-[#4686fe]"
                  }`}
                  style={{ width: `${Math.min(pct, 100)}%` }}
                />
              </div>
              <div className="text-[11px] text-gray-400 mt-1.5 text-right">
                {pct.toFixed(0)}% completo
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
