"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { Download, FileText } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

export default function HistoryPage() {
  const [farmId, setFarmId] = useState<number | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const loadFarm = useCallback(async () => {
    try {
      const res = await api.get("/farms");
      if (res.data.length > 0) {
        setFarmId(res.data[0].id);
      } else {
        const created = await api.post("/farms", {
          name: "My Farm",
          location: "Default Location",
          flock_size: 100,
        });
        setFarmId(created.data.id);
      }
    } catch (error) {
      console.error("Failed to load farm", error);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    if (!farmId) return;
    try {
      const res = await api.get(`/history/${farmId}`, { params: { page, page_size: pageSize } });
      setAlerts(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (error) {
      console.error("Failed to load history", error);
    }
  }, [farmId, page]);

  useEffect(() => {
    loadFarm();
  }, [loadFarm]);

  useEffect(() => {
    if (farmId) loadHistory();
  }, [farmId, loadHistory]);

  const downloadCSV = async () => {
    if (!farmId) return;
    try {
      const res = await api.get(`/history/${farmId}/export/csv`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
      const link = document.createElement("a");
      link.href = url;
      const filename = `alert-history-${new Date().toISOString().split('T')[0]}.csv`;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("CSV downloaded successfully!");
    } catch (error) {
      console.error("CSV export error:", error);
      toast.error("Failed to export CSV. Please try again.");
    }
  };

  const downloadPDF = async () => {
    if (!farmId) return;
    try {
      const res = await api.get(`/history/${farmId}/export/pdf`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement("a");
      link.href = url;
      const filename = `alert-history-report-${new Date().toISOString().split('T')[0]}.pdf`;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("PDF downloaded successfully!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF. Please try again.");
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <DashboardShell>
      <div className="glass rounded-3xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Alert History</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Total: {total} alerts · Export your data below
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={downloadCSV}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-sm transition-colors"
              title="Download as spreadsheet"
            >
              <Download className="h-4 w-4" />
              Download CSV
            </button>
            <button
              onClick={downloadPDF}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-sm transition-colors"
              title="Download as PDF report"
            >
              <FileText className="h-4 w-4" />
              Download PDF
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-medium">Title</th>
                <th className="text-left py-3 px-4 text-sm font-medium">Severity</th>
                <th className="text-left py-3 px-4 text-sm font-medium">Source</th>
                <th className="text-left py-3 px-4 text-sm font-medium">Date</th>
                <th className="text-left py-3 px-4 text-sm font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id} className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900/50">
                  <td className="py-3 px-4 text-sm">{alert.title}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        alert.severity === "High"
                          ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-300"
                          : "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-300"
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm">{alert.source}</td>
                  <td className="py-3 px-4 text-sm">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4 text-sm">
                    {alert.is_read ? "Seen" : "Seen"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-50 text-sm"
            >
              Previous
            </button>
            <span className="text-sm">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-50 text-sm"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
