"use client";

import { motion } from "framer-motion";
import { MagnifyingGlassIcon, BellIcon } from "@heroicons/react/24/outline";
import { getTimeAgo } from "@/lib/utils";

interface HeaderProps {
  lastUpdated: Date;
}

export function Header({ lastUpdated }: HeaderProps) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="h-16 flex items-center justify-between px-8 border-b border-slate-800/50 bg-dark-900/50 backdrop-blur-xl"
    >
      {/* Left side - Title */}
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-xl font-bold text-white">Dashboard</h1>
          <p className="text-xs text-slate-400">
            Real-time transaction analytics
          </p>
        </div>
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative hidden md:block">
          <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search transactions..."
            className="input-glass pl-10 w-64 text-sm"
          />
        </div>

        {/* Live indicator */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: "spring" }}
          className="live-indicator"
        >
          <span className="live-dot"></span>
          <span>Live • {getTimeAgo(lastUpdated)}</span>
        </motion.div>

        {/* Notifications */}
        <button className="relative p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
          <BellIcon className="w-5 h-5 text-slate-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
        </button>

        {/* Avatar */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center cursor-pointer"
        >
          <span className="text-sm font-semibold text-white">MA</span>
        </motion.div>
      </div>
    </motion.header>
  );
}
