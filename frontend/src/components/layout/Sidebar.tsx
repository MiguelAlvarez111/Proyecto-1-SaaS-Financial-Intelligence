"use client";

import { motion } from "framer-motion";
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  TableCellsIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onExport?: () => void;
  onRefresh?: () => void;
}

const navItems = [
  { id: "overview", label: "Overview", icon: ChartBarIcon },
  { id: "analysis", label: "Analysis", icon: CurrencyDollarIcon },
  { id: "transactions", label: "Transactions", icon: TableCellsIcon },
];

export function Sidebar({
  activeTab,
  onTabChange,
  onExport,
  onRefresh,
}: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="sidebar w-64 flex flex-col"
    >
      {/* Logo */}
      <div className="p-6 border-b border-slate-800/50">
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring" }}
          className="flex items-center gap-3"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-glow">
            <ChartBarIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Financial</h1>
            <p className="text-xs text-primary-400">Intelligence</p>
          </div>
        </motion.div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 px-4">
          Dashboard
        </p>
        <ul className="space-y-2">
          {navItems.map((item, index) => (
            <motion.li
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
            >
              <button
                onClick={() => onTabChange(item.id)}
                className={cn(
                  "sidebar-item w-full",
                  activeTab === item.id && "active"
                )}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            </motion.li>
          ))}
        </ul>

        <div className="mt-8">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 px-4">
            Actions
          </p>
          <ul className="space-y-2">
            <motion.li
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <button
                onClick={onRefresh}
                className="sidebar-item w-full group"
              >
                <ArrowPathIcon className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
                <span className="font-medium">Refresh Data</span>
              </button>
            </motion.li>
            <motion.li
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <button onClick={onExport} className="sidebar-item w-full">
                <ArrowDownTrayIcon className="w-5 h-5" />
                <span className="font-medium">Export CSV</span>
              </button>
            </motion.li>
          </ul>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800/50">
        <button className="sidebar-item w-full">
          <Cog6ToothIcon className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
        <div className="mt-4 px-4">
          <p className="text-xs text-slate-500">v5.0 Gold Master</p>
          <p className="text-xs text-slate-600">Next.js + Framer Motion</p>
        </div>
      </div>
    </motion.aside>
  );
}
