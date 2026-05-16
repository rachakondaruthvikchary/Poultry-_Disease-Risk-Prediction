"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Lock, User } from "lucide-react";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useLanguage } from "@/lib/language-context";
import toast from "react-hot-toast";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const { t } = useLanguage();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      await api.post("/auth/register", {
        full_name: fullName,
        email,
        password,
      });
      toast.success("Account created");
      router.push("/login");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden px-4 py-8 md:px-6 md:py-10">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-6 lg:grid-cols-[0.95fr_1.05fr]">
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
                {t("registerTitle")}
              </h2>
              <p className="mt-3 max-w-sm text-sm leading-6 text-red-800 dark:text-red-200">{t("registerSubtitle")}</p>
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
              <label htmlFor="register-fullName" className="mb-2 block text-sm font-semibold text-red-900 dark:text-red-200">{t("fullName")}</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-red-500" />
                <input
                  id="register-fullName"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-[1.15rem] border border-red-200/80 dark:border-red-700 bg-white/80 dark:bg-red-900/70 py-3.5 pl-11 pr-4 text-sm shadow-sm outline-none transition focus:-translate-y-0.5 focus:border-red-500/40 focus:ring-2 focus:ring-red-500/20"
                  placeholder="John Doe"
                />
              </div>
            </div>

            <div>
              <label htmlFor="register-email" className="mb-2 block text-sm font-semibold text-red-900 dark:text-red-200">{t("email")}</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-red-500" />
                <input
                  id="register-email"
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
              <label htmlFor="register-password" className="mb-2 block text-sm font-semibold text-red-900 dark:text-red-200">{t("password")}</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-red-500" />
                <input
                  id="register-password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-[1.15rem] border border-red-200/80 dark:border-red-700 bg-white/80 dark:bg-red-900/70 py-3.5 pl-11 pr-4 text-sm shadow-sm outline-none transition focus:-translate-y-0.5 focus:border-red-500/40 focus:ring-2 focus:ring-red-500/20"
                  placeholder="••••••••"
                />
              </div>
              <p className="mt-2 text-xs uppercase tracking-[0.18em] text-red-700">{t("passwordHint")}</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-[1.15rem] bg-gradient-to-r from-red-600 to-red-700 px-4 py-3.5 text-sm font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:from-red-700 hover:to-red-800 disabled:opacity-50"
            >
              {loading ? t("creatingAccount") : t("createAccount")}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-red-800 dark:text-red-300">
            {t("haveAccount")} {" "}
            <Link href="/login" className="font-bold text-red-700 hover:text-red-600 hover:underline dark:text-red-400">
              {t("signIn")}
            </Link>
          </p>
        </motion.div>

        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="hidden lg:block"
        >
          <div className="glass soft-noise rounded-[2.25rem] p-8 xl:p-10 overflow-hidden">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-xs font-bold uppercase tracking-widest text-red-700 dark:bg-red-900/70">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a1 1 0 011 1v1.323l3.954 1.115a1 1 0 11-.547 1.929L11 5.823v5.354l3.954 1.116a1 1 0 11-.547 1.929L11 12.677v2a1 1 0 11-2 0v-2.323L5.046 14.68a1 1 0 11.547-1.929L9 12.677V7.323L5.046 6.207a1 1 0 11.547-1.929L9 5.323V3a1 1 0 011-1h1zm-6 8a1 1 0 10-2 0 1 1 0 002 0zm12 0a1 1 0 10-2 0 1 1 0 002 0z" />
              </svg>
              Farm Health & Safety
            </div>
            <h1 className="font-display max-w-xl text-5xl font-bold leading-tight tracking-tight text-red-900 dark:text-red-50">
              Join thousands of poultry farmers protecting their flocks.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-red-800 dark:text-red-200">
              Get instant access to AI-powered disease detection, risk assessment, real-time alerts, and multilingual support in English, Hindi, and Telugu.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-2">
              {[
                ["AI-Powered Detection", "Instant disease diagnosis from bird images with high accuracy."],
                ["Multilingual Voice", "Get guidance in English, Hindi, or Telugu on any device."],
                ["Visual Disease Review", "Upload photos instantly and see predictions in real-time."],
                ["Smart Alerts", "Receive early warnings before diseases spread in your flock."],
              ].map(([title, body], index) => (
                <div
                  key={title}
                  className="rounded-[1.6rem] border border-red-200/70 bg-gradient-to-br from-red-50 to-red-100 p-4 shadow-sm dark:border-red-700 dark:bg-red-900/30"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <p className="text-[0.72rem] font-bold uppercase tracking-widest text-red-900">{title}</p>
                  <p className="mt-3 text-sm leading-6 text-red-800 dark:text-red-100">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
