"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ChartBarIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { MetricCard } from "@/components/ui/MetricCard";
import { AreaChartComponent } from "@/components/charts/AreaChartComponent";
import { DonutChart } from "@/components/charts/DonutChart";
import { HorizontalBarChart } from "@/components/charts/HorizontalBarChart";
import { TransactionTable } from "@/components/ui/TransactionTable";
import { formatCurrency, formatNumber, chartColors } from "@/lib/utils";
import { DashboardData, Transaction } from "@/types";

// Demo data - Replace with actual API calls
const generateDemoData = (): DashboardData => {
  const dailyVolume = Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (29 - i));
    return {
      date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      volume: Math.floor(Math.random() * 2000000) + 500000,
      count: Math.floor(Math.random() * 500) + 100,
    };
  });

  const statusDistribution = [
    { status: "COMPLETED", count: 7500, percentage: 75 },
    { status: "PENDING", count: 1200, percentage: 12 },
    { status: "FAILED", count: 800, percentage: 8 },
    { status: "REFUNDED", count: 500, percentage: 5 },
  ];

  const currencyVolume = [
    { currency: "USD", amount: 45000000, count: 4500 },
    { currency: "GBP", amount: 23000000, count: 2300 },
    { currency: "EUR", amount: 22000000, count: 2200 },
    { currency: "COP", amount: 30000, count: 1000 },
  ];

  const deviceVolume = [
    { device: "Desktop", amount: 52000000, percentage: 52 },
    { device: "Mobile", amount: 48000000, percentage: 48 },
  ];

  const recentTransactions: Transaction[] = Array.from({ length: 20 }, (_, i) => ({
    id: `tx-${1000 + i}`,
    timestamp: new Date(Date.now() - i * 3600000).toISOString(),
    amount: Math.floor(Math.random() * 10000) + 100,
    currency: ["USD", "EUR", "GBP", "COP"][Math.floor(Math.random() * 4)],
    status: ["COMPLETED", "PENDING", "FAILED", "REFUNDED"][
      Math.floor(Math.random() * 4)
    ] as Transaction["status"],
    amount_usd: Math.floor(Math.random() * 10000) + 100,
    client_email: `user${i}@example.com`,
    client_device: Math.random() > 0.5 ? "desktop" : "mobile",
  }));

  return {
    kpis: {
      totalVolume: 100240000,
      totalTransactions: 10000,
      avgTicket: 10024,
      successRate: 75.2,
      volumeDelta: 12.5,
      transactionsDelta: 8.3,
      avgTicketDelta: -2.1,
    },
    dailyVolume,
    statusDistribution,
    currencyVolume,
    deviceVolume,
    recentTransactions,
    lastUpdated: new Date().toISOString(),
  };
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState<DashboardData | null>(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setData(generateDemoData());
      setLastUpdated(new Date());
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setData(generateDemoData());
      setLastUpdated(new Date());
      setIsLoading(false);
    }, 500);
  };

  const handleExport = () => {
    // TODO: Implement CSV export
    alert("Export feature coming soon!");
  };

  if (isLoading || !data) {
    return (
      <div className="flex h-screen items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
          className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  const statusChartData = data.statusDistribution.map((item) => ({
    name: item.status,
    value: item.count,
    color:
      item.status === "COMPLETED"
        ? chartColors.success
        : item.status === "FAILED"
        ? chartColors.danger
        : item.status === "PENDING"
        ? chartColors.warning
        : chartColors.info,
  }));

  const currencyChartData = data.currencyVolume.map((item) => ({
    name: item.currency,
    value: item.amount,
  }));

  const deviceChartData = data.deviceVolume.map((item, i) => ({
    name: item.device,
    value: item.amount,
    color: i === 0 ? chartColors.primary : chartColors.success,
  }));

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onRefresh={handleRefresh}
        onExport={handleExport}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header lastUpdated={lastUpdated} />

        <main className="flex-1 overflow-y-auto p-8">
          <AnimatePresence mode="wait">
            {activeTab === "overview" && (
              <motion.div
                key="overview"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-8"
              >
                {/* KPI Cards Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <MetricCard
                    title="Total Volume"
                    value={formatCurrency(data.kpis.totalVolume)}
                    delta={data.kpis.volumeDelta}
                    icon={<CurrencyDollarIcon className="w-5 h-5" />}
                    delay={0}
                  />
                  <MetricCard
                    title="Transactions"
                    value={formatNumber(data.kpis.totalTransactions)}
                    delta={data.kpis.transactionsDelta}
                    icon={<ArrowTrendingUpIcon className="w-5 h-5" />}
                    delay={0.1}
                  />
                  <MetricCard
                    title="Avg Ticket"
                    value={formatCurrency(data.kpis.avgTicket)}
                    delta={data.kpis.avgTicketDelta}
                    icon={<ChartBarIcon className="w-5 h-5" />}
                    delay={0.2}
                  />
                  <MetricCard
                    title="Success Rate"
                    value={`${data.kpis.successRate}%`}
                    icon={<CheckCircleIcon className="w-5 h-5" />}
                    delay={0.3}
                  />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
                    <AreaChartComponent
                      data={data.dailyVolume}
                      title="Daily Transaction Volume"
                      delay={0.4}
                    />
                  </div>
                  <DonutChart
                    data={statusChartData}
                    title="Status Distribution"
                    delay={0.5}
                  />
                </div>

                {/* Quick stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="glass-card text-center"
                  >
                    <p className="text-sm text-slate-400 mb-2">Max Transaction</p>
                    <p className="text-2xl font-bold text-white">$9,847.32</p>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                    className="glass-card text-center"
                  >
                    <p className="text-sm text-slate-400 mb-2">Min Transaction</p>
                    <p className="text-2xl font-bold text-white">$1.05</p>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="glass-card text-center"
                  >
                    <p className="text-sm text-slate-400 mb-2">Unique Clients</p>
                    <p className="text-2xl font-bold text-white">2,847</p>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.9 }}
                    className="glass-card text-center"
                  >
                    <p className="text-sm text-slate-400 mb-2">Mobile Share</p>
                    <p className="text-2xl font-bold text-white">48.2%</p>
                  </motion.div>
                </div>
              </motion.div>
            )}

            {activeTab === "analysis" && (
              <motion.div
                key="analysis"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-8"
              >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <HorizontalBarChart
                    data={currencyChartData}
                    title="Volume by Currency (Original)"
                    delay={0}
                  />
                  <HorizontalBarChart
                    data={deviceChartData}
                    title="Volume by Device (USD)"
                    delay={0.1}
                  />
                </div>

                {/* Status Summary Table */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="glass-card"
                >
                  <h3 className="text-lg font-semibold text-white mb-6">
                    Status Breakdown
                  </h3>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Count</th>
                        <th>Percentage</th>
                        <th>Progress</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.statusDistribution.map((item) => (
                        <tr key={item.status}>
                          <td>
                            <span
                              className={`badge ${
                                item.status === "COMPLETED"
                                  ? "badge-success"
                                  : item.status === "FAILED"
                                  ? "badge-danger"
                                  : item.status === "PENDING"
                                  ? "badge-warning"
                                  : "badge-info"
                              }`}
                            >
                              {item.status}
                            </span>
                          </td>
                          <td className="text-white font-semibold">
                            {formatNumber(item.count)}
                          </td>
                          <td className="text-slate-300">{item.percentage}%</td>
                          <td>
                            <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${item.percentage}%` }}
                                transition={{ duration: 1, delay: 0.3 }}
                                className={`h-full rounded-full ${
                                  item.status === "COMPLETED"
                                    ? "bg-emerald-500"
                                    : item.status === "FAILED"
                                    ? "bg-red-500"
                                    : item.status === "PENDING"
                                    ? "bg-orange-500"
                                    : "bg-blue-500"
                                }`}
                              />
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </motion.div>
              </motion.div>
            )}

            {activeTab === "transactions" && (
              <motion.div
                key="transactions"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <TransactionTable
                  transactions={data.recentTransactions}
                  delay={0}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
