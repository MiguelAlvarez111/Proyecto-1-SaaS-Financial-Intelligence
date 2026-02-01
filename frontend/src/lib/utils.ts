import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combina clases de Tailwind de forma segura (clsx + tailwind-merge).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formatea un número como moneda USD (ej: $1.2M, $500.00).
 */
export function formatCurrency(value: number): string {
  if (value == null || Number.isNaN(value)) return "$0";
  if (Math.abs(value) >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(2)}B`;
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (Math.abs(value) >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Formatea un número con separadores de miles.
 */
export function formatNumber(value: number): string {
  if (value == null || Number.isNaN(value)) return "0";
  return Math.round(value).toLocaleString("en-US");
}

/**
 * Formatea un timestamp ISO a fecha/hora legible (ej: Jan 15, 2025 14:30).
 */
export function formatDateTime(isoString: string): string {
  if (!isoString) return "—";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Convierte una fecha a "hace X minutos/horas/días".
 */
export function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  return `${diffDay}d ago`;
}

/**
 * Colores para gráficos (alineados con el tema del dashboard).
 */
export const chartColors = {
  primary: "#6366f1",
  success: "#10b981",
  warning: "#f97316",
  danger: "#ef4444",
  info: "#3b82f6",
  gray: "#64748b",
};
