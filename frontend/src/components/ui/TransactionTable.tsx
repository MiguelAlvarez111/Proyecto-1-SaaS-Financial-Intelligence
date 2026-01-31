"use client";

import { motion } from "framer-motion";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import { Transaction } from "@/types";

interface TransactionTableProps {
  transactions: Transaction[];
  delay?: number;
}

const statusStyles = {
  COMPLETED: {
    bg: "bg-emerald-500/20",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
  },
  FAILED: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    border: "border-red-500/30",
  },
  PENDING: {
    bg: "bg-orange-500/20",
    text: "text-orange-400",
    border: "border-orange-500/30",
  },
  REFUNDED: {
    bg: "bg-blue-500/20",
    text: "text-blue-400",
    border: "border-blue-500/30",
  },
};

export function TransactionTable({
  transactions,
  delay = 0,
}: TransactionTableProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className="glass-card overflow-hidden"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Transaction Ledger</h3>
          <p className="text-sm text-slate-400 mt-1">
            Recent transactions with USD normalization
          </p>
        </div>
        <div className="live-indicator">
          <span className="live-dot"></span>
          <span>Live</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Date/Time</th>
              <th>Amount</th>
              <th>Currency</th>
              <th>Amount USD</th>
              <th>Status</th>
              <th>Device</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, index) => (
              <motion.tr
                key={tx.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  duration: 0.3,
                  delay: delay + index * 0.03,
                }}
              >
                <td className="text-slate-300">
                  {formatDateTime(tx.timestamp)}
                </td>
                <td className="font-mono text-slate-300">
                  {tx.amount.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td>
                  <span className="px-2 py-1 rounded-md bg-slate-800 text-slate-300 text-xs font-medium">
                    {tx.currency}
                  </span>
                </td>
                <td className="font-mono font-semibold text-white">
                  {formatCurrency(tx.amount_usd)}
                </td>
                <td>
                  <span
                    className={cn(
                      "px-2.5 py-1 rounded-full text-xs font-semibold border",
                      statusStyles[tx.status].bg,
                      statusStyles[tx.status].text,
                      statusStyles[tx.status].border
                    )}
                  >
                    {tx.status}
                  </span>
                </td>
                <td className="text-slate-400 capitalize">{tx.client_device}</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {transactions.length === 0 && (
        <div className="text-center py-12">
          <p className="text-slate-400">No transactions found</p>
        </div>
      )}
    </motion.div>
  );
}
