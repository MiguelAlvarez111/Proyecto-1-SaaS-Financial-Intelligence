"use client";

import { FunnelIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { ChevronDownIcon } from "@heroicons/react/24/solid";
import { useState } from "react";
import { cn } from "@/lib/utils";
import type { FilterState } from "@/types";

const CURRENCIES = ["USD", "EUR", "GBP", "COP"];
const STATUSES = ["COMPLETED", "FAILED", "PENDING", "REFUNDED"] as const;

interface FilterBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  className?: string;
}

function getDefaultDateRange() {
  const end = new Date();
  const start = new Date();
  start.setMonth(start.getMonth() - 1);
  return { start, end };
}

export function FilterBar({ filters, onChange, className }: FilterBarProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const toggleCurrency = (currency: string) => {
    const next = filters.currencies.includes(currency)
      ? filters.currencies.filter((c) => c !== currency)
      : [...filters.currencies, currency];
    onChange({ ...filters, currencies: next });
  };

  const toggleStatus = (status: string) => {
    const next = filters.statuses.includes(status)
      ? filters.statuses.filter((s) => s !== status)
      : [...filters.statuses, status];
    onChange({ ...filters, statuses: next });
  };

  const setDateStart = (value: string) => {
    const start = value ? new Date(value) : getDefaultDateRange().start;
    onChange({
      ...filters,
      dateRange: { ...filters.dateRange, start },
    });
  };

  const setDateEnd = (value: string) => {
    const end = value ? new Date(value) : getDefaultDateRange().end;
    onChange({
      ...filters,
      dateRange: { ...filters.dateRange, end },
    });
  };

  const clearFilters = () => {
    const { start, end } = getDefaultDateRange();
    onChange({
      currencies: [],
      statuses: [],
      dateRange: { start, end },
      quickFilter: "",
    });
  };

  const defaultRange = getDefaultDateRange();
  const hasActiveFilters =
    filters.currencies.length > 0 ||
    filters.statuses.length > 0 ||
    filters.dateRange.start?.toISOString().slice(0, 10) !== defaultRange.start.toISOString().slice(0, 10) ||
    filters.dateRange.end?.toISOString().slice(0, 10) !== defaultRange.end.toISOString().slice(0, 10);

  const activeCount = filters.currencies.length + filters.statuses.length + (hasActiveFilters ? 1 : 0);
  const startStr = filters.dateRange.start?.toISOString().slice(0, 10) ?? "";
  const endStr = filters.dateRange.end?.toISOString().slice(0, 10) ?? "";

  return (
    <div
      className={cn(
        "rounded-xl border border-slate-800/60 bg-slate-900/40 overflow-hidden",
        className
      )}
    >
      {/* Header: always visible, acts as toolbar */}
      <button
        type="button"
        onClick={() => setIsExpanded((e) => !e)}
        className="w-full flex items-center justify-between gap-4 px-4 py-2.5 text-left hover:bg-slate-800/20 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FunnelIcon className="w-4 h-4 text-slate-500" />
          <span className="text-[13px] font-medium text-slate-400">Filters</span>
          {activeCount > 0 && (
            <span className="flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 rounded bg-indigo-500/15 text-indigo-400 text-[11px] font-semibold">
              {activeCount}
            </span>
          )}
        </div>
        <ChevronDownIcon
          className={cn("w-4 h-4 text-slate-500 transition-transform", isExpanded && "rotate-180")}
        />
      </button>

      {/* Content: grouped with clear hierarchy */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-3 border-t border-slate-800/30">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 lg:gap-6">
            {/* Currency: indigo accent - active state clear */}
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 mb-2">
                Currency
              </p>
              <div className="flex flex-wrap gap-2">
                {CURRENCIES.map((c) => {
                  const active = filters.currencies.includes(c);
                  return (
                    <button
                      key={c}
                      type="button"
                      onClick={() => toggleCurrency(c)}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-[12px] font-medium transition-all duration-150 border",
                        active
                          ? "bg-indigo-500/20 text-indigo-200 border-indigo-400/40 shadow-sm shadow-indigo-500/10"
                          : "bg-slate-900/30 text-slate-400 border-white/5 hover:bg-slate-800/50 hover:text-slate-300 hover:border-white/10"
                      )}
                    >
                      {c}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Status: semantic colors - active state clear */}
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 mb-2">
                Status
              </p>
              <div className="flex flex-wrap gap-2">
                {STATUSES.map((s) => {
                  const active = filters.statuses.includes(s);
                  // Semantic colors: COMPLETED=green, FAILED=red, PENDING=amber, REFUNDED=blue
                  const semanticColors: Record<string, { active: string; inactive: string }> = {
                    COMPLETED: {
                      active: "bg-emerald-500/20 text-emerald-300 border-emerald-400/40 shadow-sm shadow-emerald-500/10",
                      inactive: "hover:bg-emerald-500/10 hover:text-emerald-400 hover:border-emerald-500/25",
                    },
                    FAILED: {
                      active: "bg-red-500/20 text-red-300 border-red-400/40 shadow-sm shadow-red-500/10",
                      inactive: "hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/25",
                    },
                    PENDING: {
                      active: "bg-amber-500/20 text-amber-300 border-amber-400/40 shadow-sm shadow-amber-500/10",
                      inactive: "hover:bg-amber-500/10 hover:text-amber-400 hover:border-amber-500/25",
                    },
                    REFUNDED: {
                      active: "bg-blue-500/20 text-blue-300 border-blue-400/40 shadow-sm shadow-blue-500/10",
                      inactive: "hover:bg-blue-500/10 hover:text-blue-400 hover:border-blue-500/25",
                    },
                  };
                  const colors = semanticColors[s];
                  return (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleStatus(s)}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-[12px] font-medium transition-all duration-150 border",
                        active
                          ? colors.active
                          : `bg-slate-900/30 text-slate-400 border-white/5 ${colors.inactive}`
                      )}
                    >
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Date range */}
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600 mb-2">
                Date range
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="date"
                  value={startStr}
                  onChange={(e) => setDateStart(e.target.value)}
                  className="input-glass text-[13px] flex-1 min-w-[130px] py-2"
                  aria-label="From"
                />
                <span className="text-slate-600 text-[13px]">–</span>
                <input
                  type="date"
                  value={endStr}
                  onChange={(e) => setDateEnd(e.target.value)}
                  className="input-glass text-[13px] flex-1 min-w-[130px] py-2"
                  aria-label="To"
                />
              </div>
            </div>
          </div>

          {hasActiveFilters && (
            <div className="mt-4 pt-3 border-t border-slate-800/30 flex justify-end">
              <button
                type="button"
                onClick={clearFilters}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium text-slate-500 hover:text-slate-300 hover:bg-slate-800/40 transition-colors"
              >
                <XMarkIcon className="w-3.5 h-3.5" />
                Clear filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
