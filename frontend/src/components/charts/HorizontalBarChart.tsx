"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface DataPoint {
  name: string;
  value: number;
  color?: string;
}

interface HorizontalBarChartProps {
  data: DataPoint[];
  title: string;
  delay?: number;
  formatAsCurrency?: boolean;
}

const CustomTooltip = ({ active, payload, formatAsCurrency }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card !p-3 !rounded-xl border border-primary-500/30">
        <p className="text-sm font-semibold text-white">{payload[0].payload.name}</p>
        <p className="text-lg font-bold text-primary-400">
          {formatAsCurrency ? formatCurrency(payload[0].value) : payload[0].value.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

export function HorizontalBarChart({
  data,
  title,
  delay = 0,
  formatAsCurrency = true,
}: HorizontalBarChartProps) {
  const defaultColors = ["#6366f1", "#a855f7", "#ec4899", "#10b981", "#f97316"];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className="glass-card h-[380px]"
    >
      <h3 className="text-lg font-semibold text-white mb-6">{title}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 50, left: 20, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.05)"
            horizontal={true}
            vertical={false}
          />
          <XAxis
            type="number"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#64748b" }}
            tickFormatter={(value) =>
              formatAsCurrency
                ? value >= 1000000
                  ? `$${(value / 1000000).toFixed(0)}M`
                  : `$${(value / 1000).toFixed(0)}K`
                : value.toLocaleString()
            }
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#f8fafc" }}
            width={80}
          />
          <Tooltip
            content={<CustomTooltip formatAsCurrency={formatAsCurrency} />}
          />
          <Bar
            dataKey="value"
            radius={[0, 8, 8, 0]}
            animationDuration={1500}
            animationEasing="ease-out"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || defaultColors[index % defaultColors.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
