"use client";

import { useState, useEffect, useCallback } from "react";
import { DashboardData, FilterState } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface UseDashboardOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseDashboardReturn {
  data: DashboardData | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  lastUpdated: Date | null;
}

export function useDashboard(
  filters?: Partial<FilterState>,
  options: UseDashboardOptions = {}
): UseDashboardReturn {
  const { autoRefresh = false, refreshInterval = 60000 } = options;
  
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams();
      
      if (filters?.currencies?.length) {
        params.set("currencies", filters.currencies.join(","));
      }
      if (filters?.statuses?.length) {
        params.set("statuses", filters.statuses.join(","));
      }
      if (filters?.dateRange?.start) {
        params.set("start_date", filters.dateRange.start.toISOString().split("T")[0]);
      }
      if (filters?.dateRange?.end) {
        params.set("end_date", filters.dateRange.end.toISOString().split("T")[0]);
      }

      const url = `${API_BASE_URL}/api/dashboard${params.toString() ? `?${params}` : ""}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const dashboardData: DashboardData = await response.json();
      setData(dashboardData);
      setLastUpdated(new Date());
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      console.error("Dashboard fetch error:", message);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchData,
    lastUpdated,
  };
}

export async function fetchFilters() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/filters`);
    if (!response.ok) throw new Error("Failed to fetch filters");
    return await response.json();
  } catch (err) {
    console.error("Filters fetch error:", err);
    return null;
  }
}

export async function exportTransactions(filters?: Partial<FilterState>): Promise<Blob | null> {
  try {
    const params = new URLSearchParams();
    params.set("limit", "10000");
    
    if (filters?.currencies?.length) {
      params.set("currencies", filters.currencies.join(","));
    }
    if (filters?.statuses?.length) {
      params.set("statuses", filters.statuses.join(","));
    }

    const response = await fetch(`${API_BASE_URL}/api/transactions?${params}`);
    if (!response.ok) throw new Error("Failed to export");
    
    const data = await response.json();
    
    // Convert to CSV
    const headers = ["ID", "Timestamp", "Amount", "Currency", "Amount USD", "Status", "Device"];
    const rows = data.map((tx: any) => [
      tx.id,
      tx.timestamp,
      tx.amount,
      tx.currency,
      tx.amount_usd,
      tx.status,
      tx.client_device,
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(",")).join("\n");
    return new Blob([csv], { type: "text/csv" });
  } catch (err) {
    console.error("Export error:", err);
    return null;
  }
}
