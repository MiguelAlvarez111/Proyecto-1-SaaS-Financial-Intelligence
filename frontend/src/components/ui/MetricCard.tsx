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
  reduceMotion?: boolean;
}

export function MetricCard({
  title,
  value,
  delta,
  deltaLabel = "vs last month",
  icon,
  delay = 0,
  gradient,
  reduceMotion = false,
}: MetricCardProps) {
  const isPositive = delta !== undefined && delta >= 0;
  const hasChange = delta !== undefined && delta !== 0;
  const duration = reduceMotion ? 0 : 0.5;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration,
        delay: reduceMotion ? 0 : delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
      whileHover={reduceMotion ? undefined : { y: -2, transition: { duration: 0.15 } }}
      className="metric-card group"
    >
      {/* Content */}
      <div className="relative z-10">
        {/* Header: label discreto uppercase tracking-wider */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
            {title}
          </span>
          {icon && (
            <div className="p-2 rounded-lg bg-indigo-500/8 text-indigo-400 group-hover:bg-indigo-500/12 transition-colors">
              {icon}
            </div>
          )}
        </div>

        {/* Value: protagonista con text-[32px] y tabular-nums */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: reduceMotion ? 0 : delay + 0.2, duration: reduceMotion ? 0 : 0.4 }}
          className="mb-3"
        >
          <span className="text-[32px] font-semibold text-white tracking-tight numeric leading-none">
            {value}
          </span>
        </motion.div>

        {/* Delta indicator: strict semantic colors */}
        {hasChange && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: reduceMotion ? 0 : delay + 0.3, duration: reduceMotion ? 0 : 0.3 }}
            className="flex items-center gap-2 mt-3"
          >
            <div
              className={cn(
                "flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium numeric min-w-[4.5rem] justify-center",
                isPositive
                  ? "bg-emerald-500/12 text-emerald-400"
                  : "bg-red-500/12 text-red-400"
              )}
            >
              {isPositive ? (
                <ArrowUpIcon className="w-3 h-3" />
              ) : (
                <ArrowDownIcon className="w-3 h-3" />
              )}
              <span>{Math.abs(delta).toFixed(1)}%</span>
            </div>
            <span className="text-[11px] text-slate-400">{deltaLabel}</span>
          </motion.div>
        )}

        {!hasChange && delta !== undefined && (
          <div className="flex items-center gap-2 mt-3">
            <span className="text-[11px] text-slate-500">No change</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
