"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { User, Clipboard, Database } from "lucide-react";

export default function FarmDataPage() {
  const [farmId, setFarmId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [farmSaving, setFarmSaving] = useState(false);
  const [records, setRecords] = useState<any[]>([]);
  const [farmType, setFarmType] = useState("Broiler");

  // ── Farmer & Farm Info ──────────────────────────────────────────────────
  const [farmerInfo, setFarmerInfo] = useState({
    full_name: "",
    email: "",
    contact: "",
    address: "",
  });
  const [farmInfo, setFarmInfo] = useState({
    name: "",
    location: "",
    flock_size: 100,
  });

  // ── Daily Health Check ──────────────────────────────────────────────────
  const [formData, setFormData] = useState({
    record_date: new Date().toISOString().split("T")[0],
    temperature: 25,
    humidity: 60,
    feed_intake: 120,
    water_intake: 180,
    activity_level: 75,
    mortality_rate: 1,
    bird_age: 28,
  });

  const loadRecords = useCallback(async (id: number) => {
    try {
      const res = await api.get(`/records/${id}`);
      setRecords(res.data || []);
    } catch {
      // silent
    }
  }, []);

  const loadAll = useCallback(async () => {
    try {
      const meRes = await api.get("/auth/me");
      setFarmerInfo((prev) => ({
        ...prev,
        full_name: meRes.data.full_name || "",
        email: meRes.data.email || "",
        contact: localStorage.getItem("farmer_contact") || "",
        address: localStorage.getItem("farmer_address") || "",
      }));
      setFarmType(localStorage.getItem("farm_type") || "Broiler");

      const farmsRes = await api.get("/farms");
      let farm;
      if (farmsRes.data.length > 0) {
        farm = farmsRes.data[0];
      } else {
        const created = await api.post("/farms", {
          name: "My Farm",
          location: "Default Location",
          flock_size: 100,
        });
        farm = created.data;
      }
      setFarmId(farm.id);
      setFarmInfo({ name: farm.name, location: farm.location, flock_size: farm.flock_size });
      await loadRecords(farm.id);
    } catch (error) {
      console.error("Failed to load data", error);
    }
  }, [loadRecords]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleFarmSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!farmId) return;
    // Save contact & address to localStorage
    localStorage.setItem("farmer_contact", farmerInfo.contact);
    localStorage.setItem("farmer_address", farmerInfo.address);
    localStorage.setItem("farm_type", farmType);
    setFarmSaving(true);
    try {
      await api.put(`/farms/${farmId}`, farmInfo);
      toast.success("Farmer & farm information saved.");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Could not save farm info");
    } finally {
      setFarmSaving(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!farmId) {
      toast.error("No farm found");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post("/records", { ...formData, farm_id: farmId });
      const { risk_score, risk_category } = response.data;
      const riskPercent = `${Math.round(risk_score * 100)}%`;
      if (risk_category === "High") {
        toast.error(`⚠️ Health risk is HIGH (${riskPercent}) — take immediate action!`);
      } else if (risk_category === "Critical") {
        toast.error(`🚨 Health risk is CRITICAL (${riskPercent}) — immediate intervention required!`);
      } else if (risk_category === "Medium") {
        toast(`🟡 Health risk is MEDIUM (${riskPercent}) — monitor closely.`, { icon: "⚠️" });
      } else {
        toast.success(`✅ Health risk is LOW (${riskPercent}) — flock looks healthy!`);
      }
      loadRecords(farmId);
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Could not save data");
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary outline-none";

  return (
    <DashboardShell>
      <div className="space-y-6">

        {/* ── Section 1: Farmer & Farm Information ────────────────────── */}
        <div className="glass rounded-3xl p-6">
          <div className="flex items-center gap-2 mb-1">
            <User className="w-5 h-5 text-red-600 dark:text-red-400" />
            <h2 className="text-xl font-bold text-red-900 dark:text-red-50">Farmer & Farm Information</h2>
          </div>
          <p className="text-sm text-red-700 dark:text-red-300 mb-6">
            Your personal details and farm profile. Update anytime.
          </p>

          <form onSubmit={handleFarmSave} className="space-y-6">
            {/* Farmer details */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-bold uppercase tracking-widest text-red-700 dark:text-red-400">Farmer Details</span>
                <div className="flex-1 h-px bg-slate-200 dark:bg-slate-700" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    value={farmerInfo.full_name}
                    readOnly
                    className={`${inputClass} opacity-60 cursor-not-allowed`}
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">From your account profile.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email Address</label>
                  <input
                    type="email"
                    value={farmerInfo.email}
                    readOnly
                    className={`${inputClass} opacity-60 cursor-not-allowed`}
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Your registered email.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Contact Number</label>
                  <input
                    type="tel"
                    placeholder="e.g. +92 300 1234567"
                    value={farmerInfo.contact}
                    onChange={(e) => setFarmerInfo((p) => ({ ...p, contact: e.target.value }))}
                    className={inputClass}
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Phone number for alerts.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Home Address</label>
                  <input
                    type="text"
                    placeholder="e.g. Village Ravi, Punjab"
                    value={farmerInfo.address}
                    onChange={(e) => setFarmerInfo((p) => ({ ...p, address: e.target.value }))}
                    className={inputClass}
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Your residential address.</p>
                </div>
              </div>
            </div>

            {/* Simple farm details */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-bold uppercase tracking-widest text-red-700 dark:text-red-400">Simple Farm Details</span>
                <div className="flex-1 h-px bg-slate-200 dark:bg-slate-700" />
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
                Keep these details short and easy to understand.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Farm Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Green Valley Farm"
                    value={farmInfo.name}
                    onChange={(e) => setFarmInfo((p) => ({ ...p, name: e.target.value }))}
                    className={inputClass}
                    required
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Your farm&apos;s display name.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Farm Type</label>
                  <select
                    value={farmType}
                    onChange={(e) => setFarmType(e.target.value)}
                    className={inputClass}
                  >
                    <option value="Broiler">Broiler</option>
                    <option value="Layer">Layer</option>
                    <option value="Desi">Desi</option>
                    <option value="Mixed">Mixed</option>
                  </select>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Choose the main kind of birds you keep.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Total Birds</label>
                  <input
                    type="number"
                    min={1}
                    value={farmInfo.flock_size}
                    onChange={(e) => setFarmInfo((p) => ({ ...p, flock_size: parseInt(e.target.value) }))}
                    className={inputClass}
                    required
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Just the number of birds on the farm.</p>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={farmSaving}
              className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-2.5 rounded-xl font-bold shadow-lg hover:from-red-700 hover:to-red-800 transition-all disabled:opacity-50 dark:from-red-600 dark:to-red-700"
            >
              {farmSaving ? "Saving..." : "Save Farmer & Farm Info"}
            </button>
          </form>
        </div>

        {/* ── Section 2: Daily Farm Health Check ──────────────────────── */}
        <div className="glass rounded-3xl p-6">
          <div className="flex items-center gap-2 mb-1">
            <Clipboard className="w-5 h-5 text-red-600 dark:text-red-400" />
            <h2 className="text-xl font-bold text-red-900 dark:text-red-50">Daily Farm Health Check</h2>
          </div>
          <p className="text-sm text-red-700 dark:text-red-300 mb-6">
            Fill in today&apos;s farm details. We will estimate disease risk for your flock.
          </p>

          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Record Date</label>
              <input
                type="date"
                value={formData.record_date}
                onChange={(e) => setFormData((p) => ({ ...p, record_date: e.target.value }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Choose the day for this entry.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Shed Temperature (°C)</label>
              <input
                type="number"
                step="0.1"
                value={formData.temperature}
                  onChange={(e) => {
                    const val = e.target.value.trim();
                    const num = val === "" ? undefined : Number(val);
                    setFormData((p) => ({ ...p, temperature: Number.isFinite(num) ? num : p.temperature }));
                  }}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Example: 24 to 30°C.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Shed Humidity (%)</label>
              <input
                type="number"
                step="0.1"
                value={formData.humidity}
                onChange={(e) => setFormData((p) => ({ ...p, humidity: parseFloat(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Example: 50% to 70%.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Total Feed Given (kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.feed_intake}
                onChange={(e) => setFormData((p) => ({ ...p, feed_intake: parseFloat(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Total feed consumed today.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Total Water Used (L)</label>
              <input
                type="number"
                step="0.1"
                value={formData.water_intake}
                onChange={(e) => setFormData((p) => ({ ...p, water_intake: parseFloat(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Total water consumed today.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Bird Activity Level (%)</label>
              <input
                type="number"
                step="0.1"
                value={formData.activity_level}
                onChange={(e) => setFormData((p) => ({ ...p, activity_level: parseFloat(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">100% means fully active flock.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Bird Death Rate (%)</label>
              <input
                type="number"
                step="0.1"
                value={formData.mortality_rate}
                onChange={(e) => setFormData((p) => ({ ...p, mortality_rate: parseFloat(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Percentage of birds lost today.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Average Bird Age (days)</label>
              <input
                type="number"
                value={formData.bird_age}
                onChange={(e) => setFormData((p) => ({ ...p, bird_age: parseInt(e.target.value) }))}
                className={inputClass}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Age of most birds in the flock.</p>
            </div>

            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-2.5 rounded-xl font-bold shadow-lg hover:from-red-700 hover:to-red-800 transition-all disabled:opacity-50 dark:from-red-600 dark:to-red-700"
              >
                {loading ? "Checking Risk..." : "Save Data & Check Risk"}
              </button>
            </div>
          </form>
        </div>

        {/* ── Section 3: Saved Farm Data Records ──────────────────────── */}
        <div className="glass rounded-3xl p-6">
          <div className="flex items-center gap-2 mb-1">
            <Database className="w-5 h-5 text-red-600 dark:text-red-400" />
            <h2 className="text-xl font-bold text-red-900 dark:text-red-50">Saved Farm Data Records</h2>
          </div>
          <p className="text-sm text-red-700 dark:text-red-300 mb-4">
            All daily health check entries for your farm ({records.length} record{records.length !== 1 ? "s" : ""}).
          </p>

          {records.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Database className="w-10 h-10 mb-3 opacity-30" />
              <p className="text-sm">No records yet. Submit the Daily Health Check above to get started.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Date</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Temp (°C)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Humidity (%)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Feed (kg)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Water (L)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Activity (%)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Deaths (%)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Bird Age</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Risk Score (%)</th>
                    <th className="text-left py-3 px-3 font-medium text-slate-500">Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((rec, idx) => (
                    <tr
                      key={rec.id}
                      className={`border-b border-slate-100 dark:border-slate-800 ${
                        idx % 2 === 0 ? "bg-white/40 dark:bg-slate-800/20" : ""
                      }`}
                    >
                      <td className="py-2.5 px-3 font-medium">{rec.record_date}</td>
                      <td className="py-2.5 px-3">{rec.temperature}</td>
                      <td className="py-2.5 px-3">{rec.humidity}</td>
                      <td className="py-2.5 px-3">{rec.feed_intake}</td>
                      <td className="py-2.5 px-3">{rec.water_intake}</td>
                      <td className="py-2.5 px-3">{rec.activity_level}</td>
                      <td className="py-2.5 px-3">{rec.mortality_rate}</td>
                      <td className="py-2.5 px-3">{rec.bird_age}d</td>
                      <td className="py-2.5 px-3">{rec.risk_score != null ? `${(rec.risk_score * 100).toFixed(1)}%` : "-"}</td>
                      <td className="py-2.5 px-3">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          rec.risk_category === "High"
                            ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                            : rec.risk_category === "Critical"
                            ? "bg-red-200 text-red-800 dark:bg-red-950/40 dark:text-red-300"
                            : rec.risk_category === "Medium"
                            ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                            : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        }`}>
                          <span className={`w-2 h-2 rounded-full ${
                            rec.risk_category === "Critical" ? "bg-red-900" :
                            rec.risk_category === "High" ? "bg-red-500" :
                            rec.risk_category === "Medium" ? "bg-yellow-500" : "bg-green-500"
                          }`} />
                          {rec.risk_category}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </DashboardShell>
  );
}
