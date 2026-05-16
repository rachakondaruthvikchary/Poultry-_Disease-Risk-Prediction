"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { OverviewCards } from "@/components/overview-cards";
import { RiskTrendChart } from "@/components/risk-trend-chart";
import { AlertPanel } from "@/components/alert-panel";
import { QuickUpload } from "@/components/quick-upload";
import { LanguageVoicePanel } from "@/components/language-voice-panel";
import { DiseaseReferenceGallery } from "@/components/disease-reference-gallery";
import { api } from "@/lib/api";
import { useLanguage } from "@/lib/language-context";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const { t } = useLanguage();
  const [farmId, setFarmId] = useState<number | null>(null);
  const [overview, setOverview] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loadingDashboard, setLoadingDashboard] = useState(true);

  const loadDashboardData = useCallback(async (id: number) => {
    try {
      const dashRes = await api.get(`/dashboard/${id}`, {
        params: { _ts: Date.now() },
        headers: { "Cache-Control": "no-cache" },
      });
      setOverview(dashRes.data.overview);
      setTrend(dashRes.data.trend || []);
      setLoadingDashboard(false);

      // Load alerts asynchronously so the dashboard becomes usable faster.
      void api.get(`/alerts/${id}`)
        .then((alertsRes) => {
          setAlerts(alertsRes.data.slice(0, 5));
        })
        .catch((error) => {
          console.error("Failed to load alerts", error);
        });
    } catch (error) {
      console.error("Failed to load dashboard", error);
      setLoadingDashboard(false);
    }
  }, []);

  const loadFarmAndDashboard = useCallback(async () => {
    try {
      const farmsRes = await api.get("/farms");
      if (farmsRes.data.length === 0) {
        const newFarm = await api.post("/farms", {
          name: "My Farm",
          location: "Default Location",
          flock_size: 1000,
        });
        setFarmId(newFarm.data.id);
        void loadDashboardData(newFarm.data.id);
      } else {
        setFarmId(farmsRes.data[0].id);
        void loadDashboardData(farmsRes.data[0].id);
      }
    } catch (error) {
      console.error("Failed to load farm", error);
      setLoadingDashboard(false);
    }
  }, [loadDashboardData]);

  useEffect(() => {
    loadFarmAndDashboard();
  }, [loadFarmAndDashboard]);

  useEffect(() => {
    if (!farmId) return;
    const interval = setInterval(() => {
      loadDashboardData(farmId);
    }, 15000);

    return () => clearInterval(interval);
  }, [farmId, loadDashboardData]);

  const handleQuickUpload = async (file: File) => {
    if (!farmId) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post(`/predictions/${farmId}/image`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await loadDashboardData(farmId);
      toast.success(`Prediction: ${response.data?.disease_name || "Completed"}`);
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Upload failed");
    }
  };

  return (
    <DashboardShell>
      {loadingDashboard && (
        <div className="glass soft-noise rounded-[2rem] p-5 text-sm text-red-800 dark:text-red-200">
          Loading your farm data…
        </div>
      )}
      <OverviewCards overview={overview} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RiskTrendChart data={trend} />
        <AlertPanel alerts={alerts} />
      </div>

      {/* ── Language & Voice Assistant Section ── */}
      <LanguageVoicePanel
        risk={overview?.current_risk_level ?? "Low"}
        disease={overview?.latest_image_prediction ?? t("noPrediction")}
        alertCount={overview?.total_alerts ?? 0}
        status={overview?.farm_status ?? "Stable"}
      />

      <QuickUpload onPick={handleQuickUpload} />

      {/* ── Disease Reference Gallery ── */}
      <DiseaseReferenceGallery />
    </DashboardShell>
  );
}
