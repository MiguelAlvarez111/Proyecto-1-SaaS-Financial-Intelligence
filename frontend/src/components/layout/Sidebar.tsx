"use client";

import { motion } from "framer-motion";
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  TableCellsIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onExport?: () => void;
  onRefresh?: () => void;
  onOpenSettings?: () => void;
  reduceMotion?: boolean;
  /** On mobile: sidebar is a drawer. open = visible, onClose = close drawer. */
  open?: boolean;
  onClose?: () => void;
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
  open = true,
  onClose,
}: SidebarProps) {
  const handleTabChange = (tab: string) => {
    onTabChange(tab);
    onClose?.();
  };

  return (
    <>
      {/* Backdrop: mobile only, when drawer open */}
      {onClose && (
        <div
          aria-hidden="true"
          onClick={onClose}
          className={cn(
            "fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity duration-200",
            open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
          )}
          style={{ pointerEvents: open ? "auto" : "none" }}
        />
      )}
      <motion.aside
        initial={false}
        className={cn(
          "sidebar w-64 flex flex-col",
          "fixed lg:relative inset-y-0 left-0 z-50 lg:z-auto",
          "transition-transform duration-200 ease-out lg:transition-none",
          onClose && "transform lg:translate-x-0",
          onClose ? (open ? "translate-x-0" : "-translate-x-full") : "translate-x-0"
        )}
      >
        {/* Logo + close on mobile */}
        <div className="p-5 border-b border-slate-800/30 flex items-center justify-between gap-3">
          <motion.div
            initial={false}
            className="flex items-center gap-3 min-w-0"
          >
            <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
              <ChartBarIcon className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-base font-semibold text-white">Financial</h1>
              <p className="text-[11px] text-indigo-400">Intelligence</p>
            </div>
          </motion.div>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              aria-label="Close menu"
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
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
                onClick={() => handleTabChange(item.id)}
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
    </>
  );
}
