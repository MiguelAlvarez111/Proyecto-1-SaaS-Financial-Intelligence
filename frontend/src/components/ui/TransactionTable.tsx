"use client";

import { useMemo, useState, useEffect } from "react";
import { motion } from "framer-motion";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import { Transaction } from "@/types";

/** Normalize for numeric comparison: strip commas, $, spaces so "26,754" and "26754" match */
function normNum(s: string): string {
  return s.replace(/[,$\s]/g, "");
}

function filterBySearch(transactions: Transaction[], q: string): Transaction[] {
  const term = q.trim().toLowerCase();
  if (!term) return transactions;
  const termNum = normNum(term);
  return transactions.filter((tx) => {
    const dateTime = formatDateTime(tx.timestamp).toLowerCase();
    const currency = tx.currency.toLowerCase();
    const status = tx.status.toLowerCase();
    const device = tx.client_device.toLowerCase();
    const amountRaw = tx.amount.toString();
    const amountUsdRaw = tx.amount_usd.toString();
    const amountFormatted = formatCurrency(tx.amount).toLowerCase();
    const amountUsdFormatted = formatCurrency(tx.amount_usd).toLowerCase();
    const amountNorm = normNum(amountRaw);
    const amountUsdNorm = normNum(amountUsdRaw);
    const amountFormattedNorm = normNum(amountFormatted);
    const amountUsdFormattedNorm = normNum(amountUsdFormatted);
    const textMatch =
      dateTime.includes(term) ||
      currency.includes(term) ||
      status.includes(term) ||
      device.includes(term);
    const rawAmountMatch = amountRaw.includes(term) || amountUsdRaw.includes(term);
    const formattedAmountMatch =
      amountFormatted.includes(term) || amountUsdFormatted.includes(term);
    const normalizedAmountMatch =
      termNum.length > 0 &&
      (amountNorm.includes(termNum) ||
        amountUsdNorm.includes(termNum) ||
        amountFormattedNorm.includes(termNum) ||
        amountUsdFormattedNorm.includes(termNum));
    return textMatch || rawAmountMatch || formattedAmountMatch || normalizedAmountMatch;
  });
}

interface TransactionTableProps {
  transactions: Transaction[];
  searchQuery?: string;
  delay?: number;
  reduceMotion?: boolean;
  loading?: boolean;
  error?: string | null;
  hasMore?: boolean;
  loadingMore?: boolean;
  onLoadMore?: () => void;
  onRetry?: () => void;
  showSearchingHint?: boolean;
}

// Semantic status colors: green=success, red=failed, amber=pending, blue=refunded
const statusStyles = {
  COMPLETED: {
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/20",
  },
  FAILED: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/20",
  },
  PENDING: {
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/20",
  },
  REFUNDED: {
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/20",
  },
};

export function TransactionTable({
  transactions,
  searchQuery = "",
  delay = 0,
  reduceMotion = false,
  loading = false,
  error = null,
  hasMore = false,
  loadingMore = false,
  onLoadMore,
  onRetry,
  showSearchingHint = false,
}: TransactionTableProps) {
  const [hintFadeIn, setHintFadeIn] = useState(false);
  const [showExpandedHint, setShowExpandedHint] = useState(false);
  const [expandedHintFadeIn, setExpandedHintFadeIn] = useState(false);
  const filtered = useMemo(
    () => filterBySearch(transactions, searchQuery),
    [transactions, searchQuery]
  );

  useEffect(() => {
    if (showSearchingHint) {
      setHintFadeIn(false);
      const id = requestAnimationFrame(() => setHintFadeIn(true));
      return () => cancelAnimationFrame(id);
    } else {
      setHintFadeIn(false);
    }
  }, [showSearchingHint]);

  useEffect(() => {
    if (showExpandedHint) {
      setExpandedHintFadeIn(false);
      const id = requestAnimationFrame(() => setExpandedHintFadeIn(true));
      const t = setTimeout(() => setShowExpandedHint(false), 800);
      return () => {
        cancelAnimationFrame(id);
        clearTimeout(t);
      };
    } else {
      setExpandedHintFadeIn(false);
    }
  }, [showExpandedHint]);

  const hasSearchQuery = searchQuery.trim().length > 0;

  const handleLoadMore = () => {
    if (hasSearchQuery) setShowExpandedHint(true);
    onLoadMore?.();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.6, delay }}
      className="glass-card overflow-hidden"
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-medium text-slate-300">Transaction Ledger</h3>
          {showSearchingHint && (
            <p
              className={`text-[12px] text-slate-500 font-normal mb-2 transition-opacity duration-200 ${hintFadeIn ? "opacity-100" : "opacity-0"}`}
            >
              Searching in transaction ledger
            </p>
          )}
          {showExpandedHint && hasSearchQuery && (
            <p
              className={`text-[12px] text-slate-500 font-normal mb-2 transition-opacity duration-200 ${expandedHintFadeIn ? "opacity-100" : "opacity-0"}`}
            >
              Search expanded with more transactions
            </p>
          )}
          <p className="text-[12px] text-slate-500 mt-1">
            Recent transactions with USD normalization
          </p>
        </div>
        <div className="live-indicator">
          <span className="live-dot"></span>
          <span>Live</span>
        </div>
      </div>

      {hasSearchQuery && hasMore && !loading && transactions.length > 0 && (
        <p className="text-[12px] text-slate-400 font-medium mb-2">
          Showing results from loaded transactions. Load more to widen the search.
        </p>
      )}

      {loading && transactions.length === 0 && (
        <div className="py-16 text-center">
          <p className="text-[13px] text-slate-500">Loading transactions…</p>
          <div className="mt-3 h-1 w-24 mx-auto rounded-full bg-slate-800 overflow-hidden">
            <div className="h-full w-1/2 rounded-full bg-slate-600 animate-pulse" />
          </div>
        </div>
      )}

      {error && transactions.length === 0 && (
        <div className="py-12 px-4 text-center">
          <p className="text-[13px] text-slate-400 mb-3">{error}</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              disabled={loading}
              className="px-4 py-2 rounded-lg text-[13px] font-medium bg-slate-800/60 border border-white/5 text-slate-300 hover:bg-slate-700/60 hover:border-white/10 hover:text-slate-200 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {!loading && !(error && transactions.length === 0) && (
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date / Time</th>
                <th>Amount</th>
                <th>Currency</th>
                <th>Amount USD</th>
                <th>Status</th>
                <th>Device</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((tx, index) => (
              <motion.tr
                key={tx.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  duration: reduceMotion ? 0 : 0.3,
                  delay: reduceMotion ? 0 : delay + index * 0.03,
                }}
              >
                <td className="text-slate-400 text-[13px]">
                  {formatDateTime(tx.timestamp)}
                </td>
                <td className="numeric text-slate-300">
                  {tx.amount.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td>
                  <span className="px-2 py-0.5 rounded bg-slate-800/60 text-slate-400 text-[11px] font-medium">
                    {tx.currency}
                  </span>
                </td>
                <td className="numeric font-medium text-white">
                  {formatCurrency(tx.amount_usd)}
                </td>
                <td>
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded text-[11px] font-medium border",
                      statusStyles[tx.status].bg,
                      statusStyles[tx.status].text,
                      statusStyles[tx.status].border
                    )}
                  >
                    {tx.status}
                  </span>
                </td>
                <td className="text-slate-500 text-[13px] capitalize">{tx.client_device}</td>
              </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !(error && transactions.length === 0) && filtered.length === 0 && (
        <div className="text-center py-12">
          <p className="text-slate-400">No transactions found</p>
        </div>
      )}

      {!loading && !(error && transactions.length === 0) && transactions.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-800/50 flex flex-col items-center gap-2">
          {hasMore && (
            <button
              type="button"
              onClick={handleLoadMore}
              disabled={loadingMore}
              className="px-4 py-2 rounded-lg text-[13px] font-medium bg-slate-800/60 border border-white/5 text-slate-300 hover:bg-slate-700/60 hover:border-white/10 hover:text-slate-200 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loadingMore ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-slate-500 border-t-transparent rounded-full animate-spin" />
                  Loading…
                </>
              ) : (
                "Load 50 more"
              )}
            </button>
          )}
          {!hasMore && transactions.length > 0 && (
            <p className="text-[12px] text-slate-500">End of results</p>
          )}
        </div>
      )}
    </motion.div>
  );
}
