const API_BASE = "/api";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

// Types
export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  account_id?: string;
}

export interface Balance {
  account_id: string;
  balance: number;
  currency: string;
}

export interface Account {
  account_id: string;
  account_type: string;
  status: string;
  name?: string;
  number?: string;
  balance?: number;
}

export interface Summary {
  income: number;
  expenses: number;
  net: number;
  count: number;
}

export interface MonthlyData {
  month: string;
  key: string;
  income: number;
  expenses: number;
  net: number;
}

export interface CategoryTotals {
  [category: string]: number;
}

export interface RecurringItem {
  description: string;
  avg_amount: number;
  occurrences: number;
  months: number;
  last_date: string;
  category: string;
}

export interface BalancePoint {
  date: string;
  balance: number;
}

export interface ChatResponse {
  intent: string;
  response: string;
  citations: Citation[];
}

export interface Citation {
  source?: string;
  page?: number;
  passage?: string;
  url?: string;
}

export interface AppConfig {
  mcp_mock: boolean;
  ollama_model: string;
  connected: boolean;
}

// API functions
export async function getConfig(): Promise<AppConfig> {
  return fetchJSON("/config");
}

export async function getTransactions(start?: string, end?: string): Promise<Transaction[]> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return fetchJSON(`/transactions?${params}`);
}

export async function getBalances(): Promise<Balance[]> {
  return fetchJSON("/balances");
}

export async function getAccounts(): Promise<Account[]> {
  return fetchJSON("/accounts");
}

export async function getSummary(start?: string, end?: string): Promise<Summary> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return fetchJSON(`/summary?${params}`);
}

export async function getMonthlyData(start?: string, end?: string, months = 6): Promise<MonthlyData[]> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  params.set("months", String(months));
  return fetchJSON(`/monthly?${params}`);
}

export async function getCategoryTotals(start?: string, end?: string): Promise<CategoryTotals> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return fetchJSON(`/categories?${params}`);
}

export async function getRecurring(start?: string, end?: string): Promise<RecurringItem[]> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return fetchJSON(`/recurring?${params}`);
}

export async function getBalanceHistory(start?: string, end?: string): Promise<BalancePoint[]> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return fetchJSON(`/balance-history?${params}`);
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return fetchJSON("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
