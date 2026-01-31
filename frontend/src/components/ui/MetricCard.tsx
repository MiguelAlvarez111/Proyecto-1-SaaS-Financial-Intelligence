"use client";

import { motion } from "framer-motion";
import { ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/solid";
import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  icon?: ReactNode;
  delay?: number;
  gradient?: string;
}

export function MetricCard({
  title,
  value,
  delta,
  deltaLabel = "vs last month",
  icon,
  delay = 0,
  gradient,
}: MetricCardProps) {
  const isPositive = delta !== undefined && delta >= 0;
  const hasChange = delta !== undefined && delta !== 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.5,
        delay: delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
      whileHover={{
        y: -4,
        transition: { duration: 0.2 },
      }}
      className="metric-card group"
    >
      {/* Gradient accent line */}
      <div
        className={cn(
          "absolute top-0 left-0 right-0 h-1 rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300",
          gradient || "bg-gradient-to-r from-primary-500 via-purple-500 to-pink-500"
        )}
      />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {title}
          </span>
          {icon && (
            <div className="p-2 rounded-xl bg-primary-500/10 text-primary-400 group-hover:bg-primary-500/20 transition-colors">
              {icon}
            </div>
          )}
        </div>

        {/* Value with animated counter effect */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: delay + 0.2, duration: 0.4 }}
          className="mb-3"
        >
          <span className="text-3xl font-bold text-white tracking-tight">
            {value}
          </span>
        </motion.div>

        {/* Delta indicator */}
        {hasChange && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: delay + 0.3, duration: 0.3 }}
            className="flex items-center gap-2"
          >
            <div
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold",
                isPositive
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-red-500/20 text-red-400"
              )}
            >
              {isPositive ? (
                <ArrowUpIcon className="w-3 h-3" />
              ) : (
                <ArrowDownIcon className="w-3 h-3" />
              )}
              <span>{Math.abs(delta).toFixed(1)}%</span>
            </div>
            <span className="text-xs text-slate-500">{deltaLabel}</span>
          </motion.div>
        )}

        {!hasChange && delta !== undefined && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">No change</span>
          </div>
        )}
      </div>

      {/* Decorative glow effect on hover */}
      <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1/2 h-12 bg-primary-500/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    </motion.div>
  );
}
