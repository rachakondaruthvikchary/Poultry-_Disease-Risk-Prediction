"use client";

import { AlertTriangle, ShieldCheck, Activity, Microscope } from "lucide-react";
import { useLanguage } from "@/lib/language-context";

export function OverviewCards({ overview }: { overview: any }) {
  const { t } = useLanguage();

  // Translate risk level value
  const rawRisk = overview?.current_risk_level ?? "Low";
  const riskScore = typeof overview?.current_risk_score === "number"
    ? `${Math.round(overview.current_risk_score * 100)}%`
    : null;
  const riskValue =
    rawRisk === "High" ? t("riskHigh") :
    rawRisk === "Medium" ? t("riskMedium") :
    rawRisk === "Critical" ? t("riskCritical") :
    t("riskLow");

  // Translate farm status value
  const rawStatus = overview?.farm_status ?? "Stable";
  const statusValue =
    rawStatus === "Critical" ? t("statusCritical") :
    rawStatus === "Warning" ? t("statusWarning") :
    t("statusStable");

  const cards = [
    { label: t("currentRisk"), value: riskScore ? `${riskValue} · ${riskScore}` : riskValue, icon: Activity, tone: "from-red-600/20 via-red-600/10 to-transparent", badge: "text-red-700 bg-red-100 dark:text-red-200 dark:bg-red-950/60" },
    { label: t("latestPrediction"), value: overview?.latest_image_prediction ?? t("noPrediction"), icon: Microscope, tone: "from-red-500/25 via-red-400/10 to-transparent", badge: "text-red-700 bg-red-100 dark:text-red-200 dark:bg-red-950/60" },
    { label: t("totalAlerts"), value: overview?.total_alerts ?? 0, icon: AlertTriangle, tone: "from-red-600/20 via-red-600/10 to-transparent", badge: "text-red-700 bg-red-100 dark:text-red-200 dark:bg-red-950/60" },
    { label: t("farmStatus"), value: statusValue, icon: ShieldCheck, tone: "from-red-600/20 via-red-500/10 to-transparent", badge: "text-red-700 bg-red-100 dark:text-red-200 dark:bg-red-950/60" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.label} className="glass soft-noise relative overflow-hidden rounded-[2rem] p-5 panel-entrance">
            <div className={`absolute inset-x-0 top-0 h-24 bg-gradient-to-br ${card.tone}`} />
            <div className="relative flex items-center justify-between">
              <p className="text-[0.72rem] uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">{card.label}</p>
              <div className={`grid h-10 w-10 place-items-center rounded-2xl ${card.badge}`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <p className="relative mt-4 font-display text-[1.55rem] leading-tight font-semibold tracking-[-0.03em] text-slate-900 dark:text-slate-50">{card.value}</p>
          </div>
        );
      })}
    </div>
  );
}
