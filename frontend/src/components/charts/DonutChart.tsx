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
  reduceMotion?: boolean;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div
        style={{
          background: "#0f172a",
          border: "1px solid #334155",
          borderRadius: 8,
          padding: "10px 14px",
          minWidth: 100,
        }}
      >
        <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4, whiteSpace: "nowrap" }}>
          {data.name}
        </p>
        <p
          className="numeric"
          style={{ fontSize: 16, fontWeight: 600, color: data.color }}
        >
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
  reduceMotion = false,
}: DonutChartProps) {
  const total = data.reduce((acc, item) => acc + item.value, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.6, delay: reduceMotion ? 0 : delay }}
      className="glass-card h-[380px]"
    >
      <h3 className="text-sm font-medium text-slate-300 mb-4">{title}</h3>

      <div className="relative">
        {/* Centro detrás del gráfico: se ve por el hueco del donut */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
          <div className="text-center -mt-4 px-4 py-2 min-w-[4rem]">
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: reduceMotion ? 0 : delay + 0.5, type: "spring", duration: reduceMotion ? 0 : undefined }}
              className="text-xl font-semibold text-white numeric"
            >
              {centerValue || formatNumber(total)}
            </motion.p>
            <p className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">
              {centerLabel || "Total"}
            </p>
          </div>
        </div>

        {/* Gráfico y tooltip encima: el tooltip queda visible sobre todo */}
        <div className="relative z-10">
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
              <Tooltip
                content={<CustomTooltip />}
                cursor={false}
                allowEscapeViewBox={{ x: true, y: true }}
                offset={40}
                wrapperStyle={{ outline: "none", zIndex: 30 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 mt-2">
        {data.map((item, index) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: reduceMotion ? 0 : delay + 0.3 + index * 0.1, duration: reduceMotion ? 0 : undefined }}
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
