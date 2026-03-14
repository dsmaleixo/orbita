"use client";

import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { PageHeader } from "@/components/page-header";
import {
  getConfig,
  createConnectToken,
  saveConnection,
  disconnectItem,
} from "@/lib/api";
import type { AppConfig } from "@/lib/api";
import {
  Link2,
  Shield,
  RefreshCw,
  CheckCircle2,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react";

const PluggyConnect = dynamic(
  () =>
    import("react-pluggy-connect").then((mod) => ({
      default: mod.PluggyConnect,
    })),
  { ssr: false }
);

export default function ConnectPage() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [connectToken, setConnectToken] = useState<string | null>(null);
  const [showWidget, setShowWidget] = useState(false);
  const [loading, setLoading] = useState(false);
  const [removing, setRemoving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});
  }, []);

  const itemIds = config?.item_ids ?? [];

  const handleConnect = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { accessToken } = await createConnectToken();
      setConnectToken(accessToken);
      setShowWidget(true);
    } catch {
      setError(
        "Erro ao iniciar conexão. Verifique as credenciais Pluggy no .env."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSuccess = useCallback(
    async (data: { item: { id: string } }) => {
      setShowWidget(false);
      setConnectToken(null);
      try {
        await saveConnection(data.item.id);
        const newConfig = await getConfig();
        setConfig(newConfig);
      } catch {
        setError(
          `Conexão realizada, mas houve erro ao salvar. Item ID: ${data.item.id}`
        );
      }
    },
    []
  );

  const handleClose = useCallback(() => {
    setShowWidget(false);
    setConnectToken(null);
  }, []);

  const handleRemove = useCallback(async (itemId: string) => {
    setRemoving(itemId);
    setError(null);
    try {
      await disconnectItem(itemId);
      const newConfig = await getConfig();
      setConfig(newConfig);
    } catch {
      setError("Erro ao remover conexão.");
    } finally {
      setRemoving(null);
    }
  }, []);

  return (
    <>
      <PageHeader
        title="Conectar Banco"
        subtitle="Vincule suas contas bancárias via Open Finance"
      />

      {/* Connected accounts */}
      {itemIds.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 animate-fade-in-up">
          <h3 className="text-sm font-bold text-gray-800 mb-4">
            Contas conectadas ({itemIds.length})
          </h3>
          <div className="space-y-3">
            {itemIds.map((id) => (
              <div
                key={id}
                className="flex items-center justify-between bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-emerald-600" />
                  <span className="text-sm font-mono text-gray-700">
                    {id.slice(0, 8)}...{id.slice(-4)}
                  </span>
                </div>
                <button
                  onClick={() => handleRemove(id)}
                  disabled={removing === id}
                  className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
                  title="Remover conexão"
                >
                  {removing === id ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Trash2 size={16} />
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add account */}
      <div className="bg-white rounded-2xl border border-gray-100 p-8 mb-6 animate-fade-in-up text-center">
        <h3 className="text-lg font-bold text-gray-800 mb-2">
          {itemIds.length > 0
            ? "Adicionar outra conta"
            : "Conecte sua conta bancária"}
        </h3>
        <p className="text-sm text-gray-500 mb-6 max-w-md mx-auto">
          {itemIds.length > 0
            ? "Conecte mais contas para ter uma visão completa das suas finanças."
            : "Selecione seu banco e autentique-se com segurança. Seus dados serão sincronizados automaticamente via Open Finance."}
        </p>

        {error && (
          <div className="bg-red-50 border border-red-100 rounded-xl p-4 mb-4 text-sm text-red-700 max-w-md mx-auto">
            {error}
          </div>
        )}

        <button
          onClick={handleConnect}
          disabled={loading}
          className="inline-flex items-center gap-2 px-6 py-3 bg-[#4686fe] text-white font-semibold rounded-xl hover:bg-[#3570e0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Preparando...
            </>
          ) : (
            <>
              {itemIds.length > 0 ? (
                <Plus size={18} />
              ) : (
                <Link2 size={18} />
              )}
              {itemIds.length > 0 ? "Adicionar Conta" : "Conectar Banco"}
            </>
          )}
        </button>
      </div>

      {/* Pluggy Connect Widget */}
      {showWidget && connectToken && (
        <PluggyConnect
          connectToken={connectToken}
          onSuccess={handleSuccess}
          onError={() => {
            setError("Erro durante a conexão. Tente novamente.");
            setShowWidget(false);
            setConnectToken(null);
          }}
          onClose={handleClose}
        />
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
