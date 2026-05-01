"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const data = [
  { day: "Mon", executions: 32 },
  { day: "Tue", executions: 48 },
  { day: "Wed", executions: 41 },
  { day: "Thu", executions: 63 },
  { day: "Fri", executions: 74 },
  { day: "Sat", executions: 52 },
  { day: "Sun", executions: 68 },
];

export function ExecutionChart() {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ left: -24, right: 8, top: 10, bottom: 0 }}>
        <defs>
          <linearGradient id="executions" x1="0" x2="0" y1="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.5} />
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="hsl(var(--border))" vertical={false} />
        <XAxis dataKey="day" tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: 8,
          }}
        />
        <Area
          type="monotone"
          dataKey="executions"
          stroke="hsl(var(--primary))"
          fill="url(#executions)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
