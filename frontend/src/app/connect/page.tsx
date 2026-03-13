"use client";

import { useState, useEffect } from "react";
import { PageHeader } from "@/components/page-header";
import { getConfig } from "@/lib/api";
import type { AppConfig } from "@/lib/api";
import { Link2, Shield, RefreshCw, CheckCircle2, AlertCircle, ExternalLink } from "lucide-react";

export default function ConnectPage() {
  const [config, setConfig] = useState<AppConfig | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});
  }, []);

  const isConnected = config && !config.mcp_mock && config.connected;
  const isMock = config?.mcp_mock;

  return (
    <>
      <PageHeader
        title="Conectar Banco"
        subtitle="Vincule sua conta bancária via Open Finance"
      />

      {/* Status card */}
      <div
        className={`rounded-2xl p-6 mb-6 animate-fade-in-up ${
          isConnected
            ? "bg-emerald-50 border border-emerald-100"
            : isMock
              ? "bg-amber-50 border border-amber-100"
              : "bg-gray-50 border border-gray-200"
        }`}
      >
        <div className="flex items-center gap-4">
          <div
            className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
              isConnected
                ? "bg-emerald-100"
                : isMock
                  ? "bg-amber-100"
                  : "bg-gray-200"
            }`}
          >
            {isConnected ? (
              <CheckCircle2 size={24} className="text-emerald-600" />
            ) : (
              <AlertCircle
                size={24}
                className={isMock ? "text-amber-600" : "text-gray-500"}
              />
            )}
          </div>
          <div>
            <div className="text-lg font-bold text-gray-900">
              {isConnected
                ? "Conta Conectada"
                : isMock
                  ? "Modo Demonstração"
                  : "Desconectado"}
            </div>
            <div className="text-sm text-gray-500">
              {isConnected
                ? "Seus dados financeiros estão sincronizados via Open Finance"
                : isMock
                  ? "O app está usando dados fictícios para demonstração"
                  : "Nenhuma conta bancária vinculada"}
            </div>
          </div>
        </div>
      </div>

      {/* Steps */}
      {!isConnected && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 animate-fade-in-up">
          <h3 className="text-sm font-bold text-gray-800 mb-5">
            Como conectar sua conta
          </h3>
          <div className="space-y-4">
            {[
              {
                step: 1,
                title: "Acesse o Pluggy Dashboard",
                desc: "Crie uma conta em dashboard.pluggy.ai e configure suas credenciais.",
              },
              {
                step: 2,
                title: "Crie uma conexão",
                desc: 'Use o conector Pluggy Bank (login: user_good, senha: password_good) para testes.',
              },
              {
                step: 3,
                title: "Copie o Item ID",
                desc: "Após conectar, copie o Item ID gerado pelo Pluggy.",
              },
              {
                step: 4,
                title: "Configure o .env",
                desc: "Cole o Item ID no arquivo .env → PLUGGY_ITEM_ID=<seu_id> e defina MCP_MOCK=false.",
              },
              {
                step: 5,
                title: "Reinicie o app",
                desc: "Reinicie a API para carregar as novas configurações.",
              },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-[#4686fe] text-white text-sm font-bold flex items-center justify-center flex-shrink-0">
                  {item.step}
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-800">
                    {item.title}
                  </div>
                  <div className="text-sm text-gray-500 mt-0.5">
                    {item.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features */}
      <div className="grid grid-cols-3 gap-4 stagger">
        {[
          {
            icon: Link2,
            title: "Open Finance",
            desc: "Integração regulada pelo Banco Central do Brasil",
            color: "text-[#4686fe]",
            bg: "bg-blue-50",
          },
          {
            icon: Shield,
            title: "Segurança",
            desc: "Criptografia de ponta e controle de acesso restrito",
            color: "text-emerald-500",
            bg: "bg-emerald-50",
          },
          {
            icon: RefreshCw,
            title: "Sincronização",
            desc: "Dados atualizados automaticamente via webhooks",
            color: "text-violet-500",
            bg: "bg-violet-50",
          },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.title}
              className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md hover:border-gray-200 transition-all"
            >
              <div
                className={`w-10 h-10 rounded-xl ${item.bg} flex items-center justify-center mb-3`}
              >
                <Icon size={18} className={item.color} />
              </div>
              <div className="text-sm font-semibold text-gray-800 mb-1">
                {item.title}
              </div>
              <div className="text-xs text-gray-500">{item.desc}</div>
            </div>
          );
        })}
      </div>
    </>
  );
}
