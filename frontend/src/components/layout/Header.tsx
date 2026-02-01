"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  MagnifyingGlassIcon,
  BellIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { getTimeAgo } from "@/lib/utils";

const MOCK_NOTIFICATIONS = [
  { id: "1", text: "API latency improved", time: "2m ago" },
  { id: "2", text: "New refund detected", time: "Today" },
];

interface HeaderProps {
  lastUpdated: Date;
  searchQuery?: string;
  onSearchChange?: (value: string) => void;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onOpenSettings?: () => void;
  reduceMotion?: boolean;
  searchInputRef?: React.RefObject<HTMLInputElement | null>;
}

export function Header({
  lastUpdated,
  searchQuery = "",
  onSearchChange,
  activeTab = "overview",
  onTabChange,
  onOpenSettings,
  reduceMotion = false,
  searchInputRef,
}: HeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAvatarMenu, setShowAvatarMenu] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const avatarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (showNotifications && notifRef.current && !notifRef.current.contains(target))
        setShowNotifications(false);
      if (showAvatarMenu && avatarRef.current && !avatarRef.current.contains(target))
        setShowAvatarMenu(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showNotifications, showAvatarMenu]);

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: reduceMotion ? 0 : 0.5 }}
      className="h-14 flex items-center justify-between px-8 border-b border-slate-800/30 bg-slate-950/80 backdrop-blur-md"
    >
      {/* Left side - Title */}
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-base font-medium text-white">Dashboard</h1>
          <p className="text-[11px] text-slate-500">
            Real-time transaction analytics
          </p>
        </div>
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-3">
        {/* Search: real search on Transaction Ledger; typing auto-switches to Transactions (handled in page) */}
        <div className="relative hidden md:block">
          <MagnifyingGlassIcon className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search transactions…"
            value={searchQuery}
            onChange={(e) => onSearchChange?.(e.target.value)}
            className="h-10 w-60 rounded-lg bg-slate-900/60 border border-white/5 text-[13px] text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/40 focus:ring-2 focus:ring-indigo-500/20 transition-all duration-150"
            style={{ paddingLeft: "2.5rem", paddingRight: "1rem" }}
          />
        </div>

        {/* Live indicator */}
        <motion.div
          initial={reduceMotion ? false : { scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: reduceMotion ? 0 : 0.3, type: "spring" }}
          className="flex items-center gap-2 px-2.5 py-1.5 rounded-md text-[11px] font-medium bg-emerald-500/8 border border-emerald-500/15 text-emerald-400"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Live • {getTimeAgo(lastUpdated)}</span>
        </motion.div>

        {/* Notifications: popover real */}
        <div className="relative" ref={notifRef}>
          <button
            type="button"
            onClick={() => { setShowNotifications((v) => !v); setShowAvatarMenu(false); }}
            className="relative p-2 rounded-lg bg-slate-800/40 hover:bg-slate-800/60 transition-colors"
          >
            <BellIcon className="w-4 h-4 text-slate-400" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>
          </button>
          {showNotifications && (
            <div className="absolute right-0 top-full mt-1 w-72 rounded-lg bg-slate-900 border border-slate-700/80 shadow-xl py-2 z-30">
              <p className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500 border-b border-slate-800">
                Notifications
              </p>
              {MOCK_NOTIFICATIONS.length === 0 ? (
                <p className="px-3 py-4 text-[13px] text-slate-500">No new notifications</p>
              ) : (
                <ul className="max-h-64 overflow-auto">
                  {MOCK_NOTIFICATIONS.map((n) => (
                    <li
                      key={n.id}
                      className="px-3 py-2.5 text-[13px] text-slate-300 hover:bg-slate-800/60 border-b border-slate-800/50 last:border-0 flex items-start justify-between gap-2"
                    >
                      <span>{n.text}</span>
                      <span className="text-[11px] text-slate-500 shrink-0">{n.time}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Avatar: dropdown real (Profile, Settings, Sign out) */}
        <div className="relative" ref={avatarRef}>
          <button
            type="button"
            onClick={() => { setShowAvatarMenu((v) => !v); setShowNotifications(false); }}
            className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center cursor-pointer hover:bg-indigo-500 transition-colors"
          >
            <span className="text-[12px] font-medium text-white">MA</span>
          </button>
          {showAvatarMenu && (
            <div className="absolute right-0 top-full mt-1 w-48 rounded-lg bg-slate-900 border border-slate-700/80 shadow-xl py-1 z-30">
              <button
                type="button"
                className="w-full flex items-center gap-2 px-3 py-2 text-[13px] text-slate-300 hover:bg-slate-800/60 text-left"
              >
                <UserCircleIcon className="w-4 h-4 text-slate-500" />
                Profile
              </button>
              <button
                type="button"
                onClick={() => { onOpenSettings?.(); setShowAvatarMenu(false); }}
                className="w-full flex items-center gap-2 px-3 py-2 text-[13px] text-slate-300 hover:bg-slate-800/60 text-left"
              >
                <Cog6ToothIcon className="w-4 h-4 text-slate-500" />
                Settings
              </button>
              <button
                type="button"
                className="w-full flex items-center gap-2 px-3 py-2 text-[13px] text-slate-400 hover:bg-slate-800/60 text-left border-t border-slate-800"
              >
                <ArrowRightOnRectangleIcon className="w-4 h-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.header>
  );
}
