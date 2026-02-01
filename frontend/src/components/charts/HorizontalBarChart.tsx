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
  reduceMotion?: boolean;
}

const CustomTooltip = ({ active, payload, formatAsCurrency }: any) => {
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
        <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>
          {payload[0].payload.name}
        </p>
        <p
          className="numeric"
          style={{ fontSize: 16, fontWeight: 600, color: "#e2e8f0" }}
        >
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
  reduceMotion = false,
}: HorizontalBarChartProps) {
  // Colores indigo con variación de saturación
  const defaultColors = ["#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3"];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.6, delay: reduceMotion ? 0 : delay }}
      className="glass-card h-[380px]"
    >
      <h3 className="text-sm font-medium text-slate-300 mb-6">{title}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 50, left: 20, bottom: 5 }}
          barCategoryGap="20%"
        >
          <CartesianGrid
            strokeDasharray="4 4"
            stroke="rgba(255,255,255,0.03)"
            horizontal={false}
            vertical={true}
          />
          <XAxis
            type="number"
            stroke="transparent"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#94a3b8" }}
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
            stroke="transparent"
            fontSize={13}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#e2e8f0" }}
            width={80}
          />
          <Tooltip
            content={<CustomTooltip formatAsCurrency={formatAsCurrency} />}
            cursor={{ fill: "rgba(255, 255, 255, 0.02)" }}
          />
          {/* Background track for context */}
          <Bar
            dataKey={() => Math.max(...data.map(d => d.value)) * 1.1}
            fill="rgba(255, 255, 255, 0.03)"
            radius={[6, 6, 6, 6]}
            isAnimationActive={false}
          />
          <Bar
            dataKey="value"
            radius={[6, 6, 6, 6]}
            animationDuration={1200}
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
