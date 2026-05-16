"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Lock } from "lucide-react";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useLanguage } from "@/lib/language-context";
import toast from "react-hot-toast";
import { api } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export default function LoginPage() {
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post("/auth/login", { email, password });
      if (!response.data.access_token) {
        toast.error("No token received from server");
        return;
      }
      saveToken(response.data.access_token);
      toast.success("Login successful");
      router.push("/dashboard");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden px-4 py-8 md:px-6 md:py-10">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        {/* Left Section - Chicken & Info */}
        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="hidden lg:flex flex-col items-center justify-center"
        >
          {/* Chicken SVG */}
          <div className="mb-8 flex flex-col items-center">
            <div className="relative w-56 h-56 mb-6">
              <svg 
                viewBox="0 0 300 300" 
                className="w-full h-full drop-shadow-xl"
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style={{stopColor:"#FCD34D", stopOpacity:0.3}} />
                    <stop offset="100%" style={{stopColor:"#F59E0B", stopOpacity:0}} />
                  </radialGradient>
                  <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor:"#DC2626"}} />
                    <stop offset="100%" style={{stopColor:"#991B1B"}} />
                  </linearGradient>
                  <linearGradient id="wingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{stopColor:"#EF4444"}} />
                    <stop offset="100%" style={{stopColor:"#B91C1C"}} />
                  </linearGradient>
                </defs>
                
                <circle cx="150" cy="150" r="140" fill="url(#glow)"/>
                <ellipse cx="150" cy="160" rx="55" ry="70" fill="url(#bodyGrad)"/>
                <circle cx="150" cy="75" r="28" fill="#EF4444"/>
                <circle cx="157" cy="72" r="4" fill="#FCD34D"/>
                <circle cx="158" cy="71" r="2" fill="#000"/>
                <polygon points="170,77 185,75 170,82" fill="#FCD34D"/>
                <path d="M 145 50 Q 140 35 150 30 Q 160 35 155 50" fill="#DC2626"/>
                <path d="M 155 50 Q 160 38 170 35 Q 175 42 170 52" fill="#DC2626"/>
                <ellipse cx="145" cy="90" rx="6" ry="10" fill="#DC2626"/>
                <ellipse cx="110" cy="150" rx="25" ry="45" fill="url(#wingGrad)" transform="rotate(-25 110 150)"/>
                <path d="M 190 130 Q 220 100 230 70" stroke="#991B1B" strokeWidth="12" fill="none" strokeLinecap="round"/>
                <path d="M 190 135 Q 225 110 245 85" stroke="#B91C1C" strokeWidth="10" fill="none" strokeLinecap="round"/>
                <path d="M 190 140 Q 220 125 235 110" stroke="#DC2626" strokeWidth="10" fill="none" strokeLinecap="round"/>
                <line x1="135" y1="225" x2="135" y2="265" stroke="#FCD34D" strokeWidth="4" strokeLinecap="round"/>
                <line x1="165" y1="225" x2="165" y2="265" stroke="#FCD34D" strokeWidth="4" strokeLinecap="round"/>
                <line x1="135" y1="265" x2="120" y2="275" stroke="#FCD34D" strokeWidth="3" strokeLinecap="round"/>
                <line x1="135" y1="265" x2="150" y2="275" stroke="#FCD34D" strokeWidth="3" strokeLinecap="round"/>
                <line x1="165" y1="265" x2="150" y2="275" stroke="#FCD34D" strokeWidth="3" strokeLinecap="round"/>
                <line x1="165" y1="265" x2="180" y2="275" stroke="#FCD34D" strokeWidth="3" strokeLinecap="round"/>
              </svg>
            </div>

            <h1 className="font-display text-5xl font-bold text-center tracking-[-0.05em] text-red-900 mb-2">
              PoultryGuard AI
            </h1>
            <p className="text-xl font-semibold text-red-700 mb-2">Smart Poultry Disease Detection</p>
            <p className="text-sm text-red-600 text-center max-w-xs">AI-powered monitoring for healthier flocks</p>
          </div>

          {/* Info Cards */}
          <div className="glass soft-noise rounded-[2.25rem] p-8 xl:p-10 overflow-hidden w-full">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-xs font-bold uppercase tracking-widest text-red-700 dark:bg-red-900/70">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a1 1 0 011 1v1.323l3.954 1.115a1 1 0 11-.547 1.929L11 5.823v5.354l3.954 1.116a1 1 0 11-.547 1.929L11 12.677v2a1 1 0 11-2 0v-2.323L5.046 14.68a1 1 0 11.547-1.929L9 12.677V7.323L5.046 6.207a1 1 0 11.547-1.929L9 5.323V3a1 1 0 011-1h1zm-6 8a1 1 0 10-2 0 1 1 0 002 0zm12 0a1 1 0 10-2 0 1 1 0 002 0z" />
              </svg>
              Farm Guardian
            </div>

            <h2 className="font-display text-3xl font-bold leading-tight tracking-tight text-red-900 mb-4">
              Monitor Your Flock with Intelligence
            </h2>
            <p className="text-base leading-7 text-red-800 mb-8">
              Real-time disease detection, risk assessment, and early alerts to keep your poultry healthy and productive.
            </p>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { icon: "🔍", title: "AI Detection", desc: "Instant diagnosis from images" },
                { icon: "⚠️", title: "Early Alerts", desc: "Catch issues before escalation" },
                { icon: "🗣️", title: "Voice Support", desc: "English, Hindi & Telugu" },
              ].map((item) => (
                <div
                  key={item.title}
                  className="rounded-[1.2rem] border border-red-200/70 bg-gradient-to-br from-red-50 to-red-100 p-4 shadow-sm dark:border-red-700 dark:bg-red-900/30"
                >
                  <p className="text-2xl mb-1">{item.icon}</p>
                  <p className="text-sm font-bold text-red-900">{item.title}</p>
                  <p className="mt-1 text-xs leading-5 text-red-700 dark:text-red-100">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Right Section - Login Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="glass soft-noise mx-auto w-full max-w-lg rounded-[2.25rem] p-5 md:p-8 panel-entrance"
        >
          <div className="mb-8 flex items-start justify-between gap-4">
            <div>
              <p className="text-[0.72rem] font-bold uppercase tracking-widest text-red-700 dark:text-red-400">
                {t("authLanguageLabel")}
              </p>
              <h2 className="font-display mt-4 text-4xl font-bold tracking-tight text-red-900 dark:text-red-50">
                {t("loginTitle")}
              </h2>
              <p className="mt-3 max-w-sm text-sm leading-6 text-red-800 dark:text-red-200">{t("loginSubtitle")}</p>
            </div>
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[1.4rem] bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v4h8v-4zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
            </div>
          </div>

          <div className="mb-6 w-44">
            <LanguageSwitcher />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-semibold text-red-900 dark:text-red-200">{t("email")}</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-red-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-[1.15rem] border border-red-200/80 dark:border-red-700 bg-white/80 dark:bg-red-900/70 py-3.5 pl-11 pr-4 text-sm shadow-sm outline-none transition focus:-translate-y-0.5 focus:border-red-500/40 focus:ring-2 focus:ring-red-500/20"
                  placeholder="farmer@example.com"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-red-900 dark:text-red-200">{t("password")}</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-red-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-[1.15rem] border border-red-200/80 dark:border-red-700 bg-white/80 dark:bg-red-900/70 py-3.5 pl-11 pr-4 text-sm shadow-sm outline-none transition focus:-translate-y-0.5 focus:border-red-500/40 focus:ring-2 focus:ring-red-500/20"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-[1.15rem] bg-gradient-to-r from-red-600 to-red-700 px-4 py-3.5 text-sm font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:from-red-700 hover:to-red-800 disabled:opacity-50"
            >
              {loading ? t("signingIn") : t("signIn")}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-red-800 dark:text-red-300">
            {t("noAccount")} {" "}
            <Link href="/register" className="font-bold text-red-700 hover:text-red-600 hover:underline dark:text-red-400">
              {t("register")}
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
