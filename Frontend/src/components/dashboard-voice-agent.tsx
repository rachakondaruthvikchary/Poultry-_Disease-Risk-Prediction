"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useLanguage } from "@/lib/language-context";
import { VoiceAgent } from "@/components/voice-agent";

interface OverviewState {
  risk: string;
  disease: string;
  alertCount: number;
  status: string;
}

const DEFAULT_OVERVIEW: OverviewState = {
  risk: "Low",
  disease: "",
  alertCount: 0,
  status: "Stable",
};

export function DashboardVoiceAgent() {
  const { t } = useLanguage();
  const [overview, setOverview] = useState<OverviewState>(DEFAULT_OVERVIEW);

  useEffect(() => {
    let cancelled = false;

    const loadVoiceData = async () => {
      try {
        const farmsRes = await api.get("/farms");
        const farmId = farmsRes.data?.[0]?.id;
        if (!farmId) {
          if (!cancelled) {
            setOverview((current) => ({
              ...current,
              disease: t("noPrediction"),
            }));
          }
          return;
        }

        const [dashboardRes, alertsRes] = await Promise.all([
          api.get(`/dashboard/${farmId}`, {
            params: { _ts: Date.now() },
            headers: { "Cache-Control": "no-cache" },
          }),
          api.get(`/alerts/${farmId}`),
        ]);

        if (cancelled) {
          return;
        }

        setOverview({
          risk: dashboardRes.data?.overview?.current_risk_level ?? "Low",
          disease: dashboardRes.data?.overview?.latest_image_prediction ?? t("noPrediction"),
          alertCount: alertsRes.data?.length ?? dashboardRes.data?.overview?.total_alerts ?? 0,
          status: dashboardRes.data?.overview?.farm_status ?? "Stable",
        });
      } catch {
        if (!cancelled) {
          setOverview((current) => ({
            ...current,
            disease: current.disease || t("noPrediction"),
          }));
        }
      }
    };

    void loadVoiceData();
    const interval = window.setInterval(() => {
      void loadVoiceData();
    }, 15000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [t]);

  return (
    <VoiceAgent
      risk={overview.risk}
      disease={overview.disease || t("noPrediction")}
      alertCount={overview.alertCount}
      status={overview.status}
    />
  );
}