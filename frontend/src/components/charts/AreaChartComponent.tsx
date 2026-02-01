"use client";

import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface DataPoint {
  date: string;
  volume: number;
}

interface AreaChartComponentProps {
  data: DataPoint[];
  title: string;
  delay?: number;
  reduceMotion?: boolean;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "#0f172a",
          border: "1px solid #334155",
          borderRadius: 8,
          padding: "10px 14px",
        }}
      >
        <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>{label}</p>
        <p
          className="numeric"
          style={{ fontSize: 16, fontWeight: 600, color: "#e2e8f0" }}
        >
          {formatCurrency(payload[0].value)}
        </p>
      </div>
    );
  }
  return null;
};

export function AreaChartComponent({
  data,
  title,
  delay = 0,
  reduceMotion = false,
}: AreaChartComponentProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.6, delay: reduceMotion ? 0 : delay }}
      className="glass-card h-[380px]"
    >
      <h3 className="text-sm font-medium text-slate-300 mb-6">{title}</h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#818cf8" stopOpacity={0.2} />
              <stop offset="50%" stopColor="#6366f1" stopOpacity={0.08} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="4 4"
            stroke="rgba(255,255,255,0.04)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            stroke="transparent"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#94a3b8" }}
            dy={8}
          />
          <YAxis
            stroke="transparent"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#94a3b8" }}
            tickFormatter={(value) =>
              value >= 1000000
                ? `$${(value / 1000000).toFixed(0)}M`
                : `$${(value / 1000).toFixed(0)}K`
            }
            dx={-4}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "rgba(129, 140, 248, 0.2)", strokeWidth: 1 }} />
          <Area
            type="monotone"
            dataKey="volume"
            stroke="rgba(129, 140, 248, 0.88)"
            strokeWidth={1.5}
            fill="url(#colorVolume)"
            animationDuration={1200}
            animationEasing="ease-out"
            activeDot={{ r: 5, fill: "#818cf8", stroke: "#0f172a", strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
