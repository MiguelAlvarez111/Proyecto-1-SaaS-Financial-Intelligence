"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { MetricCard } from "@/components/ui/MetricCard";
import { TransactionTable } from "@/components/ui/TransactionTable";
import { FilterBar } from "@/components/ui/FilterBar";
import { AreaChartComponent } from "@/components/charts/AreaChartComponent";
import { DonutChart } from "@/components/charts/DonutChart";
import { HorizontalBarChart } from "@/components/charts/HorizontalBarChart";
import { useDashboard, exportTransactions, fetchTransactionsPage } from "@/hooks/useDashboard";
import { formatCurrency, formatNumber, chartColors } from "@/lib/utils";
import type { DashboardData, FilterState, Transaction } from "@/types";

const STORAGE_COMPACT = "dashboard-compact";
const STORAGE_REDUCE_MOTION = "dashboard-reduce-motion";

const DEMO_DATA: DashboardData = {
  kpis: {
    totalVolume: 100_200_000,
    totalTransactions: 10_000,
    avgTicket: 10_024,
    successRate: 75.2,
    volumeDelta: 12.5,
    transactionsDelta: 8.3,
    avgTicketDelta: 2.1,
  },
  dailyVolume: [
    { date: "Jan 25", volume: 3_200_000, count: 320 },
    { date: "Jan 26", volume: 4_100_000, count: 410 },
    { date: "Jan 27", volume: 2_800_000, count: 280 },
    { date: "Jan 28", volume: 5_100_000, count: 510 },
    { date: "Jan 29", volume: 4_500_000, count: 450 },
    { date: "Jan 30", volume: 6_200_000, count: 620 },
  ],
  statusDistribution: [
    { status: "COMPLETED", count: 7520, percentage: 75.2 },
    { status: "FAILED", count: 1200, percentage: 12 },
    { status: "PENDING", count: 980, percentage: 9.8 },
    { status: "REFUNDED", count: 300, percentage: 3 },
  ],
  currencyVolume: [
    { currency: "USD", amount: 60_000_000, count: 6000 },
    { currency: "EUR", amount: 25_000_000, count: 2500 },
    { currency: "GBP", amount: 12_000_000, count: 1200 },
    { currency: "COP", amount: 3_200_000, count: 300 },
  ],
  deviceVolume: [
    { device: "Mobile", amount: 55_000_000, percentage: 55 },
    { device: "Desktop", amount: 35_000_000, percentage: 35 },
    { device: "Tablet", amount: 10_200_000, percentage: 10.2 },
  ],
  recentTransactions: [
    { id: "1", timestamp: new Date(Date.now() - 3600000).toISOString(), amount: 1250.5, currency: "USD", status: "COMPLETED", amount_usd: 1250.5, client_email: "demo@example.com", client_device: "mobile" },
    { id: "2", timestamp: new Date(Date.now() - 7200000).toISOString(), amount: 890.25, currency: "EUR", status: "COMPLETED", amount_usd: 961.47, client_email: "demo@example.com", client_device: "desktop" },
    { id: "3", timestamp: new Date(Date.now() - 10800000).toISOString(), amount: 500, currency: "USD", status: "PENDING", amount_usd: 500, client_email: "demo@example.com", client_device: "tablet" },
    { id: "4", timestamp: new Date(Date.now() - 14400000).toISOString(), amount: 2000, currency: "GBP", status: "FAILED", amount_usd: 2540, client_email: "demo@example.com", client_device: "mobile" },
    { id: "5", timestamp: new Date(Date.now() - 18000000).toISOString(), amount: 75000, currency: "COP", status: "COMPLETED", amount_usd: 18.75, client_email: "demo@example.com", client_device: "desktop" },
  ],
  lastUpdated: new Date().toISOString(),
};

const STATUS_COLORS = [
  chartColors.success,
  chartColors.danger,
  chartColors.warning,
  chartColors.info,
];

function getDefaultFilters(): FilterState {
  const end = new Date();
  const start = new Date();
  start.setMonth(start.getMonth() - 1);
  return {
    currencies: [],
    statuses: [],
    dateRange: { start, end },
    quickFilter: "",
  };
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [filters, setFilters] = useState<FilterState>(getDefaultFilters);
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearchingHint, setShowSearchingHint] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [compactMode, setCompactMode] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [ledgerTransactions, setLedgerTransactions] = useState<Transaction[]>([]);
  const [ledgerOffset, setLedgerOffset] = useState(0);
  const [ledgerHasMore, setLedgerHasMore] = useState(true);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerLoadingMore, setLedgerLoadingMore] = useState(false);
  const [ledgerError, setLedgerError] = useState<string | null>(null);
  const ledgerInitialTried = useRef(false);

  useEffect(() => {
    if (activeTab !== "transactions") return;
    if (ledgerTransactions.length > 0) return;
    if (ledgerLoading) return;
    if (ledgerInitialTried.current) return;
    ledgerInitialTried.current = true;
    setLedgerLoading(true);
    setLedgerError(null);
    fetchTransactionsPage(50, 0)
      .then((list) => {
        setLedgerTransactions(list);
        setLedgerOffset(list.length);
        setLedgerHasMore(list.length >= 50);
      })
      .catch((err) => {
        setLedgerError(err instanceof Error ? err.message : "Failed to load");
      })
      .finally(() => setLedgerLoading(false));
  }, [activeTab, ledgerTransactions.length, ledgerLoading]);

  const loadMoreTransactions = useCallback(() => {
    if (ledgerLoadingMore || !ledgerHasMore) return;
    setLedgerLoadingMore(true);
    fetchTransactionsPage(50, ledgerOffset)
      .then((list) => {
        setLedgerTransactions((prev) => {
          const ids = new Set(prev.map((t) => t.id));
          const newOnes = list.filter((t) => !ids.has(t.id));
          return [...prev, ...newOnes];
        });
        setLedgerOffset((prev) => prev + list.length);
        setLedgerHasMore(list.length >= 50);
      })
      .catch(() => setLedgerHasMore(false))
      .finally(() => setLedgerLoadingMore(false));
  }, [ledgerLoadingMore, ledgerHasMore, ledgerOffset]);

  const retryLedger = useCallback(() => {
    setLedgerLoading(true);
    setLedgerError(null);
    fetchTransactionsPage(50, 0)
      .then((list) => {
        setLedgerTransactions(list);
        setLedgerOffset(list.length);
        setLedgerHasMore(list.length >= 50);
      })
      .catch((err) => {
        setLedgerError(err instanceof Error ? err.message : "Failed to load");
      })
      .finally(() => setLedgerLoading(false));
  }, []);

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    if (value.trim().length > 0 && activeTab !== "transactions") {
      setActiveTab("transactions");
      setShowSearchingHint(true);
      requestAnimationFrame(() => {
        searchInputRef.current?.focus();
      });
    }
  }, [activeTab]);

  useEffect(() => {
    if (!showSearchingHint) return;
    const t = setTimeout(() => setShowSearchingHint(false), 1200);
    return () => clearTimeout(t);
  }, [showSearchingHint]);

  useEffect(() => {
    try {
      const c = localStorage.getItem(STORAGE_COMPACT);
      const r = localStorage.getItem(STORAGE_REDUCE_MOTION);
      if (c !== null) setCompactMode(c === "true");
      if (r !== null) setReduceMotion(r === "true");
    } catch (_) {}
  }, []);

  const { data, isLoading, error, refresh, lastUpdated } = useDashboard(filters);

  const displayData: DashboardData = data ?? DEMO_DATA;
  const isDemo = !data;

  const handleExport = useCallback(async () => {
    const blob = await exportTransactions(filters);
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transactions-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const k = displayData.kpis;
  const donutData = displayData.statusDistribution.map((s, i) => ({
    name: s.status,
    value: s.count,
    color: STATUS_COLORS[i % STATUS_COLORS.length],
  }));
  const currencyBarData = displayData.currencyVolume.map((c) => ({
    name: c.currency,
    value: c.amount,
  }));
  const deviceBarData = displayData.deviceVolume.map((d) => ({
    name: d.device,
    value: d.amount,
  }));

  const toggleCompact = useCallback(() => {
    setCompactMode((v) => {
      const next = !v;
      try { localStorage.setItem(STORAGE_COMPACT, String(next)); } catch (_) {}
      return next;
    });
  }, []);

  const toggleReduceMotion = useCallback(() => {
    setReduceMotion((v) => {
      const next = !v;
      try { localStorage.setItem(STORAGE_REDUCE_MOTION, String(next)); } catch (_) {}
      return next;
    });
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onExport={handleExport}
        onRefresh={refresh}
        onOpenSettings={() => setShowSettingsModal(true)}
        reduceMotion={reduceMotion}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          lastUpdated={lastUpdated ?? new Date()}
          searchQuery={searchQuery}
          onSearchChange={handleSearchChange}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onOpenSettings={() => setShowSettingsModal(true)}
          reduceMotion={reduceMotion}
          searchInputRef={searchInputRef}
        />
        <main
          className={`flex-1 overflow-auto ${compactMode ? "p-5" : "p-8"}`}
        >
          <FilterBar
            filters={filters}
            onChange={setFilters}
            className={compactMode ? "mb-6" : "mb-10"}
          />

          {error && (
            <div className="mb-6 px-4 py-3 rounded-lg bg-amber-500/8 border border-amber-500/15 text-amber-300 text-[13px] space-y-1">
              <p><strong>Backend unavailable.</strong> {error}. Showing demo data.</p>
              <p className="text-slate-500 text-[12px] mt-2">
                To use live data, start the backend:{" "}
                <code className="bg-slate-800/60 px-2 py-0.5 rounded text-slate-400">
                  cd backend && uvicorn main:app --reload --port 8000
                </code>
              </p>
            </div>
          )}
          {isDemo && !error && (
            <div className="mb-6 px-4 py-3 rounded-lg bg-indigo-500/8 border border-indigo-500/15 text-indigo-300 text-[13px]">
              Connect the backend at <code className="text-slate-300">localhost:8000</code> for live data. Showing demo data.
            </div>
          )}

          {activeTab === "overview" && (
            <div className={compactMode ? "space-y-6" : "space-y-10"}>
              {/* KPI Grid - "Capítulo 1" */}
              <section>
                <div
                  className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 ${compactMode ? "gap-4" : "gap-6"}`}
                >
                  <MetricCard
                    title="Total Volume"
                    value={formatCurrency(k.totalVolume)}
                    delta={k.volumeDelta}
                    delay={0.1}
                    reduceMotion={reduceMotion}
                  />
                  <MetricCard
                    title="Transactions"
                    value={formatNumber(k.totalTransactions)}
                    delta={k.transactionsDelta}
                    delay={0.2}
                    reduceMotion={reduceMotion}
                  />
                  <MetricCard
                    title="Average ticket"
                    value={formatCurrency(k.avgTicket)}
                    delta={k.avgTicketDelta}
                    delay={0.3}
                    reduceMotion={reduceMotion}
                  />
                  <MetricCard
                    title="Success Rate"
                    value={`${k.successRate}%`}
                    delta={k.successRate >= 70 ? 2.1 : -1.5}
                    delay={0.4}
                    reduceMotion={reduceMotion}
                  />
                </div>
              </section>

              {/* Charts Grid - "Capítulo 2" */}
              <section>
                <div
                  className={`grid grid-cols-1 xl:grid-cols-2 ${compactMode ? "gap-5" : "gap-8"}`}
                >
                  <AreaChartComponent
                    data={displayData.dailyVolume}
                    title="Daily volume (USD)"
                    delay={0.2}
                    reduceMotion={reduceMotion}
                  />
                  <DonutChart
                    data={donutData}
                    title="Status distribution"
                    centerValue={formatNumber(displayData.statusDistribution.reduce((a, s) => a + s.count, 0))}
                    centerLabel="Transactions"
                    delay={0.3}
                    reduceMotion={reduceMotion}
                  />
                </div>
              </section>
            </div>
          )}

          {activeTab === "analysis" && (
            <div className="space-y-8">
              <p className="text-slate-500 text-[13px]">
                Breakdown by currency and device. For KPIs and time trends, use Overview.
              </p>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <HorizontalBarChart
                  data={currencyBarData}
                  title="Volume by currency"
                  formatAsCurrency
                  reduceMotion={reduceMotion}
                />
                <HorizontalBarChart
                  data={deviceBarData}
                  title="Volume by device"
                  formatAsCurrency
                  reduceMotion={reduceMotion}
                />
              </div>
            </div>
          )}

          {activeTab === "transactions" && (
            <div className="max-w-full">
              <TransactionTable
                transactions={ledgerTransactions}
                searchQuery={searchQuery}
                delay={reduceMotion ? 0 : 0.2}
                reduceMotion={reduceMotion}
                loading={ledgerLoading}
                error={ledgerError}
                hasMore={ledgerHasMore}
                loadingMore={ledgerLoadingMore}
                onLoadMore={loadMoreTransactions}
                onRetry={retryLedger}
                showSearchingHint={showSearchingHint}
              />
            </div>
          )}
        </main>
      </div>

      {/* Settings modal: Compact mode + Reduce motion */}
      {showSettingsModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowSettingsModal(false)}
        >
          <div
            className="w-full max-w-md rounded-xl bg-slate-900 border border-slate-700/80 shadow-2xl p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white">Settings</h2>
              <button
                type="button"
                onClick={() => setShowSettingsModal(false)}
                className="text-slate-400 hover:text-white transition-colors text-sm font-medium"
              >
                Close
              </button>
            </div>
            <div className="space-y-4">
              <label className="flex items-center justify-between gap-4 cursor-pointer">
                <span className="text-[13px] text-slate-300">Compact mode</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={compactMode}
                  onClick={toggleCompact}
                  className={`relative w-10 h-5 rounded-full transition-colors ${
                    compactMode ? "bg-indigo-600" : "bg-slate-700"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      compactMode ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
              </label>
              <label className="flex items-center justify-between gap-4 cursor-pointer">
                <span className="text-[13px] text-slate-300">Reduce motion</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={reduceMotion}
                  onClick={toggleReduceMotion}
                  className={`relative w-10 h-5 rounded-full transition-colors ${
                    reduceMotion ? "bg-indigo-600" : "bg-slate-700"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      reduceMotion ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
              </label>
            </div>
            <p className="mt-4 text-[11px] text-slate-500">
              Preferences are saved in this browser.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
