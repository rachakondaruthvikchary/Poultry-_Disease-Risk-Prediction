"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type TrendPoint = {
  day: string;
  risk_score: number | null;
  has_data?: boolean;
};

/** Parse "YYYY-MM-DD" without UTC timezone shift */
function parseLocalDate(day: string) {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function formatDay(day: string) {
  return parseLocalDate(day).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function toRiskLabel(score: number) {
  if (score >= 0.85) return "Critical";
  if (score >= 0.65) return "High";
  if (score >= 0.35) return "Medium";
  return "Low";
}

function riskColor(score: number) {
  if (score >= 0.85) return "#660000";
  if (score >= 0.65) return "#ef4444";
  if (score >= 0.35) return "#f59e0b";
  return "#22c55e";
}

/* Custom dot — only shown on days with real data, colored by risk */
const CustomDot = (props: any) => {
  const { cx, cy, payload } = props;
  if (!payload?.has_data || payload.risk_score == null) return null;
  const color = riskColor(payload.risk_score);
  return <circle cx={cx} cy={cy} r={5} fill={color} stroke="#fff" strokeWidth={2} />;
};

/* Custom tooltip */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  const score = payload[0].value as number | null;
  if (score == null) {
    return (
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 shadow-lg text-xs">
        <p className="font-semibold text-slate-600 dark:text-slate-300 mb-1">{formatDay(label)}</p>
        <p className="text-slate-400">No data recorded</p>
      </div>
    );
  }
  const level = toRiskLabel(score);
  const color = riskColor(score);
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 shadow-lg text-xs">
      <p className="font-semibold text-slate-600 dark:text-slate-300 mb-1">{formatDay(label)}</p>
      <p style={{ color }} className="font-bold text-sm">
        {(score * 100).toFixed(1)}% — <span>{level} Risk</span>
      </p>
    </div>
  );
};

export function RiskTrendChart({ data }: { data: TrendPoint[] }) {
  const hasAnyData = data.some((p) => p.has_data);

  // Color based on worst recorded score in the window
  const scores = data.filter((p) => p.risk_score != null).map((p) => p.risk_score as number);
  const maxScore = scores.length ? Math.max(...scores) : 0;
  const gradientColor = riskColor(maxScore);

  return (
    <div className="glass rounded-3xl p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div>
          <h3 className="text-sm font-bold text-red-900 dark:text-red-50">📊 14-Day Risk Trend</h3>
          <p className="text-xs text-red-600 dark:text-red-400 mt-0.5">Line connects recorded data points across missing days</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-red-700 dark:text-red-300">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 inline-block" /> Low
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500 inline-block" /> Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#660000] inline-block" /> Critical
          </span>
        </div>
      </div>

      {!hasAnyData && (
        <p className="text-xs text-red-600 dark:text-red-400 mt-1 mb-2">
          No data yet — submit a Daily Health Check or upload an image to see the trend.
        </p>
      )}

      <ResponsiveContainer width="100%" height={265}>
        <AreaChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="10%" stopColor={gradientColor} stopOpacity={0.4} />
              <stop offset="95%" stopColor={gradientColor} stopOpacity={0.02} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#ef5350" strokeOpacity={0.4} vertical={false} />

          <XAxis
            dataKey="day"
            tick={{ fontSize: 10, fill: "#b91c1c" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={formatDay}
            interval={1}
          />
          <YAxis
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#b91c1c" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${Math.round(v * 100)}%`}
            width={38}
          />

          {/* Risk zone reference lines */}
          <ReferenceLine
            y={0.85}
            stroke="#660000"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{ value: "Critical", position: "insideTopRight", fontSize: 10, fill: "#660000" }}
          />
          <ReferenceLine
            y={0.65}
            stroke="#ef4444"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{ value: "High", position: "insideTopRight", fontSize: 10, fill: "#ef4444" }}
          />
          <ReferenceLine
            y={0.35}
            stroke="#f59e0b"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{ value: "Med", position: "insideTopRight", fontSize: 10, fill: "#f59e0b" }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="risk_score"
            stroke={gradientColor}
            strokeWidth={2.5}
            fill="url(#riskGrad)"
            dot={<CustomDot />}
            activeDot={{ r: 6, stroke: "#fff", strokeWidth: 2, fill: gradientColor }}
            connectNulls={true}
            isAnimationActive={true}
            animationDuration={500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

