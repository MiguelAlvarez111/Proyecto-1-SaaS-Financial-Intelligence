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
  onOpenSettings?: () => void;
  reduceMotion?: boolean;
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
  onOpenSettings,
  reduceMotion = false,
}: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: reduceMotion ? 0 : 0.5 }}
      className="sidebar w-64 flex flex-col"
    >
      {/* Logo */}
      <div className="p-5 border-b border-slate-800/30">
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring" }}
          className="flex items-center gap-3"
        >
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center">
            <ChartBarIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-white">Financial</h1>
            <p className="text-[11px] text-indigo-400">Intelligence</p>
          </div>
        </motion.div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 mb-3 px-3">
          Dashboard
        </p>
        <ul className="space-y-1">
          {navItems.map((item, index) => (
            <motion.li
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.3, delay: reduceMotion ? 0 : 0.1 + index * 0.1 }}
            >
              <button
                onClick={() => onTabChange(item.id)}
                className={cn(
                  "sidebar-item w-full",
                  activeTab === item.id && "active"
                )}
              >
                <item.icon className="w-[18px] h-[18px]" />
                <span>{item.label}</span>
              </button>
            </motion.li>
          ))}
        </ul>

        <div className="mt-6">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 mb-3 px-3">
            Actions
          </p>
          <ul className="space-y-1">
            <motion.li
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.3, delay: reduceMotion ? 0 : 0.4 }}
            >
              <button
                onClick={onRefresh}
                className="sidebar-item w-full group"
              >
                <ArrowPathIcon className="w-[18px] h-[18px] group-hover:rotate-180 transition-transform duration-500" />
                <span>Refresh Data</span>
              </button>
            </motion.li>
            <motion.li
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.3, delay: reduceMotion ? 0 : 0.5 }}
            >
              <button onClick={onExport} className="sidebar-item w-full">
                <ArrowDownTrayIcon className="w-[18px] h-[18px]" />
                <span>Export CSV</span>
              </button>
            </motion.li>
          </ul>
        </div>
      </nav>

      {/* Footer: Settings opens modal */}
      <div className="p-4 border-t border-slate-800/30">
        <button
          type="button"
          onClick={() => onOpenSettings?.()}
          className="sidebar-item w-full"
        >
          <Cog6ToothIcon className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </motion.aside>
  );
}
