"use client";

import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { formatNumber } from "@/lib/utils";

interface DataPoint {
  name: string;
  value: number;
  color: string;
}

interface DonutChartProps {
  data: DataPoint[];
  title: string;
  centerValue?: string;
  centerLabel?: string;
  delay?: number;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="glass-card !p-3 !rounded-xl border border-primary-500/30">
        <p className="text-sm font-semibold text-white">{data.name}</p>
        <p className="text-lg font-bold" style={{ color: data.color }}>
          {formatNumber(data.value)}
        </p>
      </div>
    );
  }
  return null;
};

export function DonutChart({
  data,
  title,
  centerValue,
  centerLabel,
  delay = 0,
}: DonutChartProps) {
  const total = data.reduce((acc, item) => acc + item.value, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className="glass-card h-[380px]"
    >
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>

      <div className="relative">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={100}
              paddingAngle={4}
              dataKey="value"
              animationBegin={delay * 1000}
              animationDuration={1500}
              animationEasing="ease-out"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke="transparent"
                  className="transition-all duration-300 hover:opacity-80"
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center text */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center -mt-4">
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.5, type: "spring" }}
              className="text-2xl font-bold text-white"
            >
              {centerValue || formatNumber(total)}
            </motion.p>
            <p className="text-xs text-slate-400 uppercase tracking-wider">
              {centerLabel || "Total"}
            </p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 mt-2">
        {data.map((item, index) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: delay + 0.3 + index * 0.1 }}
            className="flex items-center gap-2"
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-slate-400">{item.name}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
