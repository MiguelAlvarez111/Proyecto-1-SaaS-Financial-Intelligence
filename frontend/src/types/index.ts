export interface Transaction {
  id: string;
  timestamp: string;
  amount: number;
  currency: string;
  status: "COMPLETED" | "FAILED" | "PENDING" | "REFUNDED";
  amount_usd: number;
  client_email: string;
  client_device: string;
  client_ip?: string;
}

export interface KPIData {
  totalVolume: number;
  totalTransactions: number;
  avgTicket: number;
  successRate: number;
  volumeDelta: number;
  transactionsDelta: number;
  avgTicketDelta: number;
}

export interface DailyVolume {
  date: string;
  volume: number;
  count: number;
}

export interface StatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface CurrencyVolume {
  currency: string;
  amount: number;
  count: number;
}

export interface DeviceVolume {
  device: string;
  amount: number;
  percentage: number;
}

export interface DashboardData {
  kpis: KPIData;
  dailyVolume: DailyVolume[];
  statusDistribution: StatusDistribution[];
  currencyVolume: CurrencyVolume[];
  deviceVolume: DeviceVolume[];
  recentTransactions: Transaction[];
  lastUpdated: string;
}

export interface FilterState {
  currencies: string[];
  statuses: string[];
  dateRange: {
    start: Date;
    end: Date;
  };
  quickFilter: string;
}
